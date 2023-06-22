#!/usr/bin/env python
import rospy
import sys
import argparse
import yaml
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Quaternion, Pose, Point, Vector3
from std_msgs.msg import Header, ColorRGBA

def get_node_name(rosargs):
    for r in rosargs:
        s = r.split(':=')
        if len(s) > 1 and s[0] == '__name':
            return s[1]
    return None

def make_text_marker(text, pose, scale, frame_id, id):
    marker = Marker(
        type = Marker.TEXT_VIEW_FACING,
        id = id,
        lifetime = rospy.Duration(1000.5),
        pose     = pose,
        scale    = Vector3(scale, scale, scale),
        header   = Header(frame_id=frame_id),
        color    = ColorRGBA(0.0, 0.0, 0.0, 1.0),
        text     = text)
    return marker
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='publish text markers files')
    parser.add_argument('--topic', '-t', action='store', default="text_labels",
                        help='topic to publish marker array under.')
    parser.add_argument('fname', help='yaml file with text labels')
    parser.add_argument('world_frame')
    parser.add_argument('ros_args', metavar='r', nargs='+',
                        help='ros arguments')
    args = parser.parse_args()
    rospy.init_node(get_node_name(args.ros_args))

    fname       = args.fname
    world_frame = args.world_frame
    rospy.loginfo('publishing text from %s' % (fname))
                                
    marker_publisher = rospy.Publisher(args.topic, MarkerArray, queue_size=2, latch=True)
    params = yaml.load(open(fname, 'r'))
    arr = MarkerArray()
    id = 0
    for marker in params['markers']:
        text = marker["text"]
        scale = marker["scale"]
        T = marker["transform"]["translation"]
        q = marker["transform"]["rotation"]
        pose = Pose(Point(T['x'],T['y'],T['z']),
                    Quaternion(q['x'],q['y'],q['z'],q['w']))
        frame = marker["frame_id"] if "frame_id" in marker else args.world_frame
        arr.markers.append(make_text_marker(text, pose, scale, frame, id))
        id = id + 1
    marker_publisher.publish(arr)
    # infinite loop
    rospy.spin()
