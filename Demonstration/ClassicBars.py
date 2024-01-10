#!/usr/bin/env python

import time
import sys
import os
import numpy as np
from PIL import Image
from PIL import ImageDraw
from PIL import ImageOps
import VisualizerTools as vt
import soundfile as sf
import pygame

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
from rgbmatrix import RGBMatrix, RGBMatrixOptions


def CreateBars(array, color):
    im = Image.new("RGB", (32, 32))
    draw = ImageDraw.Draw(im, None)
    max_height = max(max(array), 1)

    for x in range(len(array)):
        x1 = 2 * x
        x2 = x * 2 + 1
        y1 = 0
        y2 = int(array[x])

        # Color will be given as RED, GREEN, BLUE
        if color == "RED":
            fill = (255 - int(100*x/len(array)), 10 + int((y2 / max_height) * 180), int((y2 / max_height) * 180))
        elif color == "GREEN":
            fill = (10 + int((y2 / max_height) * 180), 255 - int(175 * x / len(array)), int((y2 / max_height) * 180))
        else:
            fill = (10 + int((y2 / max_height) * 180), int((y2 / max_height) * 180), 255 - int(175 * x / len(array)))
        draw.rectangle([x1, y1, x2, y2], fill, width=0)
    return im

class ClassicBars:
    def __init__(self, song, small_freq, large_freq, color):
        self.song = song  # Song file to pass into soundfile module

        self.lower_bound = int(small_freq)
        self.upper_bound = int(large_freq)

        self.color = color

        #  Read in music file (wav only for now)
        self.amps, self.sample_rate = sf.read(song)

        #  Flatten it, if needed
        if len(np.shape(self.amps)) > 1:
            self.amps = self.amps[:, 0] + self.amps[:, 1]

        self.fft_index = 0  # Current position of the visualizer
        self.song_length = len(self.amps)  # Length of song in terms of frames in amplitude array

        #  Buckets are lists of endpoints used to establish what frequency ranges
        #  we care about in the process of visualizing
        self.bucket = vt.linear_buckets(self.lower_bound, self.upper_bound, 16)

        #  Start at the beginning
        self.fft_index = 0

        fft_timing_start = time.time()
        self.chunk_bucket = vt.bucket_chunk(self.amps, self.fft_index, self.bucket)
        fft_timing_end = time.time()
        self.fft_timing = fft_timing_end - fft_timing_start

        self.max_amp = max(max(self.chunk_bucket), 1)

    def run(self):

        # Object for control over the LED Matrix
        options = RGBMatrixOptions()

        # The following are all options for control over the LED Matrix, most of these are left as their defaults
        options.hardware_mapping = 'adafruit-hat'
        options.rows = 32
        options.cols = 32
        options.chain_length = 1
        options.parallel = 1
        options.row_address_type = 0
        options.multiplexing = 0
        options.pwm_bits = 11
        options.brightness = 100
        options.pwm_lsb_nanoseconds = 130
        options.led_rgb_sequence = "RGB"
        options.pixel_mapper_config = ""
        options.gpio_slowdown = 2

        # Set the following options for an instance of out matrix
        matrix = RGBMatrix(options=options)

        #  Initialize the canvas
        offset_canvas = matrix.CreateFrameCanvas()

        time_frame_start = time.time()

        pygame.mixer.init()
        pygame.mixer.music.load(self.song)
        pygame.mixer.music.play()

        while self.fft_index + self.bucket[-1]*2 < self.song_length:
            # Create a visual frame
            vf = vt.scaled_frequencies(self.chunk_bucket, 1.25*self.max_amp, 32)

            im = CreateBars(vf, self.color)  # Create an image of colorful bars
            im = ImageOps.flip(im)  # Flip the image so the bars move from the floor up
            offset_canvas.SetImage(im, 0, unsafe=False)  # Project the image to the RGB-Matrix
            offset_canvas = matrix.SwapOnVSync(offset_canvas)  # Update the matrix

            # Update frames to make the next visual frame
            time_frame_end = time.time()
            elapsed_time = time_frame_end - time_frame_start
            # Update the current index to keep up with the song
            self.fft_index = int(elapsed_time * self.sample_rate)
            # + int(self.fft_timing * self.sample_rate)

            # Take FFT of amps starting at fft_index up to max of bucket
            self.chunk_bucket = vt.bucket_chunk(self.amps, self.fft_index, self.bucket)
            self.max_amp = (self.max_amp + max(self.chunk_bucket))/2  # Average the two max amps

