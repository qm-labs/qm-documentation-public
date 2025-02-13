# OPX1000 Installation Guide

The following page describes the installation procedure of an OPX1000 system, and for systems with Octaves.
It covers network configuration, OPX1000 connectivity, rack scheme and more.

## Rack Mounting

Instructions for rack mounting the OPX1000 can be found [here](assets/OPX1000 Rack Mounting Installation Guide.pdf).

## Cluster

A **cluster** is a synced and fully-connected system of OPX1000 Chassis, Octaves, and other QM devices. 
A cluster can be comprised of a one or more OPX1000, and it may or may not include Octaves.
All FEMs in one OPX1000 chassis are automatically included in the cluster.

The cluster can be managed and configured via a web admin panel. Through the admin panel, one can check the cluster's health status and topology,
restart the cluster, configure clock settings, access logs, and more. As detailed below, multiple clusters can exist in the same network and be managed by the web admin panel.

## Hardware Installation Procedure

1. Verify you have all the [required components](#required-components-for-the-installation).

2. Mount the system in its designated place. Instructions for rack mounting the OPX1000 can be found [here](#rack-mounting).

3. Insert the FEMs into in the chassis:
    1. To prevent static discharge that can damage the FEM, please use the provided ESD gloves before touching or handling the FEMs.
    2. Slide FEM into an empty slot in the chassis.
    3. Ensure that the FEM is fully inserted and that the FEM panel is flush with the chassis panel. If it is not, check that the captive screws or ejectors are not obstructing the insertion.
    4. Secure the FEM in place using the captive screws. 
    5. Repeat for all FEMs, also install the provided blank FEMs in any remaining empty slots.

        !!! Note
            Turning on the system without all the FEMs installed, or the blank FEMs, can cause the system to overheat, which will increase fan speed and can cause the system to shut down to protect itself from damage.
4. Determine your [network configuration](network_and_router.md#network-overview-and-configuration).
5. Connect the system:
    1. If there is more than one OPX1000:
        1. One OPX1000 is defined as the *main* OPX1000.
        2. Clock: Connect the others OPX1000's clock input to the *main* OPX1000's clock outputs via the supplied SMA cables. Any clock input can be used
        3. QSync: Connect the others OPX1000's QSync port to the *main* OPX1000's Qsync ports via the supplied QSync unshielded ethernet cable. Any QSync port can be used, but it's good practice to match the connections' numbering with the clock.
        4. Data: Connect the others OPX1000's Comm port to the *main* OPX1000's Comm ports via the supplied optical cables. Remove the connectors' protectors if present. Any Comm port can be used, but it's good practice to match the connections' numbering with the clock & QSync.
    2. Octaves:
        1. If there are any Octaves, connect their clock inputs to any OPX1000's clock outputs.
        2. If all OPX1000es' clock outputs have been used, and there are still unconnected Octaves, then connect the Octave's clock input to other Octave's clock outputs.
    3. Optional: Connect any of the *main* OPX1000 clock inputs to an external reference clock.
    4. Connect the OPX1000 and Octaves to QM router via the ethernet cables, starting from port 2 onwards. Alternatively, connect the devices directly to your local network.
    5. Connect the OPX1000 and Octaves to the power outlet. It is generally recommended to connect both of the OPX1000 power supplies to separate power outlets. See the [opx1000 power requirements section below](#opx1000-power-requirements) for more information.
6. Turn on all the devices.
7. When using new devices, download the [latest QOP version](../Releases/qop3_releases.md) and upload it to the device via the admin panel.
8. Configure the cluster, as shown [below](#configuring-opx1000-and-octave). This step will also install the latest version and can take ~30 minutes. 
9. Once clustered, the system will start calibrations, and the boot sequence should take a few minutes.
10. Open a browser and type the system's IP in the address field to access the admin panel where you can configure the system, check its status and more. See the [network overview section below](network_and_router.md#network-overview-and-configuration) for more details on how to access the cluster.
11. Install the latest Python package by typing `pip install --upgrade qm-qua` in the desired Python environment.
12. Open communication in Python using:
      ```python
      from qm import QuantumMachinesManager
      qmm = QuantumMachinesManager(*args)  
      ```
      This requires passing the correct arguments to the QuantumMachinesManager object. See "accessing the cluster" options [below](network_and_router.md#network-overview-and-configuration). 
      You should see the message `qm - INFO - Health check passed` in the console.


## Extra Topics

### OPX1000 power requirements

=== "Main electricity 100-130VAC (Mostly in the US, Canada, Japan)"

    The OPX1000 has two installed PSUs (power supply units) and room for a third one, allowing for a 2+1 PSU redundancy.
    
    If more than 4 FEMs are used, two PSUs must be used simultaneously to provide the system with sufficient power. 
    They must be connected to separate wall outlets, as each PSU can carry up to 11.3A. 
    A 3rd power supply can be added to achieve PSU redundancy.

=== "Main electricity 200-240VAC (Europe and most of the world)"

    The OPX1000 has two installed PSUs (power supply units) and room for a third one, allowing for a 1+2 PSU redundancy and a 1+2 power grid redudancy.

    If multiple PSUs are used, they must be connected to separate wall outlets, as each PSU can carry up to 10A.
    It is also possible to obtain power source redundancy by connecting the PSUs to different power grids.

!!! Important Safety Information
    The electrical connection must be made in accordance with the National Electrical Code (NEC) and/or the Standard for Electrical Connections (SEC), as applicable. 
    Failure to follow these guidelines may result in equipment damage, safety hazards, or voiding of the warranty.

!!! Important Safety Information
    The system has a dedicated ground post that should be tightened to the infrastructure ground post. 
    Unconnected ground cable may cause permanent system damage.

!!! Important Safety Information
    CAUTION! Shock hazard. System has multiple AC power sources, disconnect all power sources before servicing the system!


### Required components for the installation

??? Information "List of Components"

    To ensure a smooth installation, please make sure you have the following components:

    {{ read_csv("docs/Hardware/assets/OPX1000_installation_components.csv") | add_indentation(spaces=4) }}


### Connectivity Scheme

The multi OPX1000 system has five required connectivity groups. Clock, QSync, Inter-controller communication, Network, and Power

??? Information "Clock"

    The clock signal is distributed by the *main* OPX1000 with an SMA cable per addtional OPX1000 chassis.
    An single OPX1000 chassis can distribute the clock for up to four additional OPX1000 chassis.
    If more than five chassis are used, a tree-like connectivity is needed: *main* OPX1000 chassis distributes the clock 
    to chassis 2-5. Chassis 2 distribute the clock to chassis 6-9, etc...  

??? Information "QSync"

    The QSync signal is passed between the controllers via Cat6 RJ45 (Ethernet) cables. 
    A single OPX1000 chassis can sync for up to four additional OPX1000 chassis.
    If more than five chassis are used, a tree-like connectivity is needed: *main* OPX1000 chassis syncs chassis 2-5.
    Chassis 2 syncs chassis 6-9, etc...


??? Information "Inter-controller Optical Connectivity Scheme"

    Data transfer and communication between controllers are operated via optical cables in an `all-to-all` connectivity.
    Each OPX1000 has 4 optical ports and the preferred connectivity configuration differs with the number of
    controllers, as shown below.

    Click on each configuration to see the connectivity scheme.

    !!! Note
        The following is only a recommendation. Every configuration that establishes all-to-all connectivity is valid.
      

    === "2 OPX1000"

        Connect all four optical cables between the chassis

    === "3 OPX1000"

        Connect every chassis with two optical cables to every other chassis

    === "4 OPX1000"

        Connect every chassis with one optical cables to every other chassis. One port would remain unused.

    === "5 OPX1000"

        Connect every chassis with one optical cables to every other chassis.

    === "6-8 OPX1000"

        Connect every chassis 1-4 to every chassis 5-8 with one optical cable.  

    === "9-32 OPX1000"

        These confiugration will be shipped with special splitter cables which would come with connection instructions.


### Configuring OPX1000 and Octave

??? Information "Check Devices IP"
    
    1. Connect the devices and a computer to the local network of the QM router (ports 2-10)
    2. In CMD run: 
    ```
    ssh -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" -m hmac-sha1,hmac-md5 admin@192.168.88.1 ip arp print
    ```
    3. Identify the IP of the device using its MAC addresses. The MAC address is printed on a sticker on the device.

??? Information "Configuring the Device's IP"
    
    It is possible to change the IP of the devices. If it is needed, please contact QM for assistance.

??? Information "Cluster Devices"

    Follow the steps in [this video](https://www.youtube.com/watch?v=ZVuvnJkSbDA)

### Configuring the QM router

See [this page](network_and_router.md#configuring-the-qm-router).

