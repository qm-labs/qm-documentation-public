# QOP Admin (QOPA) Releases

Here you can find release notes and version files for the latest version of QOP Admin (QOPA).
Note that the admin was taken out of the QOP package and is a separate package starting from QOP 2.5 and QOP 3.3.

## QOPA 2.1.0

### Download

[QOPA2.1.0.tar.gz.age](https://qmpublic.s3.amazonaws.com/QOPA/1787231047-4nt6m1/QOPA2.1.0.tar.gz.age)

*SHA-256 checksum:* `998182e881f55594ebe8f2df468a2f92b875de3b763a1405e09eb2287d4bf753`

### Release Notes

**Added**

- Added recovery IP configuration to allow for easier system recovery.
- Added the ability to install a BSP package. **Note:** This feature is unlocked when the device is equipped with BSP 1.4.0. Devices with an earlier version must first upgrade to BSP 1.4.0 via the USB method.
- Added `sdk`, `driver`, and `service` fields to the OPNIC UI.
- Added time period selection for log collection.

**Changed**

- Only unclustered devices can now install QOPA from the Devices menu.
- QOP downgrades are no longer blocked completely below 3.6.3 (introduced in QOPA 1.6.1 and 2.0.1) - blocking is now only done when the specific hardware revision does not support it.

**Known Issues**

- Clusters can show a "Failed" status while operations, such as a QOP update or clustering, are in progress.

## QOPA 2.0.2

### Download

[QOPA2.0.2.tar.gz.age](https://qmpublic.s3.amazonaws.com/QOPA/1786270700-7maeuy/QOPA2.0.2.tar.gz.age)

*SHA-256 checksum:* `986c1566bab9fefdcfe298065476cdad863d9f9b0a5f14ca5ff47908e8039dbc`

### Release Notes

**Added**

- Added a fallback action to power down FEMs on system shutdown, to prevent rare voltage spikes.

## QOPA 2.0.1

### Download

[QOPA2.0.1.tar.gz.age](https://qmpublic.s3.amazonaws.com/QOPA/1783587807-auda87/QOPA2.0.1.tar.gz.age)

*SHA-256 checksum:* `76332178d5add4fddf309b517d8548ce942a04adb3a6bb0b351a402677576b24`

!!! important
    Since QOPA cannot be downgraded to an older version, please note that:

    - QOP cannot be downgraded below version 3.6.3.
    - OPNIC requires QOPA 2.0 or later with QOP 3.7, so downgrading to 3.6.3 would not allow working with the OPNIC.

### Release Notes

**Added**

- Added support for QOP3.8.x

**Changed**

- Blocked installation of QOP versions 3.6.2 and earlier.

**Fixed**

- Fixed cases where QOPA could be downgraded to an older version.
- Fixed cases where QOPF could be downgraded to an older version.

**Removed**

- Discontinued Octave support for clusters >= QOP3.8.x

## QOPA 2.0.0

This release is a complete redesign focused on improving the UX when managing clusters, especially for multi-cluster environments.

### Download

[QOPA2.0.0.tar.gz.age](https://qmpublic.s3.amazonaws.com/QOPA/1778076475-w3ww4x/QOPA2.0.0.tar.gz.age)

*SHA-256 checksum:* `4b13a06247d8b78a45b26a9a4d459325463afa8cddf99481b0e3943d26afbee6`

!!! Note
    For OPX1000, upgrades to QOPA 2.0.0 are not supported from versions before QOP 3.3.0.
    Customers on earlier versions must first upgrade through QOP 3.3.1. 
    For OPX+, upgrades to QOPA 2.0.0 are not supported from versions before QOP 2.5.0.
    Customers on earlier versions must first go through QOP 2.5.0.
    See the [QOP Installation Guide](qop_installation_guide.md) for detailed instructions.

!!! Note
    OPNIC support requires QOP 3.7 or later. OPNIC is not supported with QOP 3.6.

### Release Notes

**Added**

- Added support for installing QOPA and QOPF packages on devices without requiring a cluster.
- Added an automated OPNIC pairing flow.
- Added a device-focused view.
- Added a versioned API (v2) that guarantees backward compatibility across future releases. Breaking changes will be introduced only in new API versions, with deprecation notices for older endpoints.

**Changed**

- Introduced a cluster-oriented layout where users select a cluster and perform operations in that cluster's context.
- Limited clustering operations to one cluster at a time. Moving a device between clusters now requires two actions:
    - Remove the device from the original cluster and wait for the operation to finish
    - Add the unclustered device to the new cluster and wait for the operation to finish
- Enabled FEM channel unlocking for devices without requiring a cluster.

**Fixed**

- Improved QOPF rescue and reboot reliability during update flows.
- Fixed an issue where the filesystem on OPX1000 controller could fill up due to cleanup not running correctly in multi-controller clusters.
- Fixed an issue where QOPA continued to display and use the link-local IP address for a device after it had been switched to a static IPv4 address.

**Deprecated**

- Deprecated support for Octaves in OPX1000 clusters. This support will be removed in QOP 3.8.0.

## QOPA 1.6.1

QOPA 1.6.1 can be downloaded from [here](https://qmpublic.s3.amazonaws.com/QOPA/1782020467-ofhisn/QOPA1.6.1.tar.gz.age).

!!! important
    Since QOPA cannot be downgraded to an older version, please note that:

    - This version does not support OPNIC. OPNIC requires QOPA 2.0 or later with QOP 3.7.
    - QOP cannot be downgraded below version 3.6.3.

**Added**

- Add support for QOP 3.7.
- Add support for QOPF 1.2.

**Changed**

- Block QOPA from installing QOP versions older than QOP 3.6.3.

**Fixed**

- Fixed cases where QOPA could be downgraded to an older version.
- Fixed cases where QOPF could be downgraded to an older version.
- Ensure that QOPAs stopped during QOPF installations can re-enable themselves once the timeout is reached.

## QOPA 1.6.0

QOPA 1.6.0 can be downloaded from [here](https://qmpublic.s3.amazonaws.com/QOPA/1774364953-jjikqm/QOPA1.6.0.tar.gz.age).

!!! important
    Since QOPA cannot be downgraded to an older version, please note that:

    - This version does not support OPNIC. OPNIC requires QOPA 2.0 or later with QOP 3.7.

**Added**

- Add support for QOP 3.7.

## QOPA 1.5.1

### Download
[QOPA1.5.1.tar.gz.age](https://qmpublic.s3.amazonaws.com/QOPA/1766137065-lm2z6u/QOPA1.5.1.tar.gz.age)

### Release Notes

**Added**

- Added support for QOP 2.6.0.

## QOPA 1.5.0

### Download
[QOPA1.5.0.tar.gz.age](https://qmpublic.s3.amazonaws.com/QOPA/1764772641-fd38mr/QOPA1.5.0.tar.gz.age)

### Release Notes

**Added**

- Added an option to unlock locked channels in FEMs.
- Added visual and audible indications for operations and state changes of the OPX1000 system.
- Added IP-based rate limiting to the QOPA API.

**Changed**

- Ensured that cluster changes or updates cannot be started if one or more devices are not reachable.
- Changed the shutdown and restart operations to completely power down the entire system.

**Fixed**

- Fixed Octave network configuration to not lose connectivity on earlier software versions.
- Fixed a problem that caused the process of adding an Octave to an existing OPX+ cluster to fail.
- Fixed an issue where cluster-level status messages were not being displayed in the topology view.
- Fixed the QOPF installation procedure to ensure it functions correctly over a Link-local connection.
- Fixed an issue where an Octave can run out of temporary disk space.

## QOPA 1.4.1

### Download
[QOPA1.4.1.tar.gz.age](https://qmpublic.s3.amazonaws.com/QOPA/1762876057-ida1o5/QOPA1.4.1.tar.gz.age)

### Release Notes

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

### Download
[QOPA1.3.0.tar.gz.age](https://qmpublic.s3.amazonaws.com/QOPA/1754056874-g1p5lw/QOPA1.3.0.tar.gz.age)

### Release Notes

**Changed**

- Added OPX+ support to QOPA
  - Allow OPX+ and OPX1000 clusters to reliably be in the same network.
  - OPX+ and OPX1000 devices can NOT be in the same cluster.
  - Octaves could only be moved between the clusters of identical device types.
      To move the Octave device (for example) from the OPX+ cluster to the OPX1000 cluster, the Octave device needs to be unclustered first.

## QOPA 1.2.2

### Download
[QOPA1.2.2.tar.gz.age](https://qmpublic.s3.amazonaws.com/QOPA/1750000608-9bcu65/QOPA1.2.2.tar.gz.age)

### Release Notes

**Changed**

- Topology reports status "unknown" if gateway does not respond.

**Fixed**

- Outdated streaming results are now being deleted from the device's disk.
- Improved the restart flow when the cluster is not responding, preventing the cluster from being stuck.

## QOPA 1.2.1

### Download
[QOPA1.2.1.tar.gz.age](https://qmpublic.s3.amazonaws.com/QOPA/1746012714-1363t6/QOPA1.2.1.tar.gz.age)

### Release Notes

**Added**

- Added an option to pair a Grace-Hopper server as an OPNIC accelerator host.
- The FEMs serial numbers will now be displayed in the topology view.

**Fixed**

- Shutting down an OPX1000 cluster will now correctly turn off the OPX1000 controllers.

**Removed**

- Removed the `/gateway/health` REST API endpoint, please use the `/gateway/topology?cluster_name=foo` endpoint instead. The cluster health can be read from the field `cluster_status` on the root response object.

## QOPA 1.0.0

### Download
[QOPA_1.0.0.tar.gz.age](https://qmpublic.s3.amazonaws.com/QOPA/1741714454-j30f8h/QOPA_1.0.0.tar.gz.age)
