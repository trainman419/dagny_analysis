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
    subplot(211)
    plot(time, lat)
    subplot(212)
    plot(time, lng)
    show()
    utmx = []
    utmy = []
    for lati, lngi in zip(lat, lng):
        x, y = latlong2utm(lati, lngi)
        utmx.append(x)
        utmy.append(y)
    return time, utmx, utmy


def main():
    if len(sys.argv) != 2:
        print "Usage: plot.py <dir>"
        sys.exit(1)

    data_dir = sys.argv[1]

    time, utmx, utmy = get_gps(data_dir) or [None, None, None]
    utmx_filt = [x - utmx[0] for x in utmx]
    utmy_filt = [y - utmy[0] for y in utmy]
    for i, x in enumerate(utmx_filt):
        if i == 0:
            continue
        if abs(utmx_filt[i-1] - x) > 10:
            print('x', i)
            del utmx_filt[i]
            del utmy_filt[i]
            del time[i]
    for i, x in enumerate(utmy_filt):
        if i == 0:
            continue
        if abs(utmy_filt[i-1] - x) > 10:
            print('y', i)
            del utmx_filt[i]
            del utmy_filt[i]
            del time[i]
    # subplot(311)
    # plot(time, utmx_filt)
    # subplot(312)
    # plot(time, utmy_filt)
    # subplot(313)
    print(len(time))
    axis('equal')
    scatter(utmx_filt, utmy_filt, c=time)
    show()


if __name__ == '__main__':
    main()

# vim: set ts=4 sw=4
