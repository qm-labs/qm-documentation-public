# QOP Installation Guide 
This guide outlines the steps for installing a QOP package on either an OPX+ or OPX1000 device.

## Installation Procedure
1. Open a web browser on a computer that has network access to the device you wish to update.
1. In the address bar, enter the IP address typically used to connect to your device.
This should open the web GUI. You can find your current QOP version displayed in the top right corner of the screen.
1. Based on your QOP version, refer to the flowchart below and install each intermediate version until 
you reach the desired release.
 
    ![QOP_Versions_Flowchart](assets/QOP_Upgrade_flowchart_2.x.x.png)

1. In the web GUI, navigate to `Preferences > Versions`.
1. Click the blue `Upload` button and follow the on-screen instructions to upload the desired QOP package.
1. Once the version is uploaded, select the target cluster (if applicable) from the drop-down menu.
1. Hover over the newly uploaded version and click `Install`.

!!! Note "Important notes"
    - The exact steps may vary slightly depending on your QOP Admin (QOPA) version.
    - Some versions may not display a progress bar during installation.
    - After installation is complete, press `Ctrl + F5` to refresh the page and clear the cache.
    - If any step fails, try repeating it a few times. If the issue persists, please contact QM support for assistance.