#!/usr/bin/env python3
#
# script to generate camera urdf from yaml file

import yaml
import argparse


def cameras_to_urdf(cameras, global_link='map', robot_name='cameras'):
    body_size = (0.05, 0.05, 0.05)
    #body_size = (0.01, 0.05, 0.05)
    lens_r = 0.025
    lens_l = 0.04
    alpha = 0.8
    colors = ({"red":      (0.8, 0,   0)},
              {"green":    (0,   0.8, 0)},
              {"blue":     (0,   0.0, 0.8)},
              {"yellow":   (0.6, 0.6, 0)},
              {"purple":   (0.8, 0.0, 0.8)},
              {"cyan":     (0.0, 0.8, 0.8)},
              {"grayblue": (0.4, 0.4, 0.8)},
              {"pink":     (0.8, 0.4, 0.5)})
    print("<?xml version=\"1.0\" encoding=\"utf-8\"?>")
    print("<robot name=\"%s\">" % robot_name)
    print("  <link name=\"%s\"/>" % global_link)
    col_num = 0
    for cam_name, cam in cameras.items():
        col = colors[col_num]
        col_name = list(col.keys())[0]
        print("  <material name=\"%s\">" % col_name)
        print("    <color rgba=\"%f %f %f %f\"/>" % tuple(list(col[col_name]) + [alpha]))
        print("  </material>")
        print("  <link name=\"%s\">" % cam_name)
        # -------- camera body -------
        print("    <visual>")
        print("     <origin xyz=\"0 0 %f\" rpy=\"0 0 0\"/>" \
            % (-0.5*(body_size[2]+lens_l)))
        print("     <geometry> <box size=\"%f %f %f\"/></geometry>" % body_size)
        print("     <material name=\"%s\"/>" % col_name)
        print("    </visual>")
        # -------- camera lens -------
        print("    <visual>")
        print("     <material name=\"%s\"/>" % col_name)
        print("      <geometry>")
        print("        <cylinder length=\"%f\" radius=\"%f\"/>" % (lens_l,lens_r))
        print("      </geometry>")
        print("      <origin xyz=\"0 0 0\" rpy=\"0 0 0\"/>")
        print("    </visual>")
        print("  </link>")
        # -------- joint -----
        print("  <joint name=\"%s_to_world\" type=\"fixed\">" % cam_name)
        print("    <parent link=\"%s\"/>" % global_link)
        print("    <child link=\"%s\"/>" % cam_name)
        print("  </joint>")
        col_num = (col_num + 1) % len(colors)
    print("</robot>")


def read_yaml(filename):
    with open(filename, 'r') as y:
        try:
            return yaml.safe_load(y)
        except yaml.YAMLError as e:
            print(e)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='make tag urdf from yaml file.')
    parser.add_argument('--file',  action='store',
                        required=True, help='yaml input file')
    args = parser.parse_args()
    cams = read_yaml(args.file)
    cameras_to_urdf(cams)
