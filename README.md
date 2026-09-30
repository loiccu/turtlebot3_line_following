# Line and Track Following Tutorials for the TurtleBot3

*[(Version française ici)](README_fr.md)*

This repository provides **ROS 2 Humble** tutorials for the **TurtleBot3**: from a quick installation of the robot to camera-based line and track following, written in Python.

## Tutorials

1. [**Quick installation**](Quick_installation.md): set up the PC and the TurtleBot3, optionally with a ready-to-use SD card image for the Raspberry Pi.
2. [**Line and track following**](Line_track_following.md): stream the camera to the PC, detect a colored line, then follow a line or a track made of two lines (URMRC missions).

The Python scripts of the line and track following tutorial are in the [src/](src/) folder.

A PDF version of each tutorial and how-to is available in the [pdf/](pdf/) folder.

---

### Additional how-tos

- [Back up and restore the TurtleBot3 SD card](BackupRestore_SDCard.md)
- [Battery management (LiPo safety, charging, storage)](BatteryOperation.md)


### Requirements

- A TurtleBot3 Burger with a Raspberry Pi camera mounted at the front
- A PC running Ubuntu 22.04 with ROS 2 Humble
- A Wi-Fi network shared by the PC and the robot

### External resources

- Official ROS 2 Humble tutorials:
    - [Beginner: CLI Tools](https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools.html) (**strongly recommended** before starting)
    - [Beginner: Client Libraries](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries.html)
    - [Intermediate: Launch Files](https://docs.ros.org/en/humble/Tutorials/Intermediate/Launch/Launch-Main.html)
- [Autonomous driving](https://docs.robotis.com/docs/systems/turtlebot3/autonomous_driving/) in the Robotis manual: resources and ROS 2 Humble code for missions close to the URMRC missions.
    - Associated repository: [ROBOTIS-GIT/turtlebot3_autorace](https://github.com/ROBOTIS-GIT/turtlebot3_autorace)
- Any tutorial or course on the basics of the Linux command line

---

### License

This work is licensed under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/): you may share and adapt it for any purpose, provided you give appropriate credit (Loïc Cuvillon), link to the license and indicate if changes were made. See the [LICENSE](LICENSE) file for the full text.

Exception: the HSV color space image ([assets/HSV.png](assets/HSV.png)) is not covered by this license; all rights remain with its authors.
