#!/usr/bin/env python

import os
import sys
import rosbag
import argparse
from geometry_msgs.msg import PointStamped

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
    for topic, msg, t in bag.read_messages():
        if topic == '/current_goal':
            stamped = PointStamped()
            stamped.point = msg
            stamped.header.stamp = t
            stamped.header.frame_id = 'odom'
            out_bag.write('/current_goal_stamped', stamped, t)
        out_bag.write(topic, msg, t)

    bag.close()
    out_bag.close()

if __name__ == '__main__':
    main()
