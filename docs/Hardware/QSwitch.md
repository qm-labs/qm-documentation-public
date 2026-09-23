# QSwitch

The QSwitch is a low-leakage signal switching unit for cryogenic measurement setups.
See the user manual for the full description of channels, contact configurations, and electrical specifications.

## Manuals and firmware


### QSwitch User Manual

- [QSwitch User Manual (D22019-B00)](assets/QSwitch%20User%20Manual.pdf)

### Firmware update version 2.0

**Release Notes**

- [Firmware release notes](assets/QSwitch%20Firmware%20Release%20Notes.pdf)
- [Firmware 2.0 extended release notes](assets/QSwitch%20FW2.0%20Extended%20Release%20Notes.pdf) — introduces a new Ethernet communication protocol.

**Download**

- [Windows firmware updater](https://qmpublic.s3.amazonaws.com/QSwitch/firmware-2.0/1790165373-chmrho/qswitch-fw-update_2.0.exe)
- [Linux firmware updater](https://qmpublic.s3.amazonaws.com/QSwitch/firmware-2.0/1790165373-chmrho/qswitch-fw-update-linux_2.0)

!!! Important
    Please follow the instructions in the user manual for performing a firmware update.
    On Windows, you may need to confirm that it is safe to run the updater executable.


## Drivers and code examples

- A QCoDeS driver is available in [qcodes_contrib_drivers](https://github.com/QCoDeS/Qcodes_contrib_drivers/tree/main/src/qcodes_contrib_drivers/drivers/QDevil).
- A Python wrapper is available in the [qdac2-tools](https://github.com/QDevil/qdac2-tools) repository.
