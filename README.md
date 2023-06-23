# The modified version of TagSlam

## Introduction    
the modified version of [TagSlam](https://github.com/berndpfrommer/tagslam ) which supports the realsense cameras and could run in online mode easily

---
### TagSlam

TagSlam环境配置与依赖见原作者文档  
仓库： https://github.com/berndpfrommer/tagslam_root  
docs： https://berndpfrommer.github.io/tagslam_web

---

## 1.实时运行TagSlam

实时运行TagSlam时，注意地图中需要有一个Tag36H11家族的id为0的Tag作为map的原点，其他Tag程序会根据相对0号tag的位置自动解算，程序中默认所有新发现的tag的大小暂时为4cm，如需要更改尺寸，请在tagslam/online下面的tagslam.yaml进行修改

程序可以实时识别tags（即使是没有在tagslam.yaml下声明的tag），并且会根据画面中所有tags的图像信息和姿态信息确定相机的坐标和姿态，同时也会储存地图中的所有tag的坐标信息，如果是tagslam.yaml下声明的tag，则这些tag的位姿是确定的，而实时发现的新的tag的位姿则可能会变化（相机识别可能导致这些tag的位姿有误差），注意不要出现两张一样的id的tag

**使用USB串口相机实时运行tagslam（需自行安装usb_cam包）**  

```shell
roslaunch tagslam tagslam_online_usbcam_all.launch
```

**使用T265（双目）实时运行tagslam**  

```shell
roslaunch tagslam tagslam_online_t265_all.launch
```

**使用D435i（infrared双目）实时运行tagslam**  

```shell
roslaunch tagslam tagslam_online_d435_infrared_all.launch
```

**使用D435i（rgb相机）实时运行tagslam**  

```shell
roslaunch tagslam tagslam_online_d435_rgb_all.launch
```
---

## 2.建图TagSlam
实时运行检测完所有的tags之后，或者离线rosplay录制好的包之后，在新的终端运行一下此命令存储此次运行的结果  
包括相机位姿记录和所有tag的信息，这些tags的信息可以被用于同一场景下一次的实时运行
```shell
rosservice call /tagslam/dump
```
建图后的tag信息存放在
/home/usr/.ros路径下的poses.yaml
![描述1](image\tagslam\edit\建图路径.png)
若下次使用tagslam需要使用上一次构建好的地图，将tagslam_root/src/tagslam/online下面不同相机的tagslam.yaml中的tags用poses.yaml中的tags替换。

---
## 3.相机和各个input file的配置流程
如果需要使用t265，d435i，usb相机以外的相机，在tagslam/online中新建一个所需使用相机的文件夹，其中存放
```
│  cameras.yaml (相机内参)
│  camera_poses.yaml (相机相对机器人支架rig的坐标变换，默认无平移旋转)
│  tagslam.yaml (tagslam初始化参数和tag的地图信息)
│  tagslam_online.rviz (rviz配置)
```
同时需要在tagslam/launch中新建3个launch文件   
```
│  apriltag_detector_node_相机名.launch(tags识别节点)
│  tagslam_online_相机名.launch（实时tagslam节点）
│  tagslam_online_相机名_all.launch（包括rviz在内的所有启动文件集合）
```
需要修改的文件（以t265为例，实际请替换成你的相机的名字）：  
1. **tagslam/launch/apriltag_detector_node_t265.launch**  
这个launch文件会订阅相机图像话题并识别tags并发布tags话题，修改其中的图像话题，取决于相机发布的话题，需根据设备进行修改，以下代码以t265为例
```XML
<remap from="~image/compressed" to="/camera/fisheye2/image_raw/compressed"/>
```

2. **tagslam/launch/tagslam_online_t265.launch**  
此文件用于tagslam的启动  
此处的data_dir路径指向存放了camera_poses.yaml，cameras.yaml，tagslam.yaml,tagslam_online.rviz等数据文件的文件夹路径
```XML
<arg name="data_dir" default="$(find tagslam)/online/t265"/>
```

3. **tagslam/launch/tagslam_online_t265_all.launch**  
此文件调用所有的launch文件
```XML
<launch>
    <!--此处是你的相机的启动文件  -->
    <include file="$(find realsense2_camera)/launch/demo_d435.launch">
    </include>
    <!--此处是你的tagslam的启动文件  -->
    <include file="$(find tagslam)/launch/tagslam_online_d435_rgb.launch">
        <arg name="run_online" value="true"/>
    </include>
    <!--此处是你的apriltag识别的启动文件  -->
    <include file="$(find tagslam)/launch/apriltag_detector_node_d435_rgb.launch">
    </include>
    <!--rviz可视化  -->
    <node name="tagslam_example_rviz" pkg="rviz" type="rviz" args="-d $(find tagslam)/online/d435_rgb/tagslam_online.rviz" required="true" />


</launch>

```

4. **tagslam/online/t265/camera.yaml**  
此文件存放了相机内参，若更换相机需要修改，其中如果使用realsense系列相机，使用下列命令查询相机出厂的参数,也可自行标定
```
rostopic echo /camera/fisheye1/camera_info
rostopic echo /camera/fisheye2/camera_info

# 或者进入realsense-viewer查看更加详细的内外参数
realsense-viewer
rs-enumerate-devices -c
```

5. **tagslam/online/t265/camera_poses.yaml**  
此文件存放了相机的相对于rig的坐标转换,一般默认以下值即可，即使有多个摄像机，只需要声明其中一个的位姿即可，大部分情况下不需要修改此文件
```
cam0:
  pose:
    position:
      x: 0
      y: 0
      z: 0
    rotation:
      x: 0
      y: 0
      z: 0
    R:
      [ 1000000.00000000, 0.00000000, 0.00000000, 0.00000000, 0.00000000, 0.00000000, 
        0.00000000, 1000000.00000000, 0.00000000, 0.00000000, 0.00000000, 0.00000000, 
        0.00000000, 0.00000000, 1000000.00000000, 0.00000000, 0.00000000, 0.00000000, 
        0.00000000, 0.00000000, 0.00000000, 1000000.00000000, 0.00000000, 0.00000000, 
        0.00000000, 0.00000000, 0.00000000, 0.00000000, 1000000.00000000, 0.00000000, 
        0.00000000, 0.00000000, 0.00000000, 0.00000000, 0.00000000, 1000000.00000000 ]
```

6. **tagslam/online/t265/tagslam.yaml**  
此文件存放了tagslam的初始化数据，里面包含较多的信息和类型，请详见tagslam.yaml中的相关注释
https://berndpfrommer.github.io/tagslam_web/input_files/ 也有较为详细的解释
特别注意其中的tags，即代表了地图中的tag的坐标和位姿，如果需要使用此前实时建图得到的tags信息，将.ros/poses.yaml中的tags替换掉tagslam.yaml中的tags即可