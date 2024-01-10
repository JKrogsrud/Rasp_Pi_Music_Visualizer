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


def CelestialVisuals(vf, fft_index, amps, buckets_bass, buckets_mid, color_bass, color_mid, color_high):
    im = Image.new("RGB", (32, 32))  # Create new image object
    draw = ImageDraw.Draw(im, None)  # Create a draw object on image

    #  Break the frames into the bass, mid and high range
    vf_bass = vf[:len(buckets_bass)]
    vf_mid = vf[len(buckets_bass):len(buckets_bass)+len(buckets_mid)]
    vf_high = vf[len(buckets_bass) + len(buckets_mid):]


    # Set the Color for the Bass Orbs
    if color_bass == "RED":
        bass_color = (200, 25, 25)
        bass_outline = (250, 25, 25)
    elif color_bass == "GREEN":
        bass_color = (25, 200, 25)
        bass_outline = (25, 250, 25)
    else:
        bass_color = (25, 25, 200)
        bass_outline = (25, 25, 250)

    # Set the Color for the Mid Sun
    if color_mid == "RED":
        mid_color = (200, 25, 25)
        mid_outline = (250, 75, 75)
    elif color_mid == "GREEN":
        mid_color = (25, 200, 25)
        mid_outline = (75, 250, 75)
    else:
        mid_color = (25, 25, 200)
        mid_outline = (75, 75, 250)

    # Set background High Color

    high_scale = sum(vf_high) / len(vf_high)  # Average height of higher frequencies
    if color_high == "RED":
        high_color = (int(100*high_scale), 0, 0)
    elif color_high == "GREEN":
        high_color = (0, int(100*high_scale), 0)
    else:
        high_color = (0, 0, int(100*high_scale))

    # Fill the background with said color
    draw.rectangle([(0, 0), (32, 32)], fill=high_color)

    # Create Bass orbs
    for i in range(len(vf_bass)):
        # Determines the angle each orb should be at
        theta = 2*i*np.pi/len(vf_bass) + 8 * np.pi * (fft_index / len(amps))

        # Center of Bass Orbs
        x_center = (32/3)*np.cos(theta) + 16
        y_center = (32/3)*np.sin(theta) + 16

        if max(vf_bass) > 0:
            radius = 4 * vf_bass[i]/max(vf_bass)
        else:
            radius = 1

        (x1, y1) = (x_center - radius * np.sqrt(2)/2, y_center - radius * np.sqrt(2)/2)
        (x2, y2) = (x_center + radius * np.sqrt(2)/2, y_center + radius * np.sqrt(2)/2)

        draw.ellipse([x1, y1, x2, y2], fill=bass_color, outline=bass_outline)

    # Draw the Midrange Sun
    # Create the polygonal shape for the sun
    polygon_sun = []

    for i in range(len(vf_mid)):
        theta = 2 * i * np.pi / len(vf_mid) - 4 * np.pi * (fft_index / len(amps))
        if max(vf_mid) > 0:
            x = (3 + (16)*vf_mid[i]/max(vf_mid)) * np.cos(theta) + 16
            y = (3 + (16)*vf_mid[i]/max(vf_mid)) * np.sin(theta) + 16
        else:
            x = (1 + (32 / 3) * vf_mid[i] / 1) * np.cos(theta) + 16
            y = (1 + (32 / 3) * vf_mid[i] / 1) * np.sin(theta) + 16

        polygon_sun.append((x, y))

    draw.polygon(polygon_sun, fill=mid_color, outline=mid_outline)

    return im


class CelestialOrbs:
    def __init__(self, song, color_bass, color_mid, color_high):

        self.song = song  # Name of sonf

        #  Colors received from color options: RED, GREEN, BLUE
        self.color_bass = color_bass
        self.color_mid = color_mid
        self.color_high = color_high

        #  Read in music file (wav only for now)
        self.amps, self.sample_rate = sf.read(song)

        #  Flatten it, if needed
        if len(np.shape(self.amps)) > 1:
            self.amps = self.amps[:, 0] + self.amps[:, 1]

        self.fft_index = 0  # Current position of the visualizer
        self.song_length = len(self.amps)  # Length of song in terms of frames in amplitude array
        #  self.elapsed_time = 0  # Guess on how far we are through the song

        #  Buckets are lists of endpoints used to establish what frequency ranges
        #  we care about in the process of visualizing
        self.buckets_bass = vt.linear_buckets(60, 250, 10)  # Break the Bass range into 10 buckets
        self.buckets_mid = vt.linear_buckets(260, 2000, 100)  # Break the midrange into 100 buckets
        self.buckets_high = vt.linear_buckets(2050, 6000, 5)  # Break the high range and presence into 5 buckets

        #  Create one large list
        self.big_bucket = self.buckets_bass + self.buckets_mid + self.buckets_high

        fft_timing_start = time.time()  # Start a timer to measure how long a single FFT takes
        #  Create first FFT array
        self.chunk_bucket = vt.bucket_chunk(self.amps, self.fft_index, self.big_bucket)
        fft_timing_end = time.time()  # End timer
        self.fft_timing = fft_timing_end - fft_timing_start  # Number of seconds it takes to perform the FFT

        self.max_amp = max(self.chunk_bucket)  # Current max amplitude for scaling purposes


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

        while self.fft_index + self.buckets_high[-1]*2 < self.song_length:
            # Create a visual frame for each range, scale them by a little over the max to keep in range
            vf = vt.scaled_frequencies(self.chunk_bucket, 1.25*self.max_amp, 100)

            im = CelestialVisuals(vf, self.fft_index, self.amps, self.buckets_bass, self.buckets_mid, self.color_bass, self.color_mid, self.color_high)
            im = ImageOps.flip(im)  # Flip the image so the bars move from the floor up
            offset_canvas.SetImage(im, 0, unsafe=False)  # Project the image to the RGB-Matrix
            offset_canvas = matrix.SwapOnVSync(offset_canvas)  # Update the matrix

            # Update frames to make the next visual frame
            time_frame_end = time.time()
            elapsed_time = time_frame_end - time_frame_start
            # Update the current index to keep up with the song
            self.fft_index = int(elapsed_time * self.sample_rate) + int(self.fft_timing * self.sample_rate)

            # Take FFT of amps starting at index up to max of bucket
            self.chunk_bucket = vt.bucket_chunk(self.amps, self.fft_index, self.big_bucket)
            self.max_amp = (self.max_amp + max(self.chunk_bucket))/2  # Average the two max amps

