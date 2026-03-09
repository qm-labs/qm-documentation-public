# OPX+ (QOP 2) Releases

Here you can find release notes and version files for the latest version of {{ requirement("OPX+",2) }}

## QOP 2.6.X

### QOP 2.6.0
- QOP 2.6.0 can be downloaded from [here](https://qmpublic.s3.amazonaws.com/QOP/QOP2.6.0/1766318308-7x9itz/QOP2.6.0.tar.gz.age). Please follow the [QOP Installation Guide](qop_installation_guide.md).
- Required to use with QOPA 1.5.1  [here](https://qmpublic.s3.amazonaws.com/QOPA/1766137065-lm2z6u/QOPA1.5.1.tar.gz.age).
- It is recommended to use with {{requirement("QUA", "1.2.4")}} or newer.

**Fixed**

* Resolved an issue where QUA calculations could produce incorrect values. <!-- PB-338 -->
* Fixed a rare issue that caused core‑to‑core data transfers to return erroneous results. <!-- PB-385 -->
* Resolved a bug where consecutive frame rotations ignored the Python literal rotation when mixing literal and QUA variables. <!-- PB-75 -->
* Fixed a behavior that generated unexpected pulse sequences in switch/case blocks inside `for` loops ending with a frame rotation. <!-- PB-512 -->
* Fixed an issue where specific OPD channels inflated the number of reported tags. <!-- PB-223 -->
* Resolved a failure caused by oversized gRPC messages, such as long waveforms, integration weights, or large data payloads. <!-- PB-194 -->
* Fixed an issue arising when combining `elif` conditionals with variable assignments and save operations. <!-- PB-533 -->
* Corrected a condition where logically unreachable statements were still executed and played. <!-- PB-537 -->
* Addressed a sequencing issue where rotate/reset frame operations did not execute in the expected order. <!-- PB-28 -->

## QOP 2.5.X

### QOP 2.5.0
For an in-depth review of the version's new features and upgrades, please see [the release notes](assets/QOP2.5_Release_Notes.pdf).

- QOP 2.5.0 can be downloaded from [here](https://qmpublic.s3.amazonaws.com/QOP/QOP2.5.0/1754209957-6wuxhq/QOP2.5.0.tar.gz.age). Please follow the [QOP Installation Guide](qop_installation_guide.md).
- It is recommended to use with {{requirement("QUA", "1.2.3")}} or newer.

??? note "Octave users upgrading from {{requirement("OPX+", "2.2.X")}} and below"
    Octave users upgrading from QOP version 2.2.X or earlier are encouraged to review the
    [QOP 2.4.4 Release notes](./assets/QOP_Release_Notes_V2_4_4.pdf), to learn about the updated Octave clock and
    configuration introduced in that version.

??? note "QOP Admin (QOPA)"
    Starting with this version, the Admin is taken out of the QOP package, and will
    become a stand-alone package to be installed separately. This QOP version comes with QOPA version 1.3.0 included.
    However, future versions of both QOP and QOPA will be installed sepaeately.
    For more information, please visit the [QOPA Releases](./qopa_releases.md) page.

## QOP 2.4.X

### QOP 2.4.4
For an in-depth review of the version's new features and upgrades, please see [the release notes](assets/QOP_Release_Notes_V2_4_4.pdf).

- QOP 2.4.4 can be downloaded from [here](https://qmpublic.s3.amazonaws.com/QOP/QOP2.4.4/1742888094-z7k1up/QOP2.4.4.tar.gz.age). Please follow the [QOP Installation Guide](qop_installation_guide.md).

??? note "Octave users"
    - Starting with this version, the Octave clock is managed automatically, as explained in the 
    [QOP clock](../Guides/qop_clock.md) guide. The qm.octave.set_clock() command is no longer required and will raise an error if used.
    - When using this version with `qm-qua >= 1.2.1`, you no longer need to initialize the `OctaveConfig`. 
    Instead, the octave connection details are automatically obtained from the cluster information as explained [here](../Guides/octave.md/#initiate-communication-with-an-octave).
    In addition, the `octave_calibration_db_path` can be provided as an argument when creating a `QuantumMachinesManager`. 
    For further details, refer to the [Quantum Machine Manager API](../API_references/qm_manager_api.md) documentation.

## QOP 2.2.X

For an in-depth review of the version's new features and upgrades, please see [the release notes](assets/QOP_Release_Notes_V2_2.pdf).

### QOP 2.2.2
- QOP 2.2.2 can be downloaded from [here](https://qmachines-artifacts.s3.amazonaws.com/device-updates/QOP/QOP2.2.2/QOP222.tar.gz.age). Please follow the [QOP Installation Guide](qop_installation_guide.md).

**Added**

- Improved and optimized Octave automatic calibration.

**Fixed**

- Fixed a rare case where closing one quantum machine will interfere with the digital ports of another quantum machine.
- Fixed issues with negative IF.
- Fixed a scenario where conditional digital pulse would play even if the condition is false.
- Fixed an issue with using `wait_for_all_vlaues` with `timestamp stream`.

??? note "Octave users"
    {{ requirement("QUA", "1.1.5") }} is required for those who use {{ requirement("QOP", "2.2.2") }} and have an Octave in the cluster.

### QOP 2.2.0
- QOP 2.2.0 can be downloaded from [here](https://qmachines-artifacts.s3.amazonaws.com/device-updates/versions/QOP220.tar.gz.age). Please follow the [QOP Installation Guide](qop_installation_guide.md).

- See 2.2 release notes above.

## QOP 2.0.X

For an in-depth review of the version's new features and upgrades, please see [the release notes](assets/QOP_V2.0_Release_Notes.pdf).

