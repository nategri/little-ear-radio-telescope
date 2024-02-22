import gc

import argparse
import datetime
import scipy

import matplotlib
matplotlib.use('Agg')
#import matplotlib.style as mplstyle
#mplstyle.use('fast')

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

import pybaselines

import sys
import multiprocessing as mp
from multiprocessing.managers import BaseManager

REDUCE_FACTOR = 128

def bin_val(a):
    mean = np.mean(a)
    median = np.median(a)
    sigma = np.std(a)
    max_val = np.max(a) 

    return mean

    if (max_val > (mean + 5*sigma)) and (max_val < mean + 100*sigma):
        return np.max(a)
    else:
        return mean

def assemble_telescope_dict(directory):
    data = []

    filenames = sorted(os.listdir(directory))[-4*288:]

    for fn in filenames:
        full_fn = '/'.join([directory, fn])
        print(full_fn)
        with open(full_fn, 'r') as file:
            file_data = json.loads(file.read())
            file_data['filename'] = fn
            file_data['decibels'] = np.array(file_data['skyDecibels']) - np.array(file_data['calDecibels'])
            #file_data['decibels'] = [bin_val(x) for x in file_data['decibels'].reshape(-1, REDUCE_FACTOR)]
            #print(len(file_data['decibels']))
            #print(file_data['decibels'])
            file_data['sky'] = np.array(file_data['skyDecibels'])
            file_data['sky'] = [bin_val(x) for x in file_data['sky'].reshape(-1, REDUCE_FACTOR)][200:-200]
            file_data['sky'] = np.array(file_data['skyDecibels'])
            file_data['sky'] = [bin_val(x) for x in file_data['sky'].reshape(-1, REDUCE_FACTOR)][200:-200]
            #file_data['decibels'] = np.array([np.half(x) for x in file_data['decibels']])
            #del file_data['decibels']

            """
            file_data['decibels'][509] = (file_data['decibels'][508] + file_data['decibels'][515]) / 2
            file_data['decibels'][510] = file_data['decibels'][509]
            file_data['decibels'][511] = file_data['decibels'][509]
            file_data['decibels'][512] = file_data['decibels'][509]
            file_data['decibels'][513] = file_data['decibels'][509]
            file_data['decibels'][514] = file_data['decibels'][509]
            """

            """
            # Computer baseline (aggregate coeffs later)
            center_freq = file_data['centerFrequency']
            samp_rate = file_data['sampleRate']
            x = np.linspace(
                center_freq - (samp_rate/2),
                center_freq + (samp_rate/2),
                len(file_data['decibels'])
            )
            y = file_data['decibels']
            bg, parms = pybaselines.polynomial.modpoly(y, x, poly_order=5, return_coef=True)
            file_data['coeffs'] = list(parms['coef'])
            """

            del file_data['skyDecibels']
            del file_data['calDecibels']
            data.append(file_data)

    WATERFALL_PLOT_MIN = np.median(data[-1]['decibels']) - 0.25
    WATERFALL_PLOT_MAX = np.median(data[-1]['decibels']) + 0.2

    for d in data:
        d['waterfall_min'] = WATERFALL_PLOT_MIN
        d['waterfall_max'] = WATERFALL_PLOT_MAX

    return data

def baseline_correction(data):
    spectra_averages = [np.mean(x['decibels']) for x in data]
    min_idx = np.argmin(spectra_averages)

    center_freq = data[min_idx]['centerFrequency']
    samp_rate = data[min_idx]['sampleRate']

    x = np.linspace(
        center_freq - (samp_rate/2),
        center_freq + (samp_rate/2),
        len(data[min_idx]['decibels'])
    )

    """
    y = data[min_idx]['decibels']

    bg, parms = pybaselines.polynomial.modpoly(y, x, poly_order=3, return_coef=True)

    for d in data:
        d['decibels'] = np.array(d['decibels'] - np.array(bg))
        d['power'] = parms['coef'][0]
    """

    """
    def f(z, c):
        r = 0.0
        for i in range(len(c)):
            r += c[i]*np.power(z, i)
        return r

    coeffs = np.array([0.0]*len(data[0]['coeffs']))
    for d in data:
        coeffs += np.array(d['coeffs'])
    coeffs = coeffs / len(data)

    bg = [f(z, coeffs) for z in x]
    """

    for d in data:
        #center_freq = d['centerFrequency']
        #samp_rate = d['sampleRate']
        
        x = np.linspace(
            center_freq - (samp_rate/2),
            center_freq + (samp_rate/2),
            len(d['decibels'])
        )
        y = d['decibels']

        bg, parms = pybaselines.polynomial.imodpoly(y, x, poly_order=5, return_coef=True)

        d['power'] = np.median(d['decibels'])
        #d['power'] = np.median(d['decibels'])
        #d['power'] = parms['coef'][0]
        d['decibels'] = np.array(d['decibels']) - np.array(bg)
        #d['decibels'] = d['sky']

    WATERFALL_PLOT_MIN = np.median(data[-1]['decibels']) - 0.15
    WATERFALL_PLOT_MAX = np.median(data[-1]['decibels']) + 0.5

    for d in data:
        d['waterfall_min'] = WATERFALL_PLOT_MIN
        d['waterfall_max'] = WATERFALL_PLOT_MAX

def power_for_list(data_list, agg_func=np.average):

    t_list = []
    p_list = []

    for data in data_list:
        dt = dateutil.parser.parse(data['timestamp'])

        t_list.append(dt)
        p_list.append(
            data['power']
            #np.median(data['decibels'])
        )

    return t_list, p_list

    #def spectrum(self):
        #return self._data

    # Returns power and spectrum data up until and including filename

def get_data_for_filename(td, filename):
    data_subset = [x for x in td if x['filename'] <= filename]

    return data_subset, power_for_list(data_subset)

def _azel_to_radec(az, el, date_string):
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

def _galactic_plane_in_radec():
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

def render(td, filename):
    #output_filename = filename[:-5]+'.png'
    #if os.path.isfile('./render_output/'+output_filename):
        #return

    _fig, _ax = pyplot.subplots(nrows=2, ncols=2, figsize=(16, 8))

    TIMESTEP = 5 # Minutes
    DAY_OF_TIMESTEPS = int((24*60/TIMESTEP))

    # Retrieve data
    freq_data, power_data = get_data_for_filename(td, filename)
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
    _ax[0][0].clear()
    _ax[0][1].clear()
    _ax[1][0].clear()
    _ax[1][1].clear()

    _fig.suptitle(current_date_string[:-5])


    # Spectrum plot
    #freqs = current_freq_data['frequency']
    center_freq = current_freq_data['centerFrequency']
    samp_rate = current_freq_data['sampleRate']
    freqs = np.linspace(
        center_freq - (samp_rate/2),
        center_freq + (samp_rate/2),
        len(current_freq_data['decibels'])
    )

    #freqs = freqs.reshape(-1, REDUCE_FACTOR).mean(axis=1)

    dbs = np.array(current_freq_data['decibels'])
    dbs_median = np.median(dbs)
    _ax[0][0].plot(np.array(freqs) / 1.0e6, dbs, '-b', label='Spectrum', linewidth=0.5)
    _ax[0][0].set_ylim(dbs_median - 0.5, dbs_median + 1.5)
    _ax[0][0].set_xlabel('MHz')
    _ax[0][0].set_ylabel('dB / Hz')
    _ax[0][0].tick_params(labelsize=8)
    _ax[0][0].set_xlim(bottom_freq, top_freq)
    _ax[0][0].legend(loc='upper left')

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
    _ax[1][0].set_xlabel('MHz')
    _ax[1][0].get_yaxis().set_ticks([])
    _ax[1][0].set_ylabel('Previous 24 Hours')
    _ax[1][0].tick_params(labelsize=8)
    _ax[1][0].imshow(
        waterfall_data,
        extent=[
            bottom_freq,
            top_freq,
            0.0,
            1.0
        ],
        cmap='jet',
        aspect='auto',
        vmin=td[-1]['waterfall_min'],
        vmax=td[-1]['waterfall_max']
        #interpolation='none'
    )

    # Map plot
    # Credit to: https://github.com/0xCoto/Virgo
    ra, dec = _azel_to_radec(azimuth, elevation, current_date_string)
    g_ra_list, g_dec_list = _galactic_plane_in_radec()
    _ax[0][1].set_xlabel('Right Ascension')
    _ax[0][1].set_ylabel('Declination')
    _ax[0][1].tick_params(labelsize=8)
    _ax[0][1].scatter(g_ra_list, g_dec_list, s=20, color='royalblue', label='Galactic Plane')
    _ax[0][1].scatter(ra, dec, s=200, color=[0.85, 0.15, 0.16], label='Telescope')
    _ax[0][1].set_facecolor('darkblue')
    _ax[0][1].legend(loc='upper left')
    _ax[0][1].set_xlim(0.0, 24.0)
    _ax[0][1].set_ylim(-90.0, 90.0)
    _ax[0][1].invert_xaxis()

    # Power plot
    _ax[1][1].plot(power_data[0], power_data[1], 'r-', label='Power?')
    _ax[1][1].set_xlabel('Previous 12 Hours')
    _ax[1][1].set_ylabel('Order-0 Spectrum BG Fit Term')
    _ax[1][1].set_xlim(power_data[0][-1] - datetime.timedelta(days=0.5), power_data[0][-1])
    _ax[1][1].tick_params(labelsize=8)
    for tick_label in _ax[1][1].get_xticklabels():
        tick_label.set_ha("right")
        tick_label.set_rotation(30)
    _ax[1][1].legend(loc='upper left')


    # Wrap up
    pyplot.tight_layout()
    pyplot.savefig('./render_output/'+filename.split('.')[0]+'.png')
    print('./render_output/'+filename.split('.')[0]+'.png ' + str(ra) + ' ' + str(dec))
    pyplot.cla()
    pyplot.clf()
    pyplot.close('all')
    gc.collect()

def mp_proc_func(td, filename):
    render(td, filename)

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

    telescope_data = assemble_telescope_dict(args.data)
    baseline_correction(telescope_data)

    manager = mp.Manager()
    shared_telescope_data = manager.list(telescope_data)

    #filenames = sorted(os.listdir(args.data))[int(-288):]
    filenames = sorted(os.listdir(args.data))[int(-4*288):]
    #filenames = sorted(os.listdir(args.data))
    #render(shared_telescope_data, filenames[0])

    pool = mp.Pool(10)
    for fn in filenames:
        pool.apply_async(mp_proc_func, args=(shared_telescope_data, fn))
    pool.close()
    pool.join()
