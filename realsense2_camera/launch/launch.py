from launch                            import LaunchDescription
from launch.actions                    import (DeclareLaunchArgument,
                                               OpaqueFunction, GroupAction)
from launch.substitutions              import (LaunchConfiguration,
                                               PathJoinSubstitution,
                                               EqualsSubstitution)
from launch.conditions                 import IfCondition, UnlessCondition
from launch_ros.substitutions          import FindPackageShare
from launch_ros.actions                import Node, LoadComposableNodes
from launch_ros.descriptions           import ComposableNode
from launch_ros.parameter_descriptions import ParameterFile

launch_arguments = [
    {
        'name':        'namespace',
        'default':     '',
        'description': 'namespace of the camera node'
    },
    {
        'name':        'camera_name',
        'default':     'realsense',
        'description': 'node name of the camera'
    },
    {
        'name':        'serial_no',
        'default':     '""',
        'description': 'unique serial number of the camera'
    },
    {
        'name':        'param_file',
        'default':     PathJoinSubstitution([
                           FindPackageShare('realsense2_camera'), 'config',
                           'default.yaml']),
        'description': 'path to YAML file for configuring camera'
    },
    {
        'name':        'external_container',
        'default':     'false',
        'description': 'use existing external container',
        'choices':     ['true', 'false', 'True', 'False']
    },
    {
        'name':        'container',
        'default':     '',
        'description': 'name of internal or external component container'},
    {
        'name':        'log_level',
        'default':     'info',
        'description': 'debug log level',
        'choices':     ['debug', 'info', 'warn', 'error', 'fatal']
    },
    {
        'name':        'output',
        'default':     'screen',
        'description': 'pipe node output',
        'choices':     ['screen', 'log', 'both']
    }
]

def declare_launch_arguments(args):
    return [DeclareLaunchArgument(arg['name'],
                                  default_value=arg.get('default'),
                                  description=arg.get('description'),
                                  choices=arg.get('choices')) \
            for arg in args]

def launch_setup(context):
    param_file = ParameterFile(LaunchConfiguration('param_file'),
                               allow_substs=True)
    return [
        Node(namespace=LaunchConfiguration('namespace'),
             name=LaunchConfiguration('camera_name'),
             package='realsense2_camera',
             executable='realsense2_camera_node',
             parameters=[param_file],
             output=LaunchConfiguration('output'),
             arguments=['--ros-args', '--log-level',
                        LaunchConfiguration('log_level')],
             emulate_tty=True,
             condition=IfCondition(
                           EqualsSubstitution(
                               LaunchConfiguration('container'), ''))),
        GroupAction(
            condition=UnlessCondition(
                          EqualsSubstitution(
                              LaunchConfiguration('container'), '')),
            actions=[
                Node(name=LaunchConfiguration('container'),
                     package='rclcpp_components',
                     executable='component_container_mt',
                     output=LaunchConfiguration('output'),
                     arguments=['--ros-args', '--log-level',
                                LaunchConfiguration('log_level')],
                     condition=UnlessCondition(
                                   LaunchConfiguration('external_container'))),
                LoadComposableNodes(
                    target_container=LaunchConfiguration('container'),
                    composable_node_descriptions=[
                        ComposableNode(
                            namespace=LaunchConfiguration('namespace'),
                            name=LaunchConfiguration('camera_name'),
                            package='realsense2_camera',
                            plugin='realsense2_camera::RealSenseNodeFactory',
                            parameters=[param_file],
                            extra_arguments=[{'use_intra_process_comms': True}]
                        )
                    ])
            ]),
    ]

def generate_launch_description():
    return LaunchDescription(declare_launch_arguments(launch_arguments) + \
                             [OpaqueFunction(function=launch_setup)])
