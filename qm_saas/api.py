from logging import Logger
import requests


class Client:

    def __init__(self, protocol: str, host: str, port: int, email: str, password: str, log: Logger):
        self.protocol = protocol
        self.host = host
        self.port = port
        self.email = email
        self.password = password
        self.log = log
        self._jwt = None
        self._login()

    def _base_url(self):
        return f"{self.protocol}://{self.host}:{self.port}/api/v2"

    def simulators_url(self, instance_id: str = None):
        if instance_id:
            return f"{self._base_url()}/simulators/{instance_id}"
        else:
            return f"{self._base_url()}/simulators"

    def sessions_url(self):
        return f"{self._base_url()}/sessions"

    @staticmethod
    def _headers_unauthenticated():
        return {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _headers_authenticated(self):
        if self._jwt is None:
            raise Exception("api client is unauthenticated")
        headers = self._headers_unauthenticated()
        headers["Authorization"] = self._jwt
        return headers

    def _login(self):
        endpoint = self.sessions_url()
        payload = {
            "email": self.email,
            "password": self.password
        }
        headers=self._headers_unauthenticated()
        response = requests.post(url=endpoint, headers=headers, json=payload)

        if response.status_code != 201:
            error = response.json().get("message", "no message provided")
            self.log.error(f"Authentication for {self.email} failed: HTTP{response.status_code} {error}")
            raise Exception(f"Authentication failed: {error}")
        self._jwt = response.json()["jwt"]

    def close_simulator(self, instance_id: str):
        endpoint = self.simulators_url(instance_id)
        headers = self._headers_authenticated()
        response = requests.delete(url=endpoint, headers=headers)

        if response.status_code != 200:
            message = response.json().get("message", "no message provided")
            self.log.error(f"HTTP {response.status_code}: {message}")
            raise Exception(f'Closing the simulator instance {instance_id} failed: {message}')

    def close_all_simulators(self):
        endpoint = self.simulators_url()
        headers = self._headers_authenticated()
        response = requests.delete(url=endpoint, headers=headers)
        if response.status_code != 200:
            message = response.json().get("message", "no message provided")
            self.log.error(f"HTTP {response.status_code}: {message}")
            raise Exception(f'Closing all simulator instances failed: {message}')

    def launch_simulator(self, version: str, cluster_config: dict) -> dict:
        endpoint = self.simulators_url()
        payload = {
            "version": version,
            "cluster_config": cluster_config if cluster_config else None
        }
        headers = self._headers_authenticated()
        response = requests.post(url=endpoint, headers=headers, json=payload)

        if response.status_code != 201:
            message = response.json().get("message", "no message provided")
            self.log.error(f"HTTP {response.status_code}: {message}")
            raise Exception(f"Could not spawn simulator of version {version}: {message}")

        return response.json()
