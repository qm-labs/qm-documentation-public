# Simulator Access through Cloud Service

QM can provide access to the QOP simulator in a cloud environment. This product is called QM Simulator as a Service
(QM SaaS). The service is available to customers on request to QM and can be used independently of the OPX hardware.

SaaS gives the user access to the [QOP simulator](simulator.md),
which is a software simulator that emulates the output samples of the OPX hardware. This is particularly useful for
development of QUA programs, exploration of OPX features or for integration of testing into CI workflows, all while
not requiring access to the hardware.

!!! Note
    Using the cloud simulator requires an active internet connection and an access token provided by QM.
    It also requires ports 443 and 9510 to be open for outgoing connections.

### Installation and Initialization

To use the simulator, you need to have the `qm-saas` client python package in your python environment
(alongside [qm-qua](../Releases/qm_qua_releases.md)
and an access token to a cloud service provided by QM.
The client package is [available on PyPi](https://pypi.org/project/qm-saas/) and can simply be installed via
pip or any other package manager with access to the PyPi repository.

```bash
pip install qm-saas
```

The client package provides a client class `QmSaas` that allows you to interact with the simulator service.
This client class provides methods to open and close simulator instances. On construction, it needs to be provided with
the user email and password, provided by QM.

```python
from qm_saas import QmSaas

client = QmSaas(email="jondoe@gmail.com", password="password_from_qm")
```

### The Simulator Instance

The created client object allows to spawn simulator instances and use them to simulate QUA programs as you would on real OPX hardware.
Spawning an instance creates a virtual OPX device in the cloud that can be used to simulate QUA programs. The number of instances is limited, and they have a limited lifetime.
Once an instance is spawned, it provides connection details for the `QuantumMachinesManager` object, which direct the QUA program to the cloud simulator. 
The instance is created with the latest available QOP version but can be called with a specific version. Check the `QoPVersion` enum for a list of supported versions.

```python
from qm_saas import client
from qm import QuantumMachinesManager

with client.simulator() as instance:
    # Use the instance object to simulate QUA programs
    qmm = QuantumMachinesManager(host=instance.host,
                                 port=instance.port,
                                 connection_headers=instance.default_connection_headers)
    # Continue as usual with opening a quantum machine and simulation of a qua program
```

Note the usage of the additional `connection_headers` keyword argument in the `QuantumMachinesManager` object. 
This is only required when connecting to a cloud simulator instance and not for usage with real hardware (where it defaults to `None`). 

Usage of the context manager ensures that the simulator instance is properly spawned before usage and closed when the context is exited.
This is recommended for simple usage, but includes a performance overhead for each context manager block, as spawning a new instance can take 10-20 seconds.
It is also possible to handle the instance manually using `spawn()` and `close()` methods on the instance object.
However, note that without properly closing the instance, it will remain open until it expires and will count towards the user's instance limit.
See the section on [Reusing opened simulator instances](#reusing-opened-simulator-instances) for more details on how to handle this.

```python
instance = client.simulator()
instance.spawn()
# Use the simulator instance object to simulate QUA programs
instance.close()
```

#### Simulator Instance Lifetime

Each user can have up to 3 connected instances at the same time and each instance is automatically closed after 15 minutes.
This can lead to loosing access to the instance in the middle of a session.
Please contact QM if you need to have the instance open for a longer time.
To check the status of the instance, the `is_alive` and `expires_at` properties can be used, e.g.:

```python
if instance.is_alive:
    print(f"Instance is alive and will expire at {instance.expires_at}")
else:
    print("Instance is not alive anymore")
```

Furthermore, one can make sure that no instances are open under by calling the `close_all()` method on the
client object. This will close all the users instances and make sure resources are available. This is useful when the 
old simulator instance objects are not available anymore.

```python
client.close_all()
```

#### Reusing opened Simulator Instances
The instance object can be reused across multiple simulations by simply reusing the object. 
This is simple within the same python interpreter execution, as the object is stored in memory and can be reused.
However, it is also possible to do between different python interpreter executions by serializing and storing the instance object, in order to load it in the following executions.
This can be particularly useful and saves time for running multiple simulations in succession from an IDE, e.g. for sweeping a parameter space, as it avoids spawning a new simulator instance for each individual simulation. 
Serialization and saving can be handled by the `pickle` module in python.

Within the first python interpreter execution, the instance object can be serialized and stored to a file:

```python
    from qm_saas import client
    import pickle
    instance = client.simulator()
    instance.spawn()
    pickle.dump(instance, open("path/to/instance.pkl", "wb"))
    ...
    # Use the instance to simulate
    ...
```

In the next python interpreter execution, the instance object can be loaded and used for simulation:

```python
    import pickle
    instance = pickle.load(open("path/to/instance.pkl", "rb"))
    # The spawn command will not trigger the creation of a new instance if there is already an instance opened with the
    # same id.
    instance.spawn()
    ...
    # Use the instance to simulate
    ...
    instance.close()
```

The saving and loading saves the time that it takes to spawn a new instance in the cloud and allows to share the same instance across multiple python interpreter executions. 
Note that the use of `instance.spawn()` will not create a new instance if there is already an instance opened with the same id.
Therefore, the command can be used to make sure that an instance is opened in case another python interpreter has closed it in the meantime, or in case it has expired.

### Simulation options

The QM SaaS supports the simulation of the OPX+ and OPX1000 products. 
This is achieved by selecting the respective QOP version through the `QoPVersion` enum.
The QOP version is passed to the `simulator` method when creating an instance. `QoPVersion.v2_X_Y` will give instances of OPX+ simulators and `QoPVersion.v3_X_Y` will give instances of OPX1000 simulators, respectively.

```python
from qm_saas import client, QoPVersion
from qm import QuantumMachinesManager

with client.simulator(QoPVersion.v3_2_0) as instance:
    # Use the instance object to simulate QUA programs
    qmm = QuantumMachinesManager(host=instance.host,
                                 port=instance.port,
                                 connection_headers=instance.default_connection_headers)
    # Continue as usual with opening a quantum machine and simulation of a qua program
```

#### Simulation of different OPX+ hardware configurations

For details about simulating different OPX+ hardware configurations, see the [QOP simulator guide](simulator.md#simulating-multiple-controllers). 

#### Simulation of different OPX1000 hardware configurations

When simulating the OPX1000, there is a default configuration of 1 OPX1000 with LF-FEMs in slots 1-4 and MW-FEMs in slots 5-8.
It is possible to define a custom FEM configuration of the simulator instance. 
This is done by creating a `ClusterConfig` object and adding the required controllers and FEMs to it. 
Initially a controller needs to be added to the configuration via `ClusterConfig.controller()`. 
The FEMs can then be added to this controller object via the `lf_fem(List[int])` and `mw_fem(List[int])` methods. 
Available slots are 1-8, and both LF FEMs and MW FEMs can be added. 
Trying to add two FEMs to a single slot will raise an error.
Multiple controllers can be added; they are automatically named `con1`, `con2`, etc., according to their creation order.

The `ClusterConfig` object is then passed to the `simulator` method to create an instance with the given configuration.

```python
from qm_saas import ClusterConfig, client

cluster_config = ClusterConfig()
controller = cluster_config.controller()
controller.lf_fems(1, 2, 3, 4)
controller.mw_fems(5, 6, 7, 8)

with client.simulator(cluster_config=cluster_config) as instance:
    # Use the instance object to simulate QUA programs on a config of 4 LF and 4 MW FEMs
    qmm = QuantumMachinesManager(host=instance.host,
                                 port=instance.port,
                                 connection_headers=instance.default_connection_headers)
    # Continue as usual with opening a quantum machine and simulation of a qua program
    job = qmm.simulate(qua_config, qua_program, SimulationConfig(int(1e4)))
    job.wait_until("Done", timeout=10)
    simulated_samples = job.get_simulated_samples()

# Use the simulated samples to analyze the results.
simulated_samples.con1.plot()
```
