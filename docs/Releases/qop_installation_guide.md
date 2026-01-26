# QOP Installation Guide 
This guide outlines the steps for installing a QOP package on either an OPX+ or OPX1000 device.

## Installation Procedure
1. Open a web browser on a computer that has network access to the device you wish to update.
1. In the address bar, enter the IP address typically used to connect to your device.
This should open the web GUI. You can find your current QOP version displayed in the top right corner of the screen.
1. Based on your OPX, refer to the flowchart below and install each intermediate version until 
you reach the desired release. 

!!! Note
    Please allow the booting process to finish before updating to a different QOP version

=== "OPX1000"

    {{ requirement("QOP", "3.0") }}

    ![QOP_Versions_Flowchart](assets/QOP_Upgrade_flowchart_3.x.x.png)

    === "{{ requirement("QOP", "3.2.4") }} and below"
        1. In the web GUI, navigate to `Preferences > Versions`.
        1. Click the blue `Upload` button and follow the on-screen instructions to upload the desired QOP package.
        1. Once the version is uploaded, select the target cluster (if applicable) from the drop-down menu.
        1. Hover over the newly uploaded version and click `Install`.
    
    === "{{ requirement("QOP", "3.3.0") }} and above"
        Before installing the desired QOP package, ensure that you have a compatible version of QOPA as shown in the flowchart. If not, please update the QOPA version before proceeding to install QOP package. 

        === "QOPA"
            1. In the web GUI, navigate to `Preferences > QOPA`.
            1. Click the blue `Upload` button and follow the on-screen instructions to upload the desired QOPA package. Please make sure you have installed the QOPA version that is compatible with the QOP version. 
            1. Once the version is uploaded, select the target cluster (if applicable) from the drop-down menu.
            1. Hover over the newly uploaded version and click `Install`.

        === "QOP"
            1. In the web GUI, navigate to `Preferences > QOP`.
            1. Click the blue `Upload` button and follow the on-screen instructions to upload the desired QOP package. Please make sure you have installed the QOPA version that is compatible with the QOP version. 
            1. Once the version is uploaded, select the target cluster (if applicable) from the drop-down menu.
            1. Hover over the newly uploaded version and click `Install`.



=== "OPX+"
    
    === "QOP>=2.5.0"
        ![QOP_Versions_Flowchart](assets/QOP_Upgrade_flowchart_250_and_above.png)
        
        1. In the web GUI, navigate to `Preferences > QOPA`
        1. Click the blue `Upload` button and follow the on-screen instructions to upload the desired QOPA package.
        1. Once the version is uploaded, select the target cluster from the drop-down menu.
        1. Hover over the newly uploaded version and click `Install`.
        1. Once the QOPA update is finished, navigate to `Preferences > QOP`
        1. Click the blue `Upload` button and follow the on-screen instructions to upload the desired QOP package.
        1. Once the version is uploaded, select the target cluster from the drop-down menu.
        1. Hover over the newly uploaded version and click `Install`.

            !!! Note "Important note"
                For the best performance, please make sure to update the QOPA version to the latest one.
    
    === "QOP<=2.4.4"
                
        ![QOP_Versions_Flowchart](assets/QOP_Upgrade_flowchart_244_and_below.png)
    
        1. In the web GUI, navigate to `Preferences > Versions`.
        1. Click the blue `Upload` button and follow the on-screen instructions to upload the desired QOP package.
        1. Once the version is uploaded, select the target cluster from the drop-down menu.
        1. Hover over the newly uploaded version and click `Install`.

!!! Note "Important notes"
    - The exact steps may vary slightly depending on your QOP Admin (QOPA) version.
    - Some versions may not display a progress bar during installation.
    - After installation is complete, press `Ctrl + F5` to refresh the page and clear the cache.
    - If any step fails, try repeating it a few times. If the issue persists, please contact QM support for assistance.
