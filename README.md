# robotont\_support
A package for maintaining bring-up and configuration files

[![Build Status](https://travis-ci.com/robotont/robotont_support.svg?branch=melodic-devel)](https://travis-ci.com/robotont/robotont_support)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

This package is used as a single entry point for starting background nodes on Robotont's on-board computer. The files are designed to be automatically launched from systemd services located in ```/lib/systemd/system/```. You  may also use the launchers in this package to manually bring up the nodes, however before doing so, make sure that Robotont's systemd services have been stopped.

### robotont\_bringup.launch
* To use the full capability of the robot, run:

```bash
roslaunch robotont_support robotont_bringup.launch
```
This command will start robotont driver along with the Realsense 3D camera driver, loads the robot description to the parameter server, and starts state publishers.


* If you do not need the Realsense camera, you can save the battery by running only the robot driver:

```bash
roslaunch robotont_support robotont_bringup.launch realsense:=false
```

### cam\_throttling.launch

* This launch file uses throttling node from ```topic_tools``` package to create camera topics slowed down the publishing rates. This is useful when trying to transfer image/depth streams to a remote computer in limited bandwitdh conditions.

```bash
roslaunch robotont_support robotont_bringup.launch realsense:=false
```
