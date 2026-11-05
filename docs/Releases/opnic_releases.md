# OPNIC Releases

Here you can find release notes for the OPNIC software release package.
Each release bundles the OPNIC driver, SDK, and service (including the OPNIC CLI tool) into a single package with an installation script.
For installation and upgrade instructions, see the [OPNIC Installation Guide](../Hardware/OPNIC_Installation.md).

## OPNIC 1.0.1

### Download

Choose the bundle that matches your server architecture and CUDA GPU support requirement:

| Bundle | Architecture | CUDA GPU Support |
|---|---|---|
| [opnic-release-v1.0.1-amd64-cuda.zip](https://qmpublic.s3.us-east-1.amazonaws.com/OPNIC/opnic-release-v1.0.1-amd64-cuda.zip) | x86_64 | Yes |
| [opnic-release-v1.0.1-amd64-no-cuda.zip](https://qmpublic.s3.us-east-1.amazonaws.com/OPNIC/opnic-release-v1.0.1-amd64-no-cuda.zip) | x86_64 | No |
| [opnic-release-v1.0.1-arm64-cuda.zip](https://qmpublic.s3.us-east-1.amazonaws.com/OPNIC/opnic-release-v1.0.1-arm64-cuda.zip) | ARM64 | Yes |
| [opnic-release-v1.0.1-arm64-no-cuda.zip](https://qmpublic.s3.us-east-1.amazonaws.com/OPNIC/opnic-release-v1.0.1-arm64-no-cuda.zip) | ARM64 | No |

### Compatibility

* QOP: {{ requirement("QOP", "3.7") }} or later.
* QOPA: {{ requirement("QOPA", "2.0.0") }} or later.

!!! Note
    To upgrade from an earlier release, run `uninstall.sh` from the new release package before running the installer.
    See Step 3 of the [OPNIC Installation Guide](../Hardware/OPNIC_Installation.md#opnic-installation-in-the-host-server).

### Release Notes

The following changes are relative to OPNIC 0.9.

**Added**

- Added an installation script that installs the OPNIC driver, SDK, service, and CLI tool in one step, with separate CUDA and no-CUDA bundles for x86_64 and ARM64 servers.
- Added CUDA-Q support through the OPNIC bridge. See the [NVQLink CUDA-Q Guide](../Guides/NVQLink_CUDAQ_Guide.md).
- Added the `opnic status` command to the OPNIC CLI tool.
- Added automatic rebuild of the OPNIC driver on kernel updates.
- Added stable device names for OPNIC cards.

**Changed**

- Increased the OPNIC sync timeout to 5 minutes. <!-- PB-886, PB-1120 -->

**Fixed**

- Fixed several issues that could cause OPNIC sync with the OPX1000 to hang or fail, including after an OPNIC reset or link re-calibration. <!-- PB-1124 -->
- Fixed cases where the OPNIC service did not start after an unclean shutdown.
- Fixed I2C timeouts when accessing the OPNIC.
- Fixed data transfer issues on servers with an IOMMU enabled and in GPU stream kernels. <!-- PB-1129, PB-1136 -->
