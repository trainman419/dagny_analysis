import os
import sys

from pylab import *

from utm import latlong2utm

gps_file = 'out-and-back/gps.csv'


def get_gps():
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
    utmx = []
    utmy = []
    for lati, lngi in zip(lat, lng):
        x, y = latlong2utm(lati, lngi)
        utmx.append(x)
        utmy.append(y)
    return seq, utmx, utmy


def main():
    seq, utmx, utmy = get_gps() or [None, None, None]
    utmx_filt = [x - utmx[0] for x in utmx]
    utmy_filt = [y - utmy[0] for y in utmy]
    for i, x in enumerate(utmx_filt):
        if abs(utmx_filt[i-1] - x) > 10:
            print(i)
            del utmx_filt[i]
            del utmy_filt[i]
            del seq[i]
    subplot(311)
    plot(seq, utmx_filt)
    subplot(312)
    plot(seq, utmy_filt)
    subplot(313)
    axis('equal')
    scatter(utmx_filt, utmy_filt, c=seq)
    show()


if __name__ == '__main__':
    main()
