# OPX+ (QOP 2) Releases

Here you can find release notes and version files for the latest version of {{ requirement("OPX+",2) }}

The version files and installation steps can be found [here](https://quantum-machines.atlassian.net/servicedesk/customer/portal/1/article/2505834497).

!!! Note
    Only registered customers can view this link. Please contact your QM representative if you are a customer and don’t have access.

[comment]: <> (## QOP 2.3.X)

[comment]: <> (For an in-depth review of the version's new features and upgrades, please see [the release notes]&#40;./QOP_Release_Notes_V2_3.pdf&#41;.)

[comment]: <> (### QOP 2.3.0)

[comment]: <> (See 2.3 release notes above.)

## QOP 2.2.X

For an in-depth review of the version's new features and upgrades, please see [the release notes](assets/QOP_Release_Notes_V2_2.pdf).

### QOP 2.2.2

#### Added

- Improved and optimized Octave automatic calibration.

#### Bug fixes

- Fixed a rare case where closing one quantum machine will interfere with the digital ports of another quantum machine.
- Fixed issues with negative IF.
- Fixed a scenario where conditional digital pulse would play even if the condition is false.
- Fixed an issue with using `wait_for_all_vlaues` with `timestamp stream`.

??? note "Octave users"
    {{ requirement("QUA", "1.1.5") }} is required for those who use {{ requirement("QOP", "2.2.2") }} and have an Octave in the cluster.

### QOP 2.2.0

See 2.2 release notes above.

## QOP 2.0.X

For an in-depth review of the version's new features and upgrades, please see [the release notes](assets/QOP_V2.0_Release_Notes.pdf).

