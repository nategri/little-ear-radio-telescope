import datetime
import time
import os
import numpy as np
import json
import subprocess

def find_raw_data_files():
    raw_files = []
    filenames = os.listdir('.')
    nowtime = time.time()
    for fn in filenames:
        mtime = os.path.getmtime(fn)
        dt = nowtime - mtime
        
        if (dt < 2.0) and fn[-4:] == '.dat':
            if fn.split('_')[1] in ['spectrum', 'power']:
                raw_files.append(fn)

    assert len(raw_files) == 3

    return sorted(raw_files)

def process_raw(data_dir):
    cal_spectrum_filename, combined_power_filename, sky_spectrum_filename = find_raw_data_files()

    center_freq, samp_rate, fft_size = [int(x) for x in combined_power_filename[:-4].split('_')[2:]]

    power_val = np.fromfile(combined_power_filename, dtype='float32')
    sky_spectrum_arr = np.fromfile(sky_spectrum_filename, dtype='float32')
    cal_spectrum_arr = np.fromfile(cal_spectrum_filename, dtype='float32')

    num_rows = len(sky_spectrum_arr) / fft_size
    sky_spectrum_rows = sky_spectrum_arr.reshape(num_rows, fft_size)
    cal_spectrum_rows = cal_spectrum_arr.reshape(num_rows, fft_size)

    sky_sum_arr = np.array(fft_size*[0.0])
    for x in sky_spectrum_rows:
        sky_sum_arr += x

    cal_sum_arr = np.array(fft_size*[0.0])
    for x in cal_spectrum_rows:
        cal_sum_arr += x

    sky_spectrum_arr = sky_sum_arr
    cal_spectrum_arr = cal_sum_arr

    spectrum_arr = (10*np.log10(sky_sum_arr)) - (10*np.log10(cal_spectrum_arr))

    power_val = float(np.sum(power_val))

    timestamp = datetime.datetime.fromtimestamp(
        os.path.getmtime(sky_spectrum_filename)
    )

    print(timestamp.isoformat())

    data = {
        'timestamp': timestamp.isoformat(),
        'frequency': np.linspace(
            center_freq - (samp_rate/2),
            center_freq + (samp_rate/2),
            len(spectrum_arr)
        ).tolist(),
        'decibels': spectrum_arr.tolist(),
        'power': power_val
    }

    filename = timestamp.strftime('%Y%m%d%H%M%S')
    with open(data_dir + '/telescope_data_'+filename+'.json', 'w') as f:
        f.write(json.dumps(data))

if __name__ == "__main__":

    while True:
        subprocess.call('python start_radio.py', shell=True)
        process_raw('./data')
