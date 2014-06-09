#!/usr/bin/env python

import os
import sys
import rosbag
import argparse
import tf
import numpy
from geometry_msgs.msg import PointStamped, Pose, Point, Quaternion, Transform, Vector3

def xyz_to_mat44(pos):
    return tf.transformations.translation_matrix((pos.x, pos.y, pos.z))

def xyzw_to_mat44(ori):
    return tf.transformations.quaternion_matrix((ori.x, ori.y, ori.z, ori.w))

def transform(initial, position, orientation):
    xyz = xyz_to_mat44(initial.position)
    q = xyzw_to_mat44(initial.orientation)
    mat44 = numpy.dot(xyz, q)
    mat44 = tf.transformations.inverse_matrix(mat44)
    pose44 = numpy.dot(xyz_to_mat44(position), xyzw_to_mat44(orientation))
    txpose = numpy.dot(mat44, pose44)
    xyz = tuple(tf.transformations.translation_from_matrix(txpose))[:3]
    quat = tuple(tf.transformations.quaternion_from_matrix(txpose))

    return Pose(Point(*xyz), Quaternion(*quat))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("in_bag")
    parser.add_argument("out_bag")
    args = parser.parse_args()

    if os.path.exists(args.out_bag):
        print "Output bag %s already exists; refusing to overwrite it" % (args.out_bag)
        sys.exit(0)

    bag = rosbag.Bag(args.in_bag)
    out_bag = rosbag.Bag(args.out_bag, 'w')
    initial_pose = None

    for topic, msg, t in bag.read_messages():
        if topic == '/odom':
            if not initial_pose:
                initial_pose = Pose(msg.pose.pose.position, msg.pose.pose.orientation)
            out = msg
            out.pose.pose = transform(initial_pose, out.pose.pose.position,
                    out.pose.pose.orientation)
            out_bag.write('/odom', out, t)
        elif topic == '/tf':
            for trans in msg.transforms:
                if trans.header.frame_id == 'odom' and trans.child_frame_id == 'base_link':
                    if initial_pose:
                        pose = transform(initial_pose,
                                trans.transform.translation,
                                trans.transform.rotation)
                        trans.transform.translation.x = pose.position.x
                        trans.transform.translation.y = pose.position.y
                        trans.transform.translation.z = pose.position.z
                        trans.transform.rotation = pose.orientation
            out_bag.write(topic, msg, t)
        else:
            out_bag.write(topic, msg, t)

    bag.close()
    out_bag.close()

if __name__ == '__main__':
    main()
