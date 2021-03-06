import gc

import argparse
import datetime
import scipy

import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot
import numpy as np
import os
import json
import dateutil

from astropy.time import Time as AstroTime
from astropy.coordinates import SkyCoord as AstroSkyCoord
from astropy.coordinates import Galactic as AstroGalactic
from astropy.coordinates import EarthLocation as AstroEarthLocation
from astropy.coordinates import AltAz as AstroAltAz
import astropy.units as AstroUnits

import sys
import multiprocessing as mp
from multiprocessing.managers import BaseManager

WATERFALL_PLOT_MIN = -7.5
WATERFALL_PLOT_MAX = -5.8

class TelescopeData(object):
    def __init__(self, directory):
        self._data = []

        filenames = sorted(os.listdir(directory))

        for fn in filenames:
            full_fn = '/'.join([directory, fn])
            print(full_fn)
            with open(full_fn, 'r') as file:
                file_data = json.loads(file.read())
                file_data['filename'] = fn
                file_data['decibels'] = [np.half(x) for x in file_data['decibels']]
                self._data.append(file_data)

        self._data = sorted(self._data, key=lambda x: x['timestamp'])

    def power(self, data_list, agg_func=np.average):

        t_list = []
        p_list = []

        for data in data_list:
            dt = dateutil.parser.parse(data['timestamp'])

            t_list.append(dt)
            p_list.append(
                #data['power']
                np.median(data['decibels'])
            )

        return t_list, p_list

    def spectrum(self):
        return self._data

    # Returns power and spectrum data up until and including filename
    def get_data_for_filename(self, filename):
        data_subset = [x for x in self._data if x['filename'] <= filename]

        return data_subset, (self.power(data_subset))

class DataRenderer(object):
    def __init__(self, data_directory):
        self._telescope_data = TelescopeData(data_directory)

    def _azel_to_radec(self, az, el, date_string):
        # Credit to: https://github.com/0xCoto/Virgo

        try:
            lat = float(os.environ['RT_LAT'])
            lon = float(os.environ['RT_LON'])
            alt = 0.0
        except KeyError:
            print("Please set RADIO_TELESCOPE_[LATITUDE, LONGITUDE, ALTITUDE] environment variables")
            sys.exit(1)

        earth_location = AstroEarthLocation(lat=lat*AstroUnits.deg, lon=lon*AstroUnits.deg, height=alt*AstroUnits.m)
        astro_time = AstroTime(date_string+'Z', format='isot', scale='utc')
        sky_coord = AstroSkyCoord(
            alt=el*AstroUnits.deg,
            az=az*AstroUnits.deg,
            obstime=astro_time,
            frame='altaz',
            location=earth_location
        )

        icrs_coord = sky_coord.icrs

        return icrs_coord.ra.hour, icrs_coord.dec.deg

    def _galactic_plane_in_radec(self):
        ra_list = []
        dec_list = []
        for x in range(0, 361, 1):
            sky_coord = AstroSkyCoord(
                b=0.0*AstroUnits.deg,
                l=x*AstroUnits.deg,
                frame=AstroGalactic
            )

            icrs_coord = sky_coord.icrs

            ra_list.append(icrs_coord.ra.hour)
            dec_list.append(icrs_coord.dec.deg)

        return ra_list, dec_list

    def render(self, filename):
        #output_filename = filename[:-5]+'.png'
        #if os.path.isfile('./render_output/'+output_filename):
            #return

        self._fig, self._ax = pyplot.subplots(nrows=2, ncols=2, figsize=(16, 8))

        TIMESTEP = 5 # Minutes
        DAY_OF_TIMESTEPS = int((24*60/TIMESTEP))

        # Retrieve data
        freq_data, power_data = self._telescope_data.get_data_for_filename(filename)
        azimuth = freq_data[-1]['azimuth']
        elevation= freq_data[-1]['elevation']
        current_freq_data = freq_data[-1]
        current_date_string = freq_data[-1]['timestamp']
        print(current_date_string)
        #bottom_freq = current_freq_data['frequency'][0] / 1.0e6
        #top_freq = current_freq_data['frequency'][-1] / 1.0e6
        bottom_freq = current_freq_data['startFrequency'] / 1.0e6
        top_freq = current_freq_data['endFrequency'] / 1.0e6

        # Clear plot
        self._ax[0][0].clear()
        self._ax[0][1].clear()
        self._ax[1][0].clear()
        self._ax[1][1].clear()

        self._fig.suptitle(current_date_string[:-5])


        # Spectrum plot
        #freqs = current_freq_data['frequency']
        center_freq = current_freq_data['centerFrequency']
        samp_rate = current_freq_data['sampleRate']
        freqs = np.linspace(
            center_freq - (samp_rate/2),
            center_freq + (samp_rate/2),
            len(current_freq_data['decibels'])
        ).tolist()

        dbs = np.array(current_freq_data['decibels'])
        dbs_median = np.median(dbs)
        self._ax[0][0].plot(np.array(freqs) / 1.0e6, dbs, '-b', label='Spectrum', linewidth=0.5)
        self._ax[0][0].set_ylim(dbs_median - 0.5, dbs_median + 1.5)
        self._ax[0][0].set_xlabel('MHz')
        self._ax[0][0].set_ylabel('dB / Hz')
        self._ax[0][0].tick_params(labelsize=8)
        self._ax[0][0].set_xlim(bottom_freq, top_freq)
        self._ax[0][0].legend(loc='upper left')

        # Waterfall plot
        waterfall_data = [np.array(x['decibels']) for x in freq_data][::-1]
        waterfall_len = len(waterfall_data[0])
        waterfall_data = [x for x in waterfall_data if len(x) == waterfall_len]
        if len(waterfall_data) < DAY_OF_TIMESTEPS:
            diff = DAY_OF_TIMESTEPS - len(waterfall_data)
            pad = [len(waterfall_data[0])*[-100.0] for _ in range(diff)]
            waterfall_data += pad
        elif len(waterfall_data) > DAY_OF_TIMESTEPS:
            waterfall_data = waterfall_data[:DAY_OF_TIMESTEPS]
        self._ax[1][0].set_xlabel('MHz')
        self._ax[1][0].get_yaxis().set_ticks([])
        self._ax[1][0].set_ylabel('Previous 24 Hours')
        self._ax[1][0].tick_params(labelsize=8)
        self._ax[1][0].imshow(
            waterfall_data,
            extent=[
                bottom_freq,
                top_freq,
                0.0,
                1.0
            ],
            cmap='jet',
            aspect='auto',
            vmin=WATERFALL_PLOT_MIN,
            vmax=WATERFALL_PLOT_MAX
        )

        # Map plot
        # Credit to: https://github.com/0xCoto/Virgo
        ra, dec = self._azel_to_radec(azimuth, elevation, current_date_string)
        g_ra_list, g_dec_list = self._galactic_plane_in_radec()
        self._ax[0][1].set_xlabel('Right Ascension')
        self._ax[0][1].set_ylabel('Declination')
        self._ax[0][1].tick_params(labelsize=8)
        self._ax[0][1].scatter(g_ra_list, g_dec_list, s=20, color='royalblue', label='Galactic Plane')
        self._ax[0][1].scatter(ra, dec, s=200, color=[0.85, 0.15, 0.16], label='Telescope')
        self._ax[0][1].set_facecolor('darkblue')
        self._ax[0][1].legend(loc='upper left')
        self._ax[0][1].set_xlim(0.0, 24.0)
        self._ax[0][1].set_ylim(-90.0, 90.0)
        self._ax[0][1].invert_xaxis()

        # Power plot
        self._ax[1][1].plot(power_data[0], power_data[1], 'r-', label='Power')
        self._ax[1][1].set_xlabel('Previous 12 Hours')
        self._ax[1][1].set_ylabel('dB')
        self._ax[1][1].set_xlim(power_data[0][-1] - datetime.timedelta(days=0.5), power_data[0][-1])
        self._ax[1][1].tick_params(labelsize=8)
        for tick_label in self._ax[1][1].get_xticklabels():
            tick_label.set_ha("right")
            tick_label.set_rotation(30)
        self._ax[1][1].legend(loc='upper left')


        # Wrap up
        pyplot.tight_layout()
        print('./render_output/'+filename.split('.')[0]+'.png ' + str(ra) + ' ' + str(dec))
        pyplot.savefig('./render_output/'+filename.split('.')[0]+'.png')
        pyplot.cla()
        pyplot.clf()
        pyplot.close('all')
        gc.collect()

def mp_proc_func(dr, filename):
    dr.render(filename)

if __name__ == "__main__":

    num_processed = 0

    parser = argparse.ArgumentParser(
        description="Render available data radio telescope data into a movie."
    )
    parser.add_argument(
        '--data',
        metavar='DIR',
        type=str,
        nargs='?',
        required=True,
        help='Data directory'
    )
    args = parser.parse_args()

    BaseManager.register('DataRenderer', DataRenderer)
    manager = BaseManager()
    manager.start()
    #data_renderer = DataRenderer(args.data)
    
    shared_data_renderer = manager.DataRenderer(args.data)

    filenames = sorted(os.listdir(args.data))[int(-288):]

    pool = mp.Pool(6)
    for fn in filenames:
        pool.apply_async(mp_proc_func, args=(shared_data_renderer, fn))
    pool.close()
    pool.join()
