import os

from ament_index_python import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription

from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch.substitutions import LaunchConfiguration
from launch.substitutions import TextSubstitution

from launch.conditions import IfCondition

from launch_ros.actions import Node


def generate_launch_description():
  ld = LaunchDescription()

  # Declare the launch arguments
  realsense_arg = DeclareLaunchArgument(
    name='realsense',
    default_value='true',
    description='Whether to start the realsense camera driver',
    choices=['true', 'false']
  )

  webapp_arg = DeclareLaunchArgument(
    name='webapp',
    default_value='false',  # Change to true when webapp is ported to ROS2
    description='Whether to start the webapp',
    choices=['true', 'false']
  )

  # Specify the actions
  robotont_driver_node = Node(
    package='robotont_driver',
    executable='driver_node',
    name='robotont_driver_node',
    output='screen'
  )

  joint_state_publisher_node = Node(
    package='joint_state_publisher',
    executable='joint_state_publisher',
    name='joint_state_publisher_node',
    output='screen'
  )

  robot_state_publisher_node = Node(
    package='robot_state_publisher',
    executable='robot_state_publisher',
    name='robot_state_publisher_node',
    output='screen'
  )

  should_launch_realsense = LaunchConfiguration('realsense')


  realsense_include = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
      os.path.join(
        get_package_share_directory('realsense2_camera'),
        'launch/rs_launch.py'
      )
    ),
    launch_arguments={
      'camera_namespace': '',
      'camera_name': 'camera',
      'align_depth.enable': 'true',
      'unite_imu_method': '1',
      'enable_accel': 'True',
      'enable_gyro': 'True'
    }.items(),
    condition=IfCondition(should_launch_realsense)
  )

  depthimage_to_laserscan_include = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
      os.path.join(
        get_package_share_directory('depthimage_to_laserscan'),
        'launch/depthimage_to_laserscan-launch.py'
      )
    ),
    condition=IfCondition(should_launch_realsense)
  )

  laserscan_to_ranges_node = Node(
    package='laserscan_to_ranges',
    executable='laserscan_to_ranges',
    name='laserscan_to_ranges_node',
    output='screen',
    condition=IfCondition(should_launch_realsense)
  )

  # Set realsense compressedDepth png level to 5
  realsense_param = {
    '/camera/aligned_depth_to_color/image_raw/compressedDepth/png_level': 5
  }

  # Load the robot description
  upload_description = Node(
    package='robotont_description',
    executable='upload_description',
    name='upload_description',
    output='screen'
  )


  # Add the actions to the launch description
  ld.add_action(realsense_arg)
  ld.add_action(webapp_arg)
  ld.add_action(realsense_include)
  ld.add_action(robotont_driver_node)
  ld.add_action(depthimage_to_laserscan_include)
  ld.add_action(laserscan_to_ranges_node)
  #ld.add_action(joint_state_publisher_node)
  #ld.add_action(robot_state_publisher_node)

  return ld



# TODO: Add the following to the launch file
# * robotont_nuc_description/launch/upload_description.launch
# * robotont_support/launch/cam_throttling.launch
# * robotont_webapp/launch/webapp.launch
# * tf_prefix for realsense camera
