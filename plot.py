#!/usr/bin/env python

import os
import sys

from pylab import *

from utm import latlong2utm


def get_series(directory, csv_name, columns):
    filename = os.path.join(directory, csv_name + '.csv')
    if not os.path.exists(filename):
        sys.exit("no " + filename)
    with open(filename) as f:
        raw = f.read()

    lines = raw.splitlines()
    idx = lines[0].split(',')
    conv = [(c, idx.index(c), func) for c, func in columns]

    data = lines[1:]

    res = {}
    for c, _, _ in conv:
        res[c] = []

    for d in data:
        d = d.split(',')
        for c, i, func in conv:
            res[c].append(func(d[i]))

    return [res[c] for c, _, _ in conv]


def get_gps_utm(data_dir):
    time, lat, lng = get_series(
        data_dir,
        'gps',
        [('time', float), ('latitude', float), ('longitude', float)]
    )

    utmx = []
    utmy = []
    for lati, lngi in zip(lat, lng):
        x, y = latlong2utm(lati, lngi)
        utmx.append(x)
        utmy.append(y)
    return time, utmx, utmy


def get_gps(data_dir):
    time, lat, lng = get_series(
        data_dir,
        'gps',
        [('time', float), ('latitude', float), ('longitude', float)]
    )

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


def main():
    # if len(sys.argv) != 2:
    #     print "Usage: plot.py <dir>"
    #     sys.exit(1)

    data_dir = sys.argv[1] if len(sys.argv) == 2 else 'out-and-back'

    gps_time, utmx, utmy = get_gps(data_dir) or [None, None, None]
    odom_time, odom_x, odom_y = get_series(
        data_dir,
        'odom',
        [
            ('time', float),
            ('pose.pose.position.x', float),
            ('pose.pose.position.y', float)
        ]
    )

    enc_time, enc_count, enc_steer = get_series(
        data_dir,
        'encoder',
        [('time', float), ('count', int), ('steer', int)]
    )

    utmx_filt = [x - utmx[0] for x in utmx]
    utmy_filt = [y - utmy[0] for y in utmy]

    odom_x_filt = [odom_x[0] - x for x in odom_x]
    odom_y_filt = [odom_y[0] - y for y in odom_y]

    # min_time = min(odom_time[0], gps_time[0])
    # max_time = max(odom_time[-1], gps_time[-1])
    # total_time = max_time - min_time

    # odom_color = [(t - min_time)/total_time for t in odom_time]
    # gps_color = [(t - min_time)/total_time for t in gps_time]

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
    #scatter(utmx_filt, utmy_filt, c=gps_color)
    plot(utmx_filt, utmy_filt, c='red')
    plot(odom_x_filt, odom_y_filt, c='blue')
    show()
    subplot(211)
    plot(gps_time, utmx_filt, c='red')
    plot(odom_time, odom_x_filt, c='blue')
    subplot(212)
    plot(gps_time, utmy_filt, c='red')
    plot(odom_time, odom_y_filt, c='blue')
    show()


if __name__ == '__main__':
    main()

# vim: set ts=4 sw=4
