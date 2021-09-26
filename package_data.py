import datetime
import time
import os
import numpy as np
import json

DECIMATION = 500
INTEGRATION_TIME = 5*60

def find_raw_data_files():
    raw_files = []
    filenames = os.listdir('.')
    nowtime = time.time()
    for fn in filenames:
        mtime = os.path.getmtime(fn)
        dt = nowtime - mtime
        
        if (dt < 2.0) and fn[-4:] == '.dat':
            if fn.split('_')[0] in ['spectrum', 'power']:
                raw_files.append(fn)

    assert len(raw_files) == 2

    return sorted(raw_files)

def process_raw(data_dir):
    power_filename, spectrum_filename = find_raw_data_files()

    center_freq, samp_rate, fft_size = [int(x) for x in power_filename[:-4].split('_')[1:]]

    file_lookback = int(INTEGRATION_TIME*samp_rate/(fft_size*DECIMATION))

    power_val = np.fromfile(power_filename, dtype='float32')[-file_lookback:]
    spectrum_arr = np.fromfile(spectrum_filename, dtype='float32')

    num_rows = len(spectrum_arr) / fft_size
    spectrum_rows = spectrum_arr.reshape(num_rows, fft_size)[-file_lookback:]
    sum_arr = np.array(fft_size*[0.0])
    for x in spectrum_rows:
        sum_arr += x

    spectrum_arr = sum_arr
    power_val = float(np.sum(power_val))

    print(spectrum_arr)

    spectrum_arr = 10*np.log10(np.abs(spectrum_arr))
    power_val = 10*np.log10(np.abs(power_val))

    timestamp = datetime.datetime.fromtimestamp(
        os.path.getmtime(spectrum_filename)
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
        process_raw('./data')
        time.sleep(5*60)
