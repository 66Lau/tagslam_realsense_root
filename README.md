# The modified version of TagSlam
---
## Introduction  


---
### TagSlam

TagSlam环境配置见原作者文档  
仓库 https://github.com/berndpfrommer/tagslam_root  
docs https://berndpfrommer.github.io/tagslam_web



**复现1**  

``` shell
#注意roscore
#terminal1
rosparam set use_sim_time true
roslaunch tagslam tagslam.launch run_online:=true
#terminal2
roslaunch tagslam apriltag_detector_node.launch
#terminal3
rviz -d `rospack find tagslam`/example/tagslam_example.rviz &
#terminal4
rosbag play --clock `rospack find tagslam`/example/example.bag --topics /pg_17274483/image_raw/compressed
```


**复现2**
``` shell

#terminal1
roscore
#terminal2
rosparam set use_sim_time true
roslaunch tagslam apriltag_detector_node.launch
#terminal2
rviz -d `rospack find tagslam`/example/tagslam_example.rviz &
#terminal3
rosrun tagslam_test run_single_test.bash 24
```

**tagslam.launch文件**
``` XML
<launch>
  <!-- 数组bag的目录 --> 
  <arg name="data_dir" default="$(find tagslam)/example"/>
  <!-- 初始化参数的目录 --> 
  <arg name="config_dir" default="$(arg data_dir)"/>
  <!-- tagslam.yaml --> 
  <arg name="tagslam_config_file" default="$(arg config_dir)/tagslam.yaml"/>
  <!-- cameras.yaml --> 
  <arg name="calibration_file" default="$(arg config_dir)/cameras.yaml"/>
  <!-- camera_poses.yaml --> 
  <arg name="camera_poses_file"
       default="$(arg config_dir)/camera_poses.yaml"/>

  <!-- 是否实时运行，默认为false -->   
  <arg name="run_online" default="false"/>
  <!-- 选取数据包，默认是example.bag --> 
  <arg name="bag" default="$(arg data_dir)/example.bag"/>
  <!-- 在多少张照片后停止跑bag，默认1000000 -->
  <arg name="max_number_of_frames" default="1000000"/>
  <!-- 读取bag的开始时间，默认为0，即从头开始 -->
  <arg name="start_time" default="0.0"/>
  <!-- 是否压缩画面，默认是 -->
  <arg name="has_compressed_images" default="true"/>


  <!-- 运行tagslam包的tagslam_node节点 -->
  <node pkg="tagslam" type="tagslam_node" name="tagslam" clear_params="true"
	output="screen">
    <!-- 读取cameras.yaml所有参数 -->
    <rosparam param="cameras" command="load" file="$(arg calibration_file)"/>
    <!-- 读取tagslam.yaml所有参数 -->
    <rosparam param="tagslam_config" command="load"
	      file="$(arg tagslam_config_file)"/>
    <!-- 读取camera_poses.yaml所有参数 -->    
    <rosparam param="camera_poses" command="load"
	      file="$(arg camera_poses_file)"/>
    <param name="bag_start_time" value="$(arg start_time)"/>
    <param name="bag_file" value="$(arg bag)" unless="$(arg run_online)"/>
    <param name="has_compressed_images" value="false"/>
    <param name="playback_rate" value="10.0"/>
    <param name="max_number_of_frames" value="$(arg max_number_of_frames)"/>
  </node>

</launch>
```
**使用USB串口相机实时运行tagslam**  
需自行安装usb_cam包
```shell
roslaunch tagslam tagslam_online_all.launch
```

**建图**  
实时运行检测完所有的tags之后，或者离线rosplay录制好的包之后，运行一下此命令存储此次运行的结果  
包括相机位姿记录和所有tag的信息，这些tags的信息可以被用于同一场景下一次的实时运行
```shell
rosservice call /tagslam/dump
```
建图后的tag信息存放在
/home/usr/.ros路径下的poses.yaml
![描述1](image\tagslam\edit\建图路径.png)
若下次使用tagslam需要使用上一次构建好的地图，将tagslam_root/src/tagslam/online下面的tagslam.yaml中的tags用poses.yaml中的tags替换。

**使用realsense系列双目摄像头(t265)**  
需要修改的文件：  
1. **tagslam/launch/apriltag_detector_node_t265.launch**  
这个launch文件会订阅相机图像话题并识别tags并发布tags话题，修改其中的图像话题，取决于相机，d435i和t265的双目图像话题不同，需根据设备进行修改
```XML
<remap from="~image/compressed" to="/camera/fisheye2/image_raw/compressed"/>
```

2. **tagslam/launch/tagslam_online_t265.launch**  
此文件用于tagslam的启动

```XML
<arg name="data_dir" default="$(find tagslam)/online/t265"/>
```
此处的data_dir路径指向存放了camera_poses.yaml，cameras.yaml，tagslam.yaml,tagslam_online.rviz等数据文件的路径，此处需要根据用户存放位置更改，为方便起见，建议使用不同相机设备与不同tags环境时新建一个data_dir存放数据文件

3. **tagslam/online/t265/camera.yaml**  
此文件存放了相机内参，若更换相机需要修改，其中如果使用realsense系列相机，使用下列命令查询相机出厂的参数,也可自行标定
```
rostopic echo /camera/fisheye1/camera_info
rostopic echo /camera/fisheye2/camera_info
```

4. **tagslam/online/t265/camera_poses.yaml**  
此文件存放了相机的相对于rig的坐标转换

5. **tagslam/online/t265/tagslam**  
此文件存放了tagslam的初始化数据，里面包含较多的信息和类型，请详见tagslam.yaml中的相关注释
https://berndpfrommer.github.io/tagslam_web/input_files/ 也有较为详细的解释