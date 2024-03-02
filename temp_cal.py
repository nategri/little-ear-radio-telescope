import json
import os
import numpy as np
from matplotlib import pyplot

if __name__ == "__main__":
    data = []
    filenames = os.listdir('data')
    filenames = sorted(filenames)[5:]
    for fn in filenames:
        with open('./data/'+fn, 'r') as f:
            fdata = json.loads(f.read())

            data.append(
                {
                    'temp': fdata['lnaTemp']['temp'],
                    #'temp': fdata['sdrTemp'],
                    'rx1': np.median(fdata['skyDecibels']),
                    'rx2': np.median(fdata['calDecibels']),
                    'diff': np.median(fdata['calDecibels']) -  np.median(fdata['skyDecibels'])
                }
            )

    #all_cals = [x['rx1'] for x in data] + [x['rx2'] for x in data]
    #all_temps = [x['temp'] for x in data] + [x['temp'] for x in data]
    #coeffs = np.polyfit(all_temps, all_cals, 1)
    #print(coeffs)
    #fit_func = np.poly1d(coeffs)

    coeffs = np.polyfit(
        [x['temp'] for x in data],
        [x['rx1'] for x in data],
        1
    )
    print(coeffs)

    coeffs = np.polyfit(
        [x['temp'] for x in data],
        [x['rx2'] for x in data],
        1
    )
    print(coeffs)
    fit_func = np.poly1d(coeffs)

    #pyplot.plot([x['temp'] for x in data], [x['rx1'] for x in data], 'b.', label='rx1 (terminated)')
    #pyplot.plot([x['temp'] for x in data], [x['rx2'] for x in data], 'r.', label='rx2 (terminated)')
    #pyplot.plot([x['rx1'] for x in data], [x['rx2'] for x in data], 'k.', label='chan0 v chan1')
    print(len([x['rx1'] for x in data]))
    print(len([x['rx2'] for x in data]))
    print(len([x['temp'] for x in data]))
    pyplot.scatter(
        #[x['rx1'] for x in data],
        #[x['rx2'] for x in data],
        [x['temp'] for x in data],
        [x['rx1'] for x in data],
        c='r',
        #c = [x['temp'] for x in data],
        #c = [x['diff'] for x in data],
        #label='rx1/rx2 difference',
        alpha=0.2,
        label='chan0'
    )
    pyplot.scatter(
        #[x['rx1'] for x in data],
        #[x['rx2'] for x in data],
        [x['temp'] for x in data],
        [x['rx2'] for x in data],
        c='g',
        #c = [x['temp'] for x in data],
        #c = [x['diff'] for x in data],
        #label='rx1/rx2 difference',
        alpha=0.2,
        label='chan1'
    )
    pyplot.jet()
    pyplot.plot([x['temp'] for x in data], fit_func([x['temp'] for x in data]), 'k--', label='fit')
    pyplot.xlabel('Temperature [C]')
    pyplot.ylabel('Reading for 50 ohm terminated channels [dB]')
    pyplot.title('SDR Temperature Calibration Curve\n m: {}, b: {}'.format(np.round(coeffs[1], 5), np.round(coeffs[0], 5)))
    pyplot.legend()
    pyplot.show()
