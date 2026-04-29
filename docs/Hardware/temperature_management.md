# Temperature Management

This page summarizes temperature management, monitoring, and routine maintenance recommendations for QOP systems based on OPX+, OPX1000, and Octave devices.

## General recommendations

- Install and operate the system in a temperature-controlled environment.
- Keep all air inlets and outlets unobstructed.
- In rack installations, note that devices near the top of the rack typically operate at higher temperatures.
- When possible, improve rack ventilation to maintain a steady flow of cool air around the system.
- For high-density installations, consider racks with active cooling when passive airflow is not sufficient.

Choose the relevant hardware tab below.

=== "OPX+"

    ### Airflow and maintenance

    The OPX+ includes two rear fans that operate at a fixed speed and direct air out of the unit. Fresh air enters from the left side panel, as viewed from the front, through fixed filters.

    Under typical dust conditions, it is recommended to clean the air filters every six months as part of routine maintenance. Clean the filters externally with a vacuum cleaner using low suction power.

    ### Monitoring and thermal protection

    The OPX+ monitors several internal temperatures and provides warning messages before thermal protection thresholds are reached.

    | Component | Working limit | Prevention threshold in QOP 2.2.2 | Prevention threshold in QOP 2.4.0 and later |
    |-----------|---------------|-----------------------------------|---------------------------------------------|
    | FPGA | 100 C | 80 C | 95 C |
    | CPU | 105 C | 70 C | 100 C |

    If a component reaches a critical temperature, the device shuts itself down, the cluster becomes inactive, and a warning is shown in both Python and the QM app.

    A typical Python-side error can look like this:

    ```text
    QMConnectionError: Encountered connection error from QOP: details: Hardware not ready: [FPGA temperature X is higher than max allowed Y], status: Status.UNAVAILABLE
    ```

    The exact values in the message depend on the active protection threshold and the measured temperature at the time of the failure.

    You can query the controller temperature from the QMM API:

    ```python
    temperature = QuantumMachinesManager(...).get_controllers()[i].temperature
    ```

    Here, `i` is the zero-based index of the controller in the cluster.

=== "OPX1000"

    ### Airflow and thermal protection

    The OPX1000 chassis is designed to minimize maintenance requirements. It does not use dense meshes or air filters, and its mechanical structure is designed to allow free airflow while limiting dust accumulation.

    Air enters from the FEM side of the chassis and exits from the fan side. To keep the system stable and quiet, avoid blocking airflow on either side of the chassis.

    The system implements over-temperature shutdown logic to protect the hardware from permanent damage. Software alerts are raised before shutdown, allowing the user to correct the issue before the system reaches a protection limit.

    ### Scenarios that affect thermal performance

    #### Blocked airflow

    Blocked airflow on either side of the system can reduce thermal performance.

    - Check both the front and rear sides of the chassis for airflow obstructions.
    - Pay particular attention to dense cable routing near the FEM front panel, for example SMA cables bundled too close to the chassis face.
    - Route cables up or down outside the system frame before routing them to the side.
    - Do not operate the chassis with a missing FEM or a missing blank FEM, since open slots can disturb airflow, increase fan speed, and lead to thermal shutdown.

    #### Fan failure

    Fan failure is reported in the QOPA web interface.

    - The chassis has six fans and can continue operating with five.
    - Losing one fan does not degrade system functionality, but it can increase the noise emitted by the system.
    - Fans are hot-swappable, so they can be replaced without powering the system down.
    - Until a replacement fan is available, keep the faulty fan installed to avoid excessive airflow escape.

    To replace a fan:

    1. Open the fan captive screws.
    2. Pull the fan out using the top handle.
    3. Insert the replacement fan fully into place.
    4. Tighten the captive screws.

    ### Cleaning

    Dust is unlikely to degrade system performance, but it may have a cosmetic effect, especially on the FEM front panel.

    To clean the front panel:

    1. Power down the system.
    2. Use a small, soft brush attached to a vacuum cleaner.
    3. If access is limited, disconnect SMA cables as needed.
    4. Vacuum the dust from the front panel area.

    Additional cleaning guidance:

    - The internal structure is designed to be resilient to dust accumulation.
    - Do not insert foreign objects into chassis slots in an attempt to clean them.
    - Fan modules generally remain clean, but they can be inspected and cleaned with the same vacuum method while the system is powered down.
    - There is no need to remove FEM modules to inspect for dust contamination.
    - Do not tamper with any connectors during cleaning.

    ### Fan noise and fan control

    The OPX1000 automatically controls fan speed to balance acoustic noise with safe and stable system operation. No user fan control is available in standard operation.

    As noted above, the system can continue operating with one failed fan, but the emitted noise may increase.

    In special support scenarios, QM customer support may apply manual fan-control settings with a fixed speed. This can increase the risk of an over-temperature event if operating conditions change.

=== "Octave"

    ### Airflow guidelines

    The Octave uses two software-controlled rear fans that draw air into the unit. Warm air exits through the front panel near the center of the chassis, in front of the up-converters.

    - Do not place equipment on top of the Octave.
    - Leave clearance above the unit to allow the warm air to exit. One rack unit of free space is recommended.
    - Maintain a clear flow of cool air into the rear of the system.

    ### Monitoring and fan control

    The Octave monitors multiple internal temperatures, including the CPU, FPGA, synthesizers, and up-converters.

    - The maximum allowed temperature for each module is 65 C.
    - Fan speed is controlled according to the highest measured internal temperature.
    - The fans start spinning once the internal temperature crosses 55 C.
    - A PID control loop is used to stabilize the temperature for stable signal output.

    Temperature can vary between devices and modules because of operating mode differences, such as gain, frequency, and on/off state, as well as part-to-part thermal variation.

    When a module reaches 65 C, the module shuts off and a warning is presented to the user.
