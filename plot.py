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
    seq = []
    lat = []
    lng = []
    for x in raw.splitlines()[1:]:
        x = x.split(',')
        seq.append(int(x[1]))
        lat.append(float(x[6]))
        lng.append(float(x[7]))
    for i, x in enumerate(lat):
        if i == 0:
            continue
        if abs(lat[i-1] - x) > 10:
            print(i)
            del lat[i]
            del lng[i]
            del seq[i]
    for i, x in enumerate(lng):
        if i == 0:
            continue
        if abs(lng[i-1] - x) > 10:
            print(i)
            del lat[i]
            del lng[i]
            del seq[i]
    subplot(211)
    plot(seq, lat)
    subplot(212)
    plot(seq, lng)
    show()
    utmx = []
    utmy = []
    for lati, lngi in zip(lat, lng):
        x, y = latlong2utm(lati, lngi)
        utmx.append(x)
        utmy.append(y)
    return seq, utmx, utmy


def main():
    if len(sys.argv) != 2:
        print "Usage: plot.py <dir>"
        sys.exit(1)

    data_dir = sys.argv[1]

    seq, utmx, utmy = get_gps(data_dir) or [None, None, None]
    utmx_filt = [x - utmx[0] for x in utmx]
    utmy_filt = [y - utmy[0] for y in utmy]
    for i, x in enumerate(utmx_filt):
        if i == 0:
            continue
        if abs(utmx_filt[i-1] - x) > 10:
            print('x', i)
            del utmx_filt[i]
            del utmy_filt[i]
            del seq[i]
    for i, x in enumerate(utmy_filt):
        if i == 0:
            continue
        if abs(utmy_filt[i-1] - x) > 10:
            print('y', i)
            del utmx_filt[i]
            del utmy_filt[i]
            del seq[i]
    # subplot(311)
    # plot(seq, utmx_filt)
    # subplot(312)
    # plot(seq, utmy_filt)
    # subplot(313)
    print(len(seq))
    axis('equal')
    scatter(utmx_filt, utmy_filt, c=seq)
    show()


if __name__ == '__main__':
    main()

# vim: set ts=4 sw=4
