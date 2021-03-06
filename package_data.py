import datetime
import time
import os
import numpy as np
import json
import subprocess
import dateutil.parser
import argparse

def find_raw_data_files():
    raw_files = []
    filenames = os.listdir('.')
    nowtime = time.time()
    for fn in filenames:
        mtime = os.path.getmtime(fn)
        dt = nowtime - mtime
        
        if (dt < 10.0) and fn[-4:] == '.dat':
            if fn.split('_')[1] in ['spectrum', 'power']:
                raw_files.append(fn)

    assert len(raw_files) == 3

    return sorted(raw_files)

def read_voltage():
    now = datetime.datetime.utcnow()
    val_list = []
    with open('voltage.out', 'r') as f:
        for line in list(f.readlines())[::-1]:
            try:
                dt_str, val_str = line.split()
                dt = dateutil.parser.parse(dt_str, ignoretz=True)
                val = float(val_str)

                if (now - dt).total_seconds() < (10.0*60.0):
                    val_list.append(val)
                else:
                    break
            except:
                continue

    return np.median(val_list)

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

    #power_val = np.sum(power_val)
    power_val = np.median(power_val)

    timestamp = datetime.datetime.fromtimestamp(
        os.path.getmtime(sky_spectrum_filename)
    )

    print("Data recorded: "+timestamp.isoformat())

    data = {
        'timestamp': timestamp.isoformat(),
        'frequency': np.linspace(
            center_freq - (samp_rate/2),
            center_freq + (samp_rate/2),
            len(spectrum_arr)
        ).tolist(),
        'decibels': spectrum_arr.tolist(),
        'power': float(power_val),
        'voltage': read_voltage(),
        'elevation': args.el,
        'azimuth': args.az
    }

    filename = timestamp.strftime('%Y%m%d%H%M%S')
    with open(data_dir + '/telescope_data_'+filename+'.json', 'w') as f:
        f.write(json.dumps(data))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Capture data from the radio."
    )
    parser.add_argument(
        '--continuum',
        action='store_true',
        help='Record data at 1390 MHz instead of at H line'
    )
    parser.add_argument(
        '--az',
        metavar='DEG',
        type=float,
        nargs='?',
        required=True,
        help='Azimuth of telescope'
    )
    parser.add_argument(
        '--el',
        metavar='DEG',
        type=float,
        nargs='?',
        required=True,
        help='Elevation of telescope'
    )
    args = parser.parse_args()

    # Turn on radio
    print("Powering on radio...")
    subprocess.call('python radio_power.py on', shell=True)
    time.sleep(30)

    while True:
        if read_voltage() > 13.5:
            if args.continuum:
                rcode = subprocess.call('python start_radio.py --filter-bw=2000000 --tuning-freq 1390000000 --time 300', shell=True)
            else:
                rcode = subprocess.call('python start_radio.py --filter-bw=2000000 --time=300', shell=True)
            if rcode != 0:
                print("Caught non-zero exit code for acquisition process: Rebooting in 120 seconds.")
                time.sleep(120)
                os.system('sudo reboot')
            process_raw('./data')
        else:
            subprocess.call('python radio_power.py off', shell=True)
            while True:
                time.sleep(60)
                print("Voltage too low: " + str(read_voltage()))
                if read_voltage() > 15.0:
                    print("Voltage threshold met---powering on radio....")
                    subprocess.call('python radio_power.py on', shell=True)
                    time.sleep(30)
                    break
