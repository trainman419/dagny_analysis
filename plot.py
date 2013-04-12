#!/usr/bin/env python

import os
import sys

from pylab import *

from utm import latlong2utm


def get_gps(data_dir):
    gps_file = os.path.join(data_dir, 'gps.csv')

    if not os.path.exists(gps_file):
        sys.exit('no ' + gps_file)
    with open(gps_file) as f:
        raw = f.read()
    for x in raw.splitlines()[:5]:
        print(x)
    time = []
    lat = []
    lng = []
    for x in raw.splitlines()[1:]:
        x = x.split(',')
        time.append(float(x[0]))
        lat.append(float(x[1]))
        lng.append(float(x[2]))
    for i, x in enumerate(lat):
        if i == 0:
            continue
        if abs(lat[i-1] - x) > 10:
            print(i)
            del lat[i]
            del lng[i]
            del time[i]
    for i, x in enumerate(lng):
        if i == 0:
            continue
        if abs(lng[i-1] - x) > 10:
            print(i)
            del lat[i]
            del lng[i]
            del time[i]
    #subplot(211)
    #plot(time, lat)
    #subplot(212)
    #plot(time, lng)
    #show()
    utmx = []
    utmy = []
    for lati, lngi in zip(lat, lng):
        x, y = latlong2utm(lati, lngi)
        utmx.append(x)
        utmy.append(y)
    return time, utmx, utmy

def get_odom(data_dir):
    odom_file = os.path.join(data_dir, 'odom.csv')

    if not os.path.exists(odom_file):
        sys.exit('no ' + odom_file)
    with open(odom_file) as f:
        raw = f.read()
    for x in raw.splitlines()[:5]:
        print(x)
    time = []
    pos_x = []
    pos_y = []
    orientation = []
    for x in raw.splitlines()[1:]:
        x = x.split(',')
        time.append(float(x[0]))
        pos_x.append(float(x[7]))
        pos_y.append(float(x[8]))

    #subplot(211)
    #plot(time, pos_x)
    #subplot(212)
    #plot(time, pos_y)
    #show()

    return time, pos_x, pos_y

def main():
    if len(sys.argv) != 2:
        print "Usage: plot.py <dir>"
        sys.exit(1)

    data_dir = sys.argv[1]

    gps_time, utmx, utmy = get_gps(data_dir) or [None, None, None]
    odom_time, odom_x, odom_y = get_odom(data_dir)

    utmx_filt = [x - utmx[0] for x in utmx]
    utmy_filt = [y - utmy[0] for y in utmy]

    odom_x_filt = [x - odom_x[0] for x in odom_x]
    odom_y_filt = [y - odom_y[0] for y in odom_y]

    min_time = min(odom_time[0], gps_time[0])
    max_time = max(odom_time[-1], gps_time[-1])
    total_time = max_time - min_time

    odom_color = [(t - min_time)/total_time for t in odom_time]
    gps_color = [(t - min_time)/total_time for t in gps_time]
    print odom_color

    for i, x in enumerate(utmx_filt):
        if i == 0:
            continue
        if abs(utmx_filt[i-1] - x) > 10:
            print('x', i)
            del utmx_filt[i]
            del utmy_filt[i]
            del gps_time[i]
    for i, x in enumerate(utmy_filt):
        if i == 0:
            continue
        if abs(utmy_filt[i-1] - x) > 10:
            print('y', i)
            del utmx_filt[i]
            del utmy_filt[i]
            del gps_time[i]
    # subplot(311)
    # plot(time, utmx_filt)
    # subplot(312)
    # plot(time, utmy_filt)
    # subplot(313)
    print(len(gps_time))
    axis('equal')
    scatter(utmx_filt, utmy_filt, c=gps_color)
    #plot(utmx_filt, utmy_filt, c=gps_color)
    scatter(odom_x_filt, odom_y_filt, c=odom_color)
    show()


if __name__ == '__main__':
    main()

# vim: set ts=4 sw=4
