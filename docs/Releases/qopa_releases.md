# QOP Admin (QOPA) Releases

Here you can find release notes and version files for the latest version of QOP Admin (QOPA).
Note that the admin was taken out of the QOP package and is a separate package starting from QOP 2.5 and QOP 3.3.

## QOPA 1.4.1

QOPA 1.4.1 can be downloaded from [here](https://qmpublic.s3.amazonaws.com/QOPA/1762876057-ida1o5/QOPA1.4.1.tar.gz.age).

**Added**
- Support for installing the Quantum Operation Platform Firmware (QOPF) package for OPX1000
  - Added the QOPF package with specialized installation process, for a robust and safe firmware upgrades.
  - Added safeguard to prevent cluster booting when at least one FEM does not comply with QOPF version 1.1.0.
- Added BSP compatibility check to all QOP3.x.x package installation procedures.

**Changed**
- Changed device discovery from polling to streaming, resulting in lower topology latency.
- Optimized loading speed of the QOPA user interface.
- Deny API operations on devices during clustering or update procedures.

**Fixed**
- Fixed downgrades to <= QOP3.4.x from >= QOP3.5.0.
- Fixed streaming results cleanup for OPX+ devices preventing a full disk.
- Fixed streaming and compiler files cleanup for OPX1000 devices preventing a full disk.
- Fixed administrative component installation on Octaves.
- Fixed Octave network settings.

## QOPA 1.4.0

Please reach out to Quantum Machines support in order to get installation files and instructions

## QOPA 1.3.0

QOPA 1.3.0 can be downloaded from [here](https://qmpublic.s3.amazonaws.com/QOPA/1754056874-g1p5lw/QOPA1.3.0.tar.gz.age).

**Changed**

- Added OPX+ support to QOPA
  - Allow OPX+ and OPX1000 clusters to reliably be in the same network.
  - OPX+ and OPX1000 devices can NOT be in the same cluster.
  - Octaves could only be moved between the clusters of identical device types.
      To move the Octave device (for example) from the OPX+ cluster to the OPX1000 cluster, the Octave device needs to be unclustered first.

## QOPA 1.2.2

QOPA 1.2.2 can be downloaded from [here](https://qmpublic.s3.amazonaws.com/QOPA/1750000608-9bcu65/QOPA1.2.2.tar.gz.age).

**Changed**

- Topology reports status "unknown" if gateway does not respond.

**Fixed**

- Outdated streaming results are now being deleted from the device's disk.
- Improved the restart flow when the cluster is not responding, preventing the cluster from being stuck.

## QOPA 1.2.1

QOPA 1.2.1 can be downloaded from [here](https://qmpublic.s3.amazonaws.com/QOPA/1746012714-1363t6/QOPA1.2.1.tar.gz.age).

**Added**

- Added an option to pair a Grace-Hopper server to create a DGX-Quantum cluster.
- The FEMs serial numbers will now be displayed in the topology view.

**Fixed**

- Shutting down an OPX1000 cluster will now correctly turn off the OPX1000 controllers.

**Removed**

- Removed the `/gateway/health` REST API endpoint, please use the `/gateway/topology?cluster_name=foo` endpoint instead. The cluster health can be read from the field `cluster_status` on the root response object.

## QOPA 1.0.0

QOPA 1.0.0 can be downloaded from [here](https://qmpublic.s3.amazonaws.com/QOPA/1741714454-j30f8h/QOPA_1.0.0.tar.gz.age).
