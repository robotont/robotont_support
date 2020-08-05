# robotont\_support
Package for maintaining bring-up and configuration files

[![Build Status](https://travis-ci.org/robotont/robotont_support.svg?branch=melodic-devel)](https://travis-ci.org/robotont/robotont_support)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

This package is used as a single entry point to run the most important Robotont nodes in background. The files are designed to be automatically launched when the robot is started and are called from systemd services located in ```/lib/systemd/system/```.

* To use the full capability of the robot, run:

```bash
roslaunch robotont_support robotont_bringup.launch
```
This command will start robotont driver along with the realsense 3D camera driver, loads robot description to the parameter server, and starts state publishers.


* If you do not need the realsense camera, you can save the battery by running:

```bash
roslaunch robotont_support robotont_bringup.launch realsense:=false
```
