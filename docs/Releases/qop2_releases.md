# OPX+ (QOP 2) Releases

Here you can find release notes and version files for the latest version of {{ requirement("OPX+",2) }}

## QOP 2.4.X

### QOP 2.4.4
For an in-depth review of the version's new features and upgrades, please see [the release notes](assets/QOP_Release_Notes_V2_4_4.pdf).

- QOP 2.4.4 can be downloaded from [here](https://qmpublic.s3.amazonaws.com/QOP/QOP2.4.4/1742888094-z7k1up/QOP2.4.4.tar.gz.age).

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
- QOP 2.2.2 can be downloaded from [here](https://qmachines-artifacts.s3.amazonaws.com/device-updates/QOP/QOP2.2.2/QOP222.tar.gz.age).

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
- QOP 2.2.0 can be downloaded from [here](https://qmachines-artifacts.s3.amazonaws.com/device-updates/versions/QOP220.tar.gz.age).

- See 2.2 release notes above.

## QOP 2.0.X

For an in-depth review of the version's new features and upgrades, please see [the release notes](assets/QOP_V2.0_Release_Notes.pdf).

