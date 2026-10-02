# Quick Installation (with a Ready-to-Use SD Card)
by Loïc Cuvillon

*[(Version française ici)](Quick_installation_fr.md)*

This quick start guide sets up the TurtleBot3 and the PC for line following, using a camera with the `v4l2_camera` ROS package.

It follows the [official manual](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/pc_setup) to install ROS Humble, but offers a much quicker alternative to set up the TurtleBot3 Raspberry Pi (RPi): a ready-to-use SD card image.

**Contents**
1. [PC installation](#1-pc-installation)
2. [TurtleBot3 RPi installation](#2-turtlebot3-rpi-installation-sbc-and-opencr-setup)
3. [Back up the SD card](#3-back-up-the-sd-card)
4. [Basic TurtleBot3 tests](#4-basic-turtlebot3-tests)


## 1. PC installation
Follow the official Robotis quick start guide to set up a PC with Ubuntu 22.04 and ROS 2 Humble:
- [quick_start_guide/pc_setup](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/pc_setup)

> **Note:** at the corresponding step, install both ROS 2 Humble Desktop and the ROS development tools:
> ```sh
> sudo apt install ros-humble-desktop
> sudo apt install ros-dev-tools
> ```

Then install a few useful tools:
- `rpi-imager`, to write the SD card:
    ```sh
    sudo apt install rpi-imager
    ```
- `terminator`, to open several terminals in a split view:
    ```sh
    sudo apt install terminator
    ```
- `codium` (VSCodium, the open-source build of VS Code), to edit Python code:
    ```sh
    sudo snap install codium --classic
    ```
    Then run `codium` and install the Python extension (`ms-python.python`) for advanced editing, live syntax checking, debugging, etc.


## 2. TurtleBot3 RPi installation (SBC and OpenCR setup)
There are two ways to install the TurtleBot3 Raspberry Pi (the SBC, single board computer):
- [Option A](#option-a-with-a-ready-to-use-sd-card-image): write a ready-to-use SD card image (much quicker),
- [Option B](#option-b-step-by-step-with-the-robotis-manual): follow the step-by-step instructions of the Robotis manual.

### Option A: with a ready-to-use SD card image
As an alternative to building the RPi system step by step as in the Robotis manual ([quick_start_guide/sbc_setup](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/sbc_setup)), a ready-to-use SD card image is available. It has been tested for a Raspberry Pi4. It contains Ubuntu 22.04, ROS 2 Humble, the TurtleBot3 packages, the legacy camera driver and the camera tools (V4L2):

**Download:** [turtlebot3_humble_v4l2camera.img.gz](https://seafile.unistra.fr/f/882bc4b224e947a8a27d/?dl=1)

MD5 checksum: `17adbbfc7703a4f99a9bbc24980356a7  turtlebot3_humble_v4l2camera.img.gz`

#### Write the image to the SD card
1. Check that the download is not corrupted: the following command must display the checksum above.
    ```sh
    md5sum turtlebot3_humble_v4l2camera.img.gz
    ```
2. Decompress the image (about 7.5 GB once decompressed):
    ```sh
    gunzip -k turtlebot3_humble_v4l2camera.img.gz
    ```
3. Write the image to the SD card with `rpi-imager`:
    - in the Raspberry Pi Imager window, choose *Operating System* > *Use custom* and select the decompressed file `turtlebot3_humble_v4l2camera.img`,
    - choose your SD card as *Storage* and write the image,
    - no OS customization is needed.

#### Network configuration
The TurtleBot3 network (Wi-Fi or wired) is configured in the file `/etc/netplan/50-cloud-init.yaml`. It can be edited either on the TurtleBot3 itself, with a screen and a keyboard (method 1), or directly on the SD card from the PC (method 2).

##### Method 1: with an HDMI screen and a USB keyboard
- As detailed in [Configure the Raspberry Pi](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/sbc_setup#configure-the-raspberry-pi):
    - insert the SD card into the RPi,
    - connect a screen to the RPi with an HDMI cable, and connect a USB keyboard,
    - power on the TurtleBot3 (**after** connecting the HDMI cable!).
- Log in with the user `ubuntu` and the password `turtlebot`.
- The directory `/etc/netplan` contains 1 regular file and 2 hidden files:
    ```sh
    ls -A /etc/netplan
    ```
    ```
    50-cloud-init.yaml  .50-cloud-init.yaml.dhcp  .50-cloud-init.yaml.static
    ```
    The two hidden files are ready-made configurations. Copy the one you need over `50-cloud-init.yaml`, then edit it:

    - **a) DHCP**: your Wi-Fi hotspot/router has a DHCP server that automatically gives an IP address to the TurtleBot3.
        ```sh
        cd /etc/netplan
        sudo cp .50-cloud-init.yaml.dhcp 50-cloud-init.yaml
        ```
        Then edit the file: replace `c138proj` with your Wi-Fi SSID and `password_here` with your Wi-Fi password.
        ```sh
        sudo nano 50-cloud-init.yaml
        ```
    - **b) Static IP**: there is no DHCP server, or you use a wired connection (`eth0`).
        ```sh
        cd /etc/netplan
        sudo cp .50-cloud-init.yaml.static 50-cloud-init.yaml
        ```
        Then edit the file: replace `c138proj` with your Wi-Fi SSID, the password with your Wi-Fi password, and the 3 IP addresses with the ones you want for the TurtleBot3, the name server (DNS) and the gateway respectively.
        ```sh
        sudo nano 50-cloud-init.yaml
        ```
        > In YAML files, indentation matters: use spaces (not tabs) and keep the existing indentation.

- Apply the network configuration (no reboot needed):
    ```sh
    sudo netplan apply
    ```
    The following warning is normal and can be ignored: `WARNING:root:Cannot call Open vSwitch: ovsdb-server.service is not running.`

- Troubleshooting:
    - `ip a` displays the current IP configuration of the Wi-Fi (`wlan0`) and wired (`eth0`) interfaces,
    - `sudo netplan --debug apply` displays debug information.

##### Method 2: directly on the SD card, from the PC (no screen or keyboard needed)
A screen and a keyboard may still be needed to debug a failed network connection.
- Insert the SD card (with the image already written) into the Ubuntu PC. Its partitions are mounted automatically, usually in `/media/<your_PC_user>/`.
- In the `writable` partition, edit the file `etc/netplan/50-cloud-init.yaml` as detailed in [method 1](#method-1-with-an-hdmi-screen-and-a-usb-keyboard) (copy the DHCP or static configuration, then edit the SSID, password and IP addresses):
    ```sh
    cd /media/$USER/writable/etc/netplan
    ```
    then use the same `sudo cp` and `sudo nano` commands as in method 1.
- Eject the SD card, insert it into the TurtleBot3 and power it on.

#### Connect remotely to the TurtleBot3
Connect from a terminal on the PC to the TurtleBot3 through the network, as described in [quick_start_guide/bringup](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/bringup):

1. On the PC, check that the TurtleBot3 RPi is online:
    ```sh
    ping 192.168.1.45
    ```
    where `192.168.1.45` has to be replaced with the static IP address you gave to the TurtleBot3, or with the dynamic IP address assigned by your router/hotspot (it can be found in the router web interface, or with `ip a` on the TurtleBot3 with a screen connected).
    If the TurtleBot3 is connected to the network, the round-trip time of each packet is displayed. Stop `ping` with `Ctrl+C`.

2. On the PC, connect remotely to the TurtleBot3:
    ```sh
    ssh ubuntu@192.168.1.45
    ```
    Replace `192.168.1.45` with the TurtleBot3 IP address, and `ubuntu` with the user you created if you built the SD card yourself.
3. When prompted, enter the user password of the TurtleBot3 (`turtlebot` for the ready-to-use image).

#### Update the ROS 2 repository key
The signing key of the ROS 2 package repositories changes from time to time. If `sudo apt update` reports a `NO_PUBKEY` or `EXPKEYSIG` error for `packages.ros.org`, update the key on the RPi with:
```sh
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
sudo apt update
```

#### OpenCR firmware update (if required)
- The latest firmware (at the time the image was built) and an update script are already installed on the SD card.
    - Run the OpenCR firmware update on the RPi:
        ```sh
        cd ~/opencr
        bash update_opencr.bash
        ```
        Note: the script needs an Internet connection to install software packages.
    - When asked which daemons to restart, just select *OK*.
    - About 20 seconds after the end of the update, the OpenCR board should play a short melody to confirm the update.
- If you have any trouble, see the official page: [quick_start_guide/opencr_setup](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/opencr_setup).

#### .bashrc
The `~/.bashrc` file of the TurtleBot3 is already configured as expected by the manual:
```bash
source /opt/ros/humble/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export ROS_DOMAIN_ID=30 #TURTLEBOT3
export LDS_MODEL=LDS-01
export TURTLEBOT3_MODEL=burger
```
If your LiDAR model is not `LDS-01`, replace it with `LDS-02` or `LDS-03`. Then reload the file with `source ~/.bashrc` (or open a new terminal).

> **Important:** the PC must use the same `ROS_DOMAIN_ID` (30) as the TurtleBot3, otherwise they cannot communicate. The PC setup of the manual adds `export ROS_DOMAIN_ID=30 #TURTLEBOT3` to the `~/.bashrc` of the PC.

### Option B: step by step with the Robotis manual
- Install Ubuntu and ROS 2 Humble on the SBC, choosing the `v4l2_camera` package method for the RPi camera:
    - [quick_start_guide/sbc_setup](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/sbc_setup) (see the *Raspberry Pi Camera* section),
    - if `rqt_image_view` is not available when testing the camera, use `rqt -s image_view`.
- Install the OpenCR firmware:
    - [quick_start_guide/opencr_setup](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/opencr_setup).


## 3. Back up the SD card
It is highly recommended to back up the content of your SD card once the installation is complete.
See how to do it in [BackupRestore_SDCard.md](BackupRestore_SDCard.md).


## 4. Basic TurtleBot3 tests
Test the communication between the PC and the TurtleBot3, and the ROS 2 environment, with the basic teleoperation of the manual:
- [Bringup](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/bringup)
- [Teleoperation (keyboard)](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/teleoperation)

> **Tip:** to avoid typing `export TURTLEBOT3_MODEL=burger` in every new terminal on the PC, add this line at the end of the PC `~/.bashrc` file, as on the TurtleBot3 ([quick_start_guide/export_turtlebot3_model](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/export_turtlebot3_model)).

Troubleshooting:
- check that the PC and the TurtleBot3 **both** use the same `ROS_DOMAIN_ID` (run this in a terminal on each of them):
    ```sh
    echo $ROS_DOMAIN_ID
    ```
- check that the PC and the TurtleBot3 are on the same network (see [Connect remotely to the TurtleBot3](#connect-remotely-to-the-turtlebot3)),
- check that the motors and the OpenCR board work correctly: [OpenCR test](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/opencr_setup#opencr-test),
- reboot the TurtleBot3.
