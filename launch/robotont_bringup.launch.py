import os
from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs):
    # Get parameter values
    namespace = LaunchConfiguration('namespace').perform(context)
    frame_prefix = LaunchConfiguration('frame_prefix').perform(context)
    generation = LaunchConfiguration('generation').perform(context)
    realsense_enabled = LaunchConfiguration('realsense').perform(context) == 'true'
    lidar_enabled = LaunchConfiguration('lidar').perform(context) == 'true'
    camera_enabled = LaunchConfiguration('camera').perform(context) == 'true'
    slam_enabled = LaunchConfiguration('slam').perform(context) == 'true'
    gamepad_conf = LaunchConfiguration('gamepad_conf').perform(context)
    
    # If frame_prefix empty, use namespace as prefix
    if not frame_prefix:
        frame_prefix = namespace

    print(f"Bringing up Robotont with generation: {generation}, namespace: '{namespace}', frame_prefix: '{frame_prefix}'")            
    nodes = []
    
    # Driver node
    nodes.append(Node(
        package='robotont_driver',
        executable='driver_node',
        name='driver',
        namespace=namespace,
        parameters=[{'frame_prefix': frame_prefix}],
        output='screen'
    ))
    
    # Generation-specific setup
    if generation == 'lite3':
        # Lite3: RPLidar + IMX500 camera + lite description
        nodes.append(IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('robotont_lite_description'), 'launch/upload_description.launch.py')
            ),
            launch_arguments={
                'namespace': namespace,
                'frame_prefix': frame_prefix+'/' if frame_prefix else '',
                'generation': generation,
                'primary_color': '0.16 0.65 0.98 1.0',
                'secondary_color': '0.0 1.0 1.0 1.0'
            }.items()
        ))
        
        if lidar_enabled:
            nodes.insert(0, Node(
                package='rplidar_ros',
                executable='rplidar_node',
                name='rplidar_node',
                namespace=namespace,
                parameters=[{
                    'channel_type': 'serial',
                    'serial_port': '/dev/lidar',
                    'serial_baudrate': 1000000,
                    'frame_id': f'{frame_prefix}/laser_link' if frame_prefix else 'laser_link',
                    'angle_compensate': True,
                    'scan_mode': 'DenseBoost'
                }],
                output='screen'
            ))
            if slam_enabled:
                nodes.append(IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(
                        os.path.join(get_package_share_directory('slam_toolbox'), 'launch', 'online_async_launch.py')
                    ),
                    launch_arguments={
                        'namespace': namespace,
                        'use_sim_time': 'false',
                        'params_file': os.path.join(get_package_share_directory('robotont_lite_description'), 'config', 'slam', 'slam_toolbox_lite3.yaml')
                    }.items()
                ))
        
        if camera_enabled:
            nodes.append(Node(
                package='camera_ros',
                executable='camera_node',
                name='camera',
                namespace=namespace,
                parameters=[{
                    'camera': 0,
                    'width': 640,
                    'height': 480,
                    'framerate': 10.0,
                    'format': 'YUYV',
                    'camera_name': 'camera',
                    'frame_id': f'{frame_prefix}/camera_link' if frame_prefix else 'camera_link'
                }],
                output='screen',
                respawn=True,
                respawn_delay=3.0,
                remappings=[
                    ('image', 'camera/image_raw'),
                    ('camera_info', 'camera/camera_info')
                ]
            ))
        
    elif generation in ['2.1', '3'] and realsense_enabled:
        # Gen 2.1/3: RealSense + depth to laserscan
        nodes.append(IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('robotont_nuc_description'), 'launch/description.launch.py')
            ),
            launch_arguments={
                'namespace': namespace,
                'frame_prefix': frame_prefix+'/' if frame_prefix else '',
                'generation': generation
            }.items()
        ))
        
        nodes.append(IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('realsense2_camera'), 'launch/rs_launch.py')
            ),
            launch_arguments={
                'camera_namespace': namespace,
                'camera_name': 'camera',
                'align_depth.enable': 'true',
                'unite_imu_method': '1',
                'enable_accel': 'true',
                'enable_gyro': 'true'
            }.items()
        ))
        
        nodes.append(IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('depthimage_to_laserscan'),
                           'launch/depthimage_to_laserscan-launch.py')
            )
        ))
    else:
        # Robot without Realsense: use a basic robotont_description
        nodes.append(IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('robotont_description'), 'launch/description.launch.py')
            ),
            launch_arguments={
                'namespace': namespace,
                'frame_prefix': frame_prefix+'/' if frame_prefix else '',
                'generation': generation
            }.items()
        ))

        
    nodes.append(Node(
        package='laserscan_to_ranges',
        executable='laserscan_to_ranges',
        name='laserscan_to_ranges',
        namespace=namespace,
        output='screen',
        parameters=[{
            'method': 'min',
            'field_of_view': 0.0,
            'angle_offset': 180.0,
            'enable_ranges': True,
            'range_frame_prefix': frame_prefix + '/range_' if frame_prefix else 'range_',
            'base_frame': frame_prefix + '/lidar_link' if frame_prefix else ''
        }],
    ))
    
    nodes.append(IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('demo_teleop'), 'launch/teleop_joy.launch.py')
        ),
        launch_arguments={
            'namespace': namespace,
            'gamepad_conf': gamepad_conf
        }.items()
    ))
    
    return nodes


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('namespace', default_value=''),
        DeclareLaunchArgument('frame_prefix', default_value=''),
        DeclareLaunchArgument('generation', default_value='3', choices=['2.1', '3', 'lite3']),
        DeclareLaunchArgument('realsense', default_value='false', choices=['true', 'false']),
        DeclareLaunchArgument('lidar', default_value='false', choices=['true', 'false']),
        DeclareLaunchArgument('camera', default_value='false', choices=['true', 'false']),
        DeclareLaunchArgument('gamepad_conf', default_value='trust.yaml'),
        DeclareLaunchArgument('slam', default_value='false', choices=['true', 'false']),
        
        # TODO: fake_hardware argument should be added to easily switch between real and fake hardware from a single bringup entrypoint
        
        OpaqueFunction(function=launch_setup)
    ])
