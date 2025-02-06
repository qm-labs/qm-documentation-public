import datetime

import deprecation
from enum import Enum
import logging
import re

from qm_saas.api import Client

_AUTHORIZATION_TOKEN_HEADER_NAME = "simulation-auth"
_AUTHORIZATION_ID_HEADER_NAME = "simulation-id"
_FEM_MIN_SLOT = 1
_FEM_MAX_SLOT = 8


class QoPVersion(Enum):
    """
    An enum containing the available Quantum Orchestration Platform (QoP) versions.
    """
    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, _: str):
        pattern = re.compile("v(\\d+)_(\\d+)_(\\d+)")
        match = pattern.match(_)
        self._major = int(match.group(1))
        self._minor = int(match.group(2))
        self._patch = int(match.group(3))

    def __str__(self):
        return "%s.%s" % (self.__class__.__name__, self._name_)

    @property
    def major(self):
        return self._major

    @property
    def minor(self):
        return self._minor

    @property
    def patch(self):
        return self._patch

    latest = "v3_2_0"
    v3_2_0 = "v3_2_0"

    v3_1_0 = "v3_1_0"
    v2_4_0 = "v2_4_0"
    v2_2_2 = "v2_2_2"
    v2_2_0 = "v2_2_0"
    v2_1_3 = "v2_1_3"


class FemType(Enum):
    """
    An enum containing the available Front-End Module (FEM) types.
    """
    MW_FEM = "MW_FEM"
    LF_FEM = "LF_FEM"


class ControllerConfig:
    """
    A configuration of a controller and its FEMs in the cluster.
    """
    def __init__(self):
        self._slots = dict()

    def lf_fems(self, *slots: int):
        """
        Add LF FEMs to numbered slots in the cluster configuration.

        Args:
            *slots: The slots for the LF FEMs.
        """
        for slot in slots:
            self._add_slot(slot, FemType.LF_FEM)
        return self

    def mw_fems(self, *slots: int):
        """
        Add MW FEMs to numbered slots in the cluster configuration.

        Args:
            *slots: The slots for the MW FEMs.
        """
        for slot in slots:
            self._add_slot(slot, FemType.MW_FEM)
        return self

    def _add_slot(self, slot: int, fem_type: FemType):
        key = f"{slot}"
        if key in self._slots.keys():
            raise ValueError(f"Slot number {key} is already configured as {self._slots[key]}")

        if _FEM_MIN_SLOT <= slot <= _FEM_MAX_SLOT:
            self._slots[key] = fem_type.value
        else:
            raise ValueError(f"Invalid slot number {key}, must be [{_FEM_MIN_SLOT}, {_FEM_MAX_SLOT}]")

    @property
    def slots(self) -> dict:
        """
        Get the slots' FEM configuration.

        Returns: 
            A dictionary of the slots and their FEM types.
        """
        return self._slots


class ClusterConfig:
    """
    A configuration of the cluster and its controllers.
    """
    def __init__(self):
        self._controllers = dict()

    def controller(self) -> ControllerConfig:
        """
        Add a controller to the cluster configuration.

        Returns: 
            The controller configuration.
        """
        if len(self._controllers) != 0:
            raise ValueError("Only one controller is supported")
        con = f"con{len(self._controllers) + 1}"

        pattern = re.compile("^con(\\d+)$")
        match = pattern.fullmatch(con)
        if match is None:
            raise ValueError(f"Invalid controller name {con}; expecting 'con\\d+'")

        return self._controller(con)

    def _controller(self, con: str) -> ControllerConfig:
        if con in self._controllers.keys():
            raise ValueError(f"Controller {con} already exists")
        controller_config = ControllerConfig()
        self._controllers[con] = controller_config
        return controller_config

    @property
    def controllers(self) -> dict:
        """
        Get the controllers' configuration.

        Returns: 
            A dictionary of the controllers and their configuration.
        """
        return self._controllers

    def to_dict(self) -> dict:
        """
        Convert the cluster configuration to a dictionary.

        Returns: 
            A dictionary of the cluster controllers and their FEM.
        """
        return {
            "controllers": {k: {"slots": v.slots} for k, v in self._controllers.items()}
        }


class QmSaasInstance:
    """
    A simulator instance on the cloud platform.
    """

    def __init__(self, client: Client, version: QoPVersion, cluster_config=None, auto_cleanup: bool = True, log: logging.Logger = None):
        """
        Create a simulator instance on the cloud platform.

        Args:
            client: The client to use for the simulator instance
            version: The QoP version to use for the simulator instance
            cluster_config: The cluster configuration for the simulator instance for QoP v3.x.x
            auto_cleanup: If true (default), automatically delete the simulator instance when the context manager exits
                          otherwise it will be left running until it timeouts or is manually closed.
            log: The logger to use for logging messages. If not provided, a default logger will be used.
        """
        self._client = client
        self._version = version
        self._cluster_config = cluster_config
        self._spawned = False
        self._auto_cleanup = auto_cleanup
        self._port = None
        self._host = None
        self._expires_at = None
        self._id = None
        self._token = None
        self._log = log or logging.getLogger(__name__)

    def __enter__(self):
        self.spawn()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if not self._auto_cleanup:
            self._log.debug("Skipping close as auto_cleanup is disabled")
            return
        self.close()

    def spawn(self):
        """
        Spawns the simulator instance on the QmSaaS platform.
        This is a blocking operation.

        The simulator is spawned only once, subsequent calls to this method will not spawn a new simulator, unless the current one is closed.
        """
        if not self._spawned:
            self._create_simulator(self._version, self._cluster_config)
            self._spawned = True

    def close(self):
        """
        Closes the remote simulator and the session.
        This operation is idempotent and can be called multiple times.
        """
        if not self._spawned:
            self._log.debug("Simulator was not spawned, nothing to close")
            return

        self._log.debug(f"Closing simulator with ID {self._id}")
        self._client.close_simulator(self._id)

        self._log.info("Simulator closed successfully")
        self._spawned = False
        self._host = None
        self._port = None
        self._expires_at = None
        self._id = None
        self._token = None

    def _create_simulator(self, version: QoPVersion, cluster_config=None):
        if version is None:
            raise ValueError("Version must be provided")

        self._log.debug(f"Creating simulator with version {self._version}")
        response = self._client.launch_simulator(version.value, cluster_config.to_dict() if cluster_config else {})

        self._id = response["id"]
        self._token = response["token"]
        self._host = response["host"]
        self._port = response["port"]
        self._expires_at = datetime.datetime.fromisoformat(response["expires_at"]).replace(tzinfo=datetime.timezone.utc)
        self._log.info(f"Simulator created with id {self._id} at {self._host}:{self._port}")

    @property
    @deprecation.deprecated(details="Will be remove in the next version.")
    def qm_manager_parameters(self):
        if not self._spawned:
            raise ValueError("Simulator is not spawned")
        return dict(host=self._host, port=self._port, sim_id=self._id, sim_token=self._token)

    @property
    def default_connection_headers(self):
        return {
            _AUTHORIZATION_ID_HEADER_NAME: self._id,
            _AUTHORIZATION_TOKEN_HEADER_NAME: self._token
        }

    @property
    @deprecation.deprecated(details="Use 'token' instead")
    def sim_token(self):
        return self._token

    @property
    @deprecation.deprecated(details="Use 'id' instead")
    def sim_id(self):
        return self._id

    @property
    @deprecation.deprecated(details="Use 'host' instead")
    def sim_host(self):
        return self._host

    @property
    @deprecation.deprecated(details="Use 'port' instead")
    def sim_port(self):
        return self._port

    @property
    def host(self) -> str:
        """
        Get the host of the simulator instance.

        Returns: 
            The host of the simulator instance.
        """
        return self._host

    @property
    def port(self) -> int:
        """
        Get the port of the host of the simulator instance.

        Returns: 
            port of the host of the simulator instance.
        """
        return self._port

    @property
    def id(self) -> str:
        """
        Get the ID of the simulator instance.

        Returns: 
            The ID of the simulator instance.
        """
        return self._id

    @property
    def token(self) -> str:
        """
        Get the token of the simulator instance.

        Returns: 
            The token of the simulator instance.
        """
        return self._token

    @property
    def expires_at(self) -> datetime.datetime:
        """
        Get the expiration time of the simulator instance.

        Returns: 
            The expiration time of the simulator instance.
        """
        return self._expires_at

    @property
    def is_alive(self) -> bool:
        """
        Check if the simulator instance is alive.

        Returns: 
            True if the simulator instance is alive, False otherwise.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        if self._expires_at is None:
            return False
        else:
            return now < self._expires_at

    @property
    def is_spawned(self) -> bool:
        """
        Check if the simulator instance is spawned.

        Returns: 
            True if the simulator instance is spawned, False otherwise.
        """
        return self._spawned

    @property
    def cluster_config(self):
        """
        Get the cluster configuration.

        Returns: 
            The cluster configuration.
        """
        return self._cluster_config.controllers if self._cluster_config else None


@deprecation.deprecated(details="Use qm_saas.QmSaasInstance instead")
class QoPSaaSInstance(QmSaasInstance):
    def __init__(self, client: Client, version: QoPVersion, cluster_config=None, auto_cleanup: bool = True, log: logging.Logger = None):
        super().__init__(client, version, cluster_config, auto_cleanup, log)


class QmSaas:
    """
    A simulator client for QmSaas - The Quantum Orchestration Platform (QoP) on the cloud.
    """

    def __init__(
        self,
        host: str = "qm-saas.quantum-machines.co",
        port: int = 443,
        email: str = None,
        password: str = None,
        auto_cleanup: bool = True,
        log: logging.Logger = None,
    ):
        """
        Create a QmSaas client.

        Args:
            host: The host of the endpoint of the cloud platform api
            port: The port of the endpoint of the cloud platform api
            email: The user's email
            password: The user's password
            auto_cleanup: If true (default), automatically delete the simulator instance when the context manager exits
                          otherwise it will be left running until it timeouts or is manually closed.
            log: The logger to use for logging messages. If not provided, a default logger will be used.
        """
        self.log = log or logging.getLogger(__name__)
        self.auto_cleanup = auto_cleanup
        self._client = Client(
            protocol="https",
            host=host,
            port=port,
            email=email,
            password=password,
            log=self.log
        )

    def simulator(self, version: QoPVersion = QoPVersion.latest, cluster_config=None) -> QmSaasInstance:
        """
        Create a simulator instance on the cloud platform.

        Args:
            version: The QoP version to use for the simulator instance. Defaults to the latest version
            cluster_config: The cluster configuration for the simulator instance for QoP v3.x.x
        """
        if cluster_config is not None and version.major != 3:
            raise ValueError("Cluster configuration is only supported for QoP v3.x.x")

        return QmSaasInstance(
            client=self._client,
            version=version,
            cluster_config=cluster_config,
            auto_cleanup=self.auto_cleanup,
            log=self.log,
        )

    def close_all(self):
        """
        Close all the simulator instances created by this client
        """
        self._client.close_all_simulators()

    @property
    def port(self):
        """
        Get the port of the endpoint of the cloud platform api

        Returns: 
            The port of the endpoint of the cloud platform api
        """
        return self._client.port

    @property
    def host(self):
        """
        Get the host of the endpoint of the cloud platform api

        Returns: 
            The host of the endpoint of the cloud platform api
        """
        return self._client.host


@deprecation.deprecated(details="Use qm_saas.QmSaas instead")
class QoPSaaS(QmSaas):
    def __init__(
        self,
        host: str = "qm-saas.quantum-machines.co",
        port: int = 443,
        email: str = None,
        password: str = None,
        auto_cleanup: bool = True,
        log: logging.Logger = None,
    ):
        super().__init__(host, port, email, password, auto_cleanup, log)
