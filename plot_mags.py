from pylab import axis, subplot, plot, show, ylim

from plot import get_series


def main():
    data_dir = 'out-and-back'
    mag_time, mag_x, mag_y, mag_z = get_series(
        data_dir,
        'magnetic',
        [('time', float), ('vector.x', float), ('vector.y', float), ('vector.z', float)]
    )

    axis('equal')
    subplot(311)
    plot(mag_time, mag_x)
    ylim([-0.5, 0.5])
    subplot(312)
    plot(mag_time, mag_y)
    ylim([-0.5, 0.5])
    subplot(313)
    plot(mag_time, mag_z)
    ylim([-0.5, 0.5])
    show()

if __name__ == '__main__':
    main()
