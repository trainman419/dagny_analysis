from pylab import plot, scatter, show, axis, quiver

from plot import get_series, get_gps_utm

from math import sin, cos, pi, atan2

Q_SCALE = (0.032 / 4.0)

steer_to_radius_map = {
    0: 100.0,
    10: 5.550,
    20: 3.875,
    30: 2.900,
    40: 1.960,
    50: 1.560,
    60: 1.290,
    70: 1.025,
    80: 0.905,
    90: 0.790,
    100: 0.695
}

radius_to_steer_map = {}
for k, v in steer_to_radius_map.iteritems():
    radius_to_steer_map[v] = k


def steer_to_radius(steer):
    steer = abs(steer)
    index = min((int(steer) / 10) * 10, 100)
    radius = steer_to_radius_map[index]
    if steer != index:
        # Extrapolate
        delta = steer - index
        if index != 100:
            step = steer_to_radius_map[index + 10] - radius
        else:
            step = steer_to_radius_map[100] - steer_to_radius_map[90]
        radius += step * delta
    return radius


def delta_from_start(data, reverse=False):
    if reverse:
        return [data[0] - x for x in data]
    else:
        return [x - data[0] for x in data]


def pairwise_diff(data):
    new_data = []
    for i, x in enumerate(data):
        if i == 0:
            new_data.append(None)
        else:
            new_data.append(x - data[i - 1])
    return [data[i + 1] if x is None else x for i, x in enumerate(new_data)]


def filter_and_interpolate_fill(data, min=-100, max=100):
    if len(data) < 4:
        return data
    data = [x if x < max and x > min else None for x in data]
    new_data = []
    for i, x in enumerate(data):
        if x is not None:
            new_data.append(x)
            continue
        if i == 0:
            new_data.append(data[i + 1])
        elif i == len(data):
            new_data.append(data[i - 1])
        else:
            new_data.append((data[i + 1] - data[i - 1]) / 2.0)
    return new_data


def kf_filter(enc_time, enc_count, enc_steer):
    pass


def dead_recon(enc_time, enc_count, enc_steer, gps_time, utm_x, utm_y, odomx, odomy, magx, magy):
    xs = [0]
    ys = [0]
    thetas = [0]
    ox = 0.036923
    oy = 0.107692
    os = 1.5
    magx = [x - ox*os for i, x in enumerate(magx) if i % 2 == 0]
    magy = [y - oy*os for i, y in enumerate(magy) if i % 2 == 0]
    for dtime, dcount, steer, magxn, magyn in zip(pairwise_diff(enc_time), enc_count, enc_steer, magx, magy):
        dist = dcount * Q_SCALE * 1.3
        yaw = thetas[-1]
        steer += 2
        radius = steer_to_radius(steer)
        if steer == 0:
            dx = dist * cos(yaw)
            dy = dist * sin(yaw)
            dtheta = 0
        else:
            dtheta = dist / radius
            if steer > 0:
                theta_c1 = yaw + (pi / 2.0)
            else:
                dtheta *= -1
                theta_c1 = yaw - (pi / 2.0)
            theta_c2 = theta_c1 - dtheta

            dx = radius * (cos(theta_c2) - cos(theta_c1))
            dy = radius * (sin(theta_c2) - sin(theta_c1))

        xs.append(xs[-1] + dx)
        ys.append(ys[-1] + dy)
        thetas.append(atan2(magxn, magyn) + 0.1)
    #for

    axis('equal')
    plot(utm_x, utm_y)
    # scatter(utm_x, utm_y, c=gps_time)
    plot([x * -1 for x in xs], [y * -1 for y in ys])
    plot(odomx, odomy)
    # quiver(xs, ys, [cos(x) for x in thetas], [sin(x) for x in thetas], minlength=2)
    show()


def main():
    data_dir = 'out-and-back'
    enc_time, enc_count, enc_steer = get_series(
        data_dir,
        'encoder',
        [('time', float), ('count', int), ('steer', int)]
    )
    odom_time, odom_x, odom_y = get_series(
        data_dir,
        'odom',
        [
            ('time', float),
            ('pose.pose.position.x', float),
            ('pose.pose.position.y', float)
        ]
    )
    mag_time, mag_x, mag_y, mag_z = get_series(
        data_dir,
        'magnetic',
        [('time', float), ('vector.x', float), ('vector.y', float), ('vector.z', float)]
    )
    gps_time, utmx, utmy = get_gps_utm(data_dir)

    enc_time = delta_from_start(enc_time)
    enc_count = pairwise_diff(enc_count)
    enc_count = filter_and_interpolate_fill(enc_count)
    # scatter(enc_time, map(steer_to_radius, enc_steer))
    # show()
    utmx = filter_and_interpolate_fill(delta_from_start(utmx))
    utmy = filter_and_interpolate_fill(delta_from_start(utmy))
    odom_x = delta_from_start(odom_x, reverse=True)
    odom_y = delta_from_start(odom_y, reverse=True)

    dead_recon(enc_time, enc_count, enc_steer, gps_time, utmx, utmy, odom_x, odom_y, mag_x, mag_y)

if __name__ == '__main__':
    main()
