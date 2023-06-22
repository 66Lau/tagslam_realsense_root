#!/usr/bin/env python3
#
# script to generate tag urdf from yaml file

import yaml
import argparse


def tags_to_urdf(tags, mesh_dir='package://tagslam_viz/tags', tag_fam='36_11',
                 global_link='map', robot_name='tags', tag_thick=0.005):
    print("<?xml version=\"1.0\" encoding=\"utf-8\"?>")
    print("<robot name=\"%s\">" % robot_name)
    print("<link name=\"%s\"/>" % global_link)
    for t in tags:
        sz = float(t['size'])
        tid = int(t['id'])
        print(" <link name=\"tag_%d\">" % tid)
        print("  <visual>")
        print("   <origin rpy=\"0 0 0\" xyz=\"0 0 -%f\"/>" % (sz * tag_thick))
        print("     <geometry>")
        print("       <mesh filename=\"%s/tag%s_%05d.dae\" scale=\"%f %f %f\"/>" % (
            mesh_dir, tag_fam, int(t['id']), sz, sz, sz))
        print("     </geometry>")
        print("  </visual>")
        print(" </link>")
        print(" <joint name=\"tag_%d_to_world\" type=\"fixed\">" % tid)
        print("   <parent link=\"%s\"/>" % global_link)
        print("   <child link=\"tag_%d\"/>" % tid)
        print("   <origin xyz=\"0 0 0\" rpy=\"0 0 0\"/>")
        print("   </joint>")
    print("</robot>")


def find_tags(d):
    all = []
    if type(d) is list: # it's a list (maybe bodies, must dig deeper)
        for l in d:
            all = all + find_tags(l) # recursion!
    elif type(d) is dict: # for dictionary, search for 'tags' field
        for k,v in d.items():
            if k == 'tags' and type(v) is list:
                for t in v: # found what we are looking for!
                    all = all + [{'id': t['id'], 'size': t['size']}]
            else:
                all = all + find_tags(v) # recursion!
    return all


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
    parser.add_argument('--mesh_dir', action='store',
                        required=True, help='location of mesh files')
    parser.add_argument('--family', action='store', default="36_11",
                        help='tag family, e.g. 36_11')
    args = parser.parse_args()
    y = read_yaml(args.file)
    tags = find_tags(y)
    tags_to_urdf(tags, mesh_dir=args.mesh_dir, tag_fam=args.family)
