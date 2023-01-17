# robotont\_support
A package for maintaining bring-up and configuration files

[![Build Status](https://travis-ci.com/robotont/robotont_support.svg?branch=melodic-devel)](https://travis-ci.com/robotont/robotont_support)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

This package is used as a single entry point for starting background nodes on Robotont's on-board computer. The files are designed to be automatically launched from systemd services located in ```/lib/systemd/system/```. You  may also use the launchers in this package to manually bring up the nodes, however before doing so, make sure that Robotont's systemd services have been stopped.

### robotont\_bringup.launch

To use the full capability of the robot, run:

```bash
roslaunch robotont_support robotont_bringup.launch
```
This command will perform the following actions:
* start the [robotont driver](https://github.com/robotont/robotont_driver)
* start the [Realsense 3D camera driver](https://github.com/IntelRealSense/realsense-ros)
* serve the robotont [web application](https://github.com/robotont/robotont_webapp)
* load the [robot description](https://github.com/robotont/robotont_nuc_description) to the parameter server
* start the state publishers.


You can control whether the Realsense camera and the web application are started with the following arguments:

```bash
roslaunch robotont_support robotont_bringup.launch realsense:=false webapp:=false
```

### cam\_throttling.launch

This launch file uses throttling node from ```topic_tools``` package to create additional ```..._throttled``` depth camera topics with slowed down publishing rates. Throttling becomes useful when trying to transfer image/depth streams to a remote computer in limited bandwitdh conditions. Use the ```cam_fps``` argument to set the desired publishing rate for the throttled topics.

```bash
roslaunch robotont_support cam_throttling.launch cam_fps:=5
```
