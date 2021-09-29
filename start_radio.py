#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Start Radio
# Generated: Wed Sep 29 04:17:28 2021
##################################################


from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import fft
from gnuradio import gr
from gnuradio import iio
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from optparse import OptionParser


class start_radio(gr.top_block):

    def __init__(self, fft_size=512, filter_bw=20000000, gain=64, samp_rate=2000000, time=150, tuning_freq=1420405752):
        gr.top_block.__init__(self, "Start Radio")

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
        self.iio_fmcomms2_source_0 = iio.fmcomms2_source_f32c('ip:192.168.2.1', tuning_freq, samp_rate, filter_bw, True, True, 0x8000, True, True, True, "manual", gain, "manual", gain, "A_BALANCED", '', True)
        self.fft_vxx_1 = fft.fft_vcc(fft_size, True, (window.hamming(fft_size)), True, 4)
        self.fft_vxx_0 = fft.fft_vcc(fft_size, True, (window.hamming(fft_size)), True, 4)
        self.blocks_sub_xx_1 = blocks.sub_ff(1)
        self.blocks_stream_to_vector_1 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_size)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_size)
        self.blocks_integrate_xx_1_0_0 = blocks.integrate_ff(decimation, fft_size)
        self.blocks_integrate_xx_1_0 = blocks.integrate_ff(decimation, fft_size)
        self.blocks_integrate_xx_1 = blocks.integrate_ff(fft_size*decimation, 1)
        self.blocks_head_1 = blocks.head(gr.sizeof_gr_complex*1, fft_size*int(samp_rate*time / fft_size))
        self.blocks_head_0 = blocks.head(gr.sizeof_gr_complex*1, fft_size*int(samp_rate*time / fft_size))
        self.blocks_file_sink_1 = blocks.file_sink(gr.sizeof_float*1, "combined_power_{}_{}_{}.dat".format(tuning_freq, samp_rate, fft_size), False)
        self.blocks_file_sink_1.set_unbuffered(False)
        self.blocks_file_sink_0_0 = blocks.file_sink(gr.sizeof_float*fft_size, "cal_spectrum_{}_{}_{}.dat".format(tuning_freq, samp_rate, fft_size), False)
        self.blocks_file_sink_0_0.set_unbuffered(False)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_float*fft_size, "sky_spectrum_{}_{}_{}.dat".format(tuning_freq, samp_rate, fft_size), False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.blocks_complex_to_mag_squared_3 = blocks.complex_to_mag_squared(1)
        self.blocks_complex_to_mag_squared_2 = blocks.complex_to_mag_squared(1)
        self.blocks_complex_to_mag_squared_1 = blocks.complex_to_mag_squared(fft_size)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(fft_size)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_integrate_xx_1_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_1, 0), (self.blocks_integrate_xx_1_0_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_2, 0), (self.blocks_sub_xx_1, 1))
        self.connect((self.blocks_complex_to_mag_squared_3, 0), (self.blocks_sub_xx_1, 0))
        self.connect((self.blocks_head_0, 0), (self.blocks_complex_to_mag_squared_3, 0))
        self.connect((self.blocks_head_0, 0), (self.blocks_stream_to_vector_1, 0))
        self.connect((self.blocks_head_1, 0), (self.blocks_complex_to_mag_squared_2, 0))
        self.connect((self.blocks_head_1, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.blocks_integrate_xx_1, 0), (self.blocks_file_sink_1, 0))
        self.connect((self.blocks_integrate_xx_1_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.blocks_integrate_xx_1_0_0, 0), (self.blocks_file_sink_0_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_1, 0))
        self.connect((self.blocks_stream_to_vector_1, 0), (self.fft_vxx_0, 0))
        self.connect((self.blocks_sub_xx_1, 0), (self.blocks_integrate_xx_1, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.fft_vxx_1, 0), (self.blocks_complex_to_mag_squared_1, 0))
        self.connect((self.iio_fmcomms2_source_0, 0), (self.blocks_head_0, 0))
        self.connect((self.iio_fmcomms2_source_0, 1), (self.blocks_head_1, 0))

    def get_fft_size(self):
        return self.fft_size

    def set_fft_size(self, fft_size):
        self.fft_size = fft_size
        self.blocks_head_1.set_length(self.fft_size*int(self.samp_rate*self.time / self.fft_size))
        self.blocks_head_0.set_length(self.fft_size*int(self.samp_rate*self.time / self.fft_size))
        self.blocks_file_sink_1.open("combined_power_{}_{}_{}.dat".format(self.tuning_freq, self.samp_rate, self.fft_size))
        self.blocks_file_sink_0_0.open("cal_spectrum_{}_{}_{}.dat".format(self.tuning_freq, self.samp_rate, self.fft_size))
        self.blocks_file_sink_0.open("sky_spectrum_{}_{}_{}.dat".format(self.tuning_freq, self.samp_rate, self.fft_size))

    def get_filter_bw(self):
        return self.filter_bw

    def set_filter_bw(self, filter_bw):
        self.filter_bw = filter_bw
        self.iio_fmcomms2_source_0.set_params(self.tuning_freq, self.samp_rate, self.filter_bw, True, True, True, "manual", self.gain, "manual", self.gain, "A_BALANCED", '', True)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.iio_fmcomms2_source_0.set_params(self.tuning_freq, self.samp_rate, self.filter_bw, True, True, True, "manual", self.gain, "manual", self.gain, "A_BALANCED", '', True)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.iio_fmcomms2_source_0.set_params(self.tuning_freq, self.samp_rate, self.filter_bw, True, True, True, "manual", self.gain, "manual", self.gain, "A_BALANCED", '', True)
        self.blocks_head_1.set_length(self.fft_size*int(self.samp_rate*self.time / self.fft_size))
        self.blocks_head_0.set_length(self.fft_size*int(self.samp_rate*self.time / self.fft_size))
        self.blocks_file_sink_1.open("combined_power_{}_{}_{}.dat".format(self.tuning_freq, self.samp_rate, self.fft_size))
        self.blocks_file_sink_0_0.open("cal_spectrum_{}_{}_{}.dat".format(self.tuning_freq, self.samp_rate, self.fft_size))
        self.blocks_file_sink_0.open("sky_spectrum_{}_{}_{}.dat".format(self.tuning_freq, self.samp_rate, self.fft_size))

    def get_time(self):
        return self.time

    def set_time(self, time):
        self.time = time
        self.blocks_head_1.set_length(self.fft_size*int(self.samp_rate*self.time / self.fft_size))
        self.blocks_head_0.set_length(self.fft_size*int(self.samp_rate*self.time / self.fft_size))

    def get_tuning_freq(self):
        return self.tuning_freq

    def set_tuning_freq(self, tuning_freq):
        self.tuning_freq = tuning_freq
        self.iio_fmcomms2_source_0.set_params(self.tuning_freq, self.samp_rate, self.filter_bw, True, True, True, "manual", self.gain, "manual", self.gain, "A_BALANCED", '', True)
        self.blocks_file_sink_1.open("combined_power_{}_{}_{}.dat".format(self.tuning_freq, self.samp_rate, self.fft_size))
        self.blocks_file_sink_0_0.open("cal_spectrum_{}_{}_{}.dat".format(self.tuning_freq, self.samp_rate, self.fft_size))
        self.blocks_file_sink_0.open("sky_spectrum_{}_{}_{}.dat".format(self.tuning_freq, self.samp_rate, self.fft_size))

    def get_decimation(self):
        return self.decimation

    def set_decimation(self, decimation):
        self.decimation = decimation


def argument_parser():
    parser = OptionParser(usage="%prog: [options]", option_class=eng_option)
    parser.add_option(
        "", "--fft-size", dest="fft_size", type="intx", default=512,
        help="Set fft_size [default=%default]")
    parser.add_option(
        "", "--filter-bw", dest="filter_bw", type="intx", default=20000000,
        help="Set filter_bw [default=%default]")
    parser.add_option(
        "", "--gain", dest="gain", type="eng_float", default=eng_notation.num_to_str(64),
        help="Set gain [default=%default]")
    parser.add_option(
        "", "--samp-rate", dest="samp_rate", type="intx", default=2000000,
        help="Set samp_rate [default=%default]")
    parser.add_option(
        "", "--time", dest="time", type="intx", default=150,
        help="Set time [default=%default]")
    parser.add_option(
        "", "--tuning-freq", dest="tuning_freq", type="intx", default=1420405752,
        help="Set tuning_freq [default=%default]")
    return parser


def main(top_block_cls=start_radio, options=None):
    if options is None:
        options, _ = argument_parser().parse_args()

    tb = top_block_cls(fft_size=options.fft_size, filter_bw=options.filter_bw, gain=options.gain, samp_rate=options.samp_rate, time=options.time, tuning_freq=options.tuning_freq)
    tb.start()
    tb.wait()


if __name__ == '__main__':
    main()
