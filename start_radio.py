#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Start Radio
# GNU Radio version: 3.10.1.1

from gnuradio import blocks
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import iio




class start_radio(gr.top_block):

    def __init__(self, fft_size=512, filter_bw=20000000, gain=32, samp_rate=2000000, time=150, tuning_freq=1420405752):
        gr.top_block.__init__(self, "Start Radio", catch_exceptions=True)

        ##################################################
        # Parameters
        ##################################################
        self.fft_size = fft_size
        self.filter_bw = filter_bw
        self.gain = gain
        self.samp_rate = samp_rate
        self.time = time
        self.tuning_freq = tuning_freq

        ##################################################
        # Variables
        ##################################################
        self.decimation = decimation = 500

        ##################################################
        # Blocks
        ##################################################
        self.iio_fmcomms2_source_0 = iio.fmcomms2_source_fc32('ip:192.168.2.1', [True, True, True, True], 0x20000)
        self.iio_fmcomms2_source_0.set_len_tag_key('packet_len')
        self.iio_fmcomms2_source_0.set_frequency(tuning_freq)
        self.iio_fmcomms2_source_0.set_samplerate(samp_rate)
        if True:
            self.iio_fmcomms2_source_0.set_gain_mode(0, 'manual')
            self.iio_fmcomms2_source_0.set_gain(0, gain)
        if True:
            self.iio_fmcomms2_source_0.set_gain_mode(1, 'manual')
            self.iio_fmcomms2_source_0.set_gain(1, gain)
        self.iio_fmcomms2_source_0.set_quadrature(True)
        self.iio_fmcomms2_source_0.set_rfdc(True)
        self.iio_fmcomms2_source_0.set_bbdc(True)
        self.iio_fmcomms2_source_0.set_filter_params('Auto', '', 0, 0)
        self.fft_vxx_1 = fft.fft_vcc(fft_size, True, window.hamming(fft_size), True, 4)
        self.fft_vxx_0 = fft.fft_vcc(fft_size, True, window.hamming(fft_size), True, 4)
        self.blocks_stream_to_vector_1 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_size)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_size)
        self.blocks_integrate_xx_1_0_0 = blocks.integrate_ff(decimation, fft_size)
        self.blocks_integrate_xx_1_0 = blocks.integrate_ff(decimation, fft_size)
        self.blocks_head_1 = blocks.head(gr.sizeof_gr_complex*1, fft_size*int(samp_rate*time / fft_size))
        self.blocks_head_0 = blocks.head(gr.sizeof_gr_complex*1, fft_size*int(samp_rate*time / fft_size))
        self.blocks_file_sink_0_0 = blocks.file_sink(gr.sizeof_float*fft_size, "cal_spectrum_{}_{}_{}.dat".format(tuning_freq, samp_rate, fft_size), False)
        self.blocks_file_sink_0_0.set_unbuffered(True)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_float*fft_size, "sky_spectrum_{}_{}_{}.dat".format(tuning_freq, samp_rate, fft_size), False)
        self.blocks_file_sink_0.set_unbuffered(True)
        self.blocks_complex_to_mag_squared_1 = blocks.complex_to_mag_squared(fft_size)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(fft_size)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_integrate_xx_1_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_1, 0), (self.blocks_integrate_xx_1_0_0, 0))
        self.connect((self.blocks_head_0, 0), (self.blocks_stream_to_vector_1, 0))
        self.connect((self.blocks_head_1, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.blocks_integrate_xx_1_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.blocks_integrate_xx_1_0_0, 0), (self.blocks_file_sink_0_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_1, 0))
        self.connect((self.blocks_stream_to_vector_1, 0), (self.fft_vxx_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.fft_vxx_1, 0), (self.blocks_complex_to_mag_squared_1, 0))
        self.connect((self.iio_fmcomms2_source_0, 0), (self.blocks_head_0, 0))
        self.connect((self.iio_fmcomms2_source_0, 1), (self.blocks_head_1, 0))


    def get_fft_size(self):
        return self.fft_size

    def set_fft_size(self, fft_size):
        self.fft_size = fft_size
        self.blocks_file_sink_0.open("sky_spectrum_{}_{}_{}.dat".format(self.tuning_freq, self.samp_rate, self.fft_size))
        self.blocks_file_sink_0_0.open("cal_spectrum_{}_{}_{}.dat".format(self.tuning_freq, self.samp_rate, self.fft_size))
        self.blocks_head_0.set_length(self.fft_size*int(self.samp_rate*self.time / self.fft_size))
        self.blocks_head_1.set_length(self.fft_size*int(self.samp_rate*self.time / self.fft_size))

    def get_filter_bw(self):
        return self.filter_bw

    def set_filter_bw(self, filter_bw):
        self.filter_bw = filter_bw

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.iio_fmcomms2_source_0.set_gain(0, self.gain)
        self.iio_fmcomms2_source_0.set_gain(1, self.gain)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_file_sink_0.open("sky_spectrum_{}_{}_{}.dat".format(self.tuning_freq, self.samp_rate, self.fft_size))
        self.blocks_file_sink_0_0.open("cal_spectrum_{}_{}_{}.dat".format(self.tuning_freq, self.samp_rate, self.fft_size))
        self.blocks_head_0.set_length(self.fft_size*int(self.samp_rate*self.time / self.fft_size))
        self.blocks_head_1.set_length(self.fft_size*int(self.samp_rate*self.time / self.fft_size))
        self.iio_fmcomms2_source_0.set_samplerate(self.samp_rate)

    def get_time(self):
        return self.time

    def set_time(self, time):
        self.time = time
        self.blocks_head_0.set_length(self.fft_size*int(self.samp_rate*self.time / self.fft_size))
        self.blocks_head_1.set_length(self.fft_size*int(self.samp_rate*self.time / self.fft_size))

    def get_tuning_freq(self):
        return self.tuning_freq

    def set_tuning_freq(self, tuning_freq):
        self.tuning_freq = tuning_freq
        self.blocks_file_sink_0.open("sky_spectrum_{}_{}_{}.dat".format(self.tuning_freq, self.samp_rate, self.fft_size))
        self.blocks_file_sink_0_0.open("cal_spectrum_{}_{}_{}.dat".format(self.tuning_freq, self.samp_rate, self.fft_size))
        self.iio_fmcomms2_source_0.set_frequency(self.tuning_freq)

    def get_decimation(self):
        return self.decimation

    def set_decimation(self, decimation):
        self.decimation = decimation



def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--fft-size", dest="fft_size", type=intx, default=512,
        help="Set fft_size [default=%(default)r]")
    parser.add_argument(
        "--filter-bw", dest="filter_bw", type=intx, default=20000000,
        help="Set filter_bw [default=%(default)r]")
    parser.add_argument(
        "--gain", dest="gain", type=eng_float, default=eng_notation.num_to_str(float(32)),
        help="Set gain [default=%(default)r]")
    parser.add_argument(
        "--samp-rate", dest="samp_rate", type=intx, default=2000000,
        help="Set samp_rate [default=%(default)r]")
    parser.add_argument(
        "--time", dest="time", type=intx, default=150,
        help="Set time [default=%(default)r]")
    parser.add_argument(
        "--tuning-freq", dest="tuning_freq", type=intx, default=1420405752,
        help="Set tuning_freq [default=%(default)r]")
    return parser


def main(top_block_cls=start_radio, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(fft_size=options.fft_size, filter_bw=options.filter_bw, gain=options.gain, samp_rate=options.samp_rate, time=options.time, tuning_freq=options.tuning_freq)

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    tb.wait()


if __name__ == '__main__':
    main()
