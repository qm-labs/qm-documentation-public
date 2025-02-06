QM Cloud Simulator as a Service Python Package (qm-saas) Releases

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).


## 1.1.3 - 2025-01-08

**Added**

- Support for QOP 3.2.4 version

## 1.1.2 - 2024-12-17

**Added**

- The simulator client now supports python 3.12 and with that `qm-qua` packages >=1.2.2.
- QoPVersion now has a `latest` element that can be used to get the latest supported version of the simulator.
- Creating a simulator instance using `client.simulator()` will now automatically use the latest supported version of the simulator.

**Fixed**

- Fixed an issue where the wrong type was returned from `client.simulator()` (was `QoPSaaSInstance` instead of `QmSaasInstance`). 
- The `QmSaasInstance` object can now be serialized using pickle.
- Fixed an issue where using `QoPVersion.v3_2_0` would raise an error when trying to define custom FEM configurations.

## 1.1.1- 2024-11-13

**Changed**

- Renamed the `QoPSaaS` class to `QmSaas` and `QoPSaaSInstance` to `QmSaasInstance` respectively.
- Removed the `sim` prefix from many class properties, e.g. `sim_host` -> `host`.
- The default `host` has changed. The previous default `sim_host` would still work by redirecting to the new one.

**Added**

- The simulator now supports Version [QOP 3.2.0](https://docs.quantum-machines.co/latest/docs/Releases/qop3_releases/).
- Added a `QmSaas.close_all()` function that allows the user to close all simulator instances opened by his client
  (maximum per client: 3).
- Users can query if the instance object they are using is alive and at what datetime it will expire via
  `QmSaasInstance.is_alive()`, `QmSaasInstance.expires_at()`. (default time limit: 15 minutes)
- Every instance now has a cluster_config that shows the (controller) FEM configuration for a given simulator instance 
  `QmSaasInstance.cluster_config()`.
- Users can now freely define the controller FEM configuration of their instance via a `ClusterConfig()` object.
  FEMs can be added to this config via `ClusterConfig().controller().lf_fem(slot)` and
  `ClusterConfig().controller().mw_fem(slot)`.

## 1.0.2 - 2024-07-02

**Added**

- The simulator now supports Version [QOP 3.1.0](https://docs.quantum-machines.co/latest/docs/Releases/qop3_releases/). This means that saas now also simulates the OPX1000 product.
- The user can select it via `QoPVersion.v3_1_0` and pass it to the constructor of a simulator instance.
- There is only one static configuration supported, which is 4 LF FEM modules in the first four slots and 4 MW FEM
  modules in the last four slots.

## 1.0.1 - 2024-06-13

**Fixed**

- Fixes in the documentation.

## 1.0.0 - 2024-06-12
The initial release of the QM Simulator as a Service.
