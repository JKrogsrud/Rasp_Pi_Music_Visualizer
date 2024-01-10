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

def CelestialVisuals(vf, fft_index, amps, max_amp, buckets_bass, buckets_mid, buckets_high):
    im = Image.new("RGB", (32, 32))
    draw = ImageDraw.Draw(im, None)

    #  Break the frames into the bass, mid and high range
    vf_bass = vf[:len(buckets_bass)]
    vf_mid = vf[len(buckets_bass):len(buckets_bass)+len(buckets_mid)]
    vf_high = vf[len(buckets_bass) + len(buckets_mid):]

    #  using the High frequencies created a background aura in red
    warmth_scale = sum(vf_high) / len(vf_high)
    warm_color = (int(warmth_scale), 0, 0)

    draw.rectangle([(0, 0), (32, 32)], fill=warm_color)

    # Create Bass orbs
    for i in range(len(vf_bass)):
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

        bass_color = (0, 50, 200 - (100 * int(vf_bass[i]/max(max_amp,1))))
        bass_outline = (10, 60, 210 - (100 * int(vf_bass[i]/max(max_amp,1))))
        draw.ellipse([x1, y1, x2, y2], fill=bass_color, outline=bass_outline)

    # Draw the Midrange Sun
    # Create the polygonal shape for the sun
    polygon_sun = []

    for i in range(len(vf_mid)):
        theta = 2 * i * np.pi / len(vf_mid) - 4 * np.pi * (fft_index / len(amps))  # Center of Bass Orbs
        if max(vf_mid) > 0:
            x = (3 + (32/6)*vf_mid[i]/max(vf_mid)) * np.cos(theta) + 16
            y = (3 + (32/6)*vf_mid[i]/max(vf_mid)) * np.sin(theta) + 16
        else:
            x = (1 + (32 / 3) * vf_mid[i] / 1) * np.cos(theta) + 16
            y = (1 + (32 / 3) * vf_mid[i] / 1) * np.sin(theta) + 16

        polygon_sun.append((x, y))

    inside_color = (209, 222, 25)
    outside_color = (255, 128, 0)
    draw.polygon(polygon_sun, fill=inside_color, outline=outside_color)

    return im


class CelestialOrbs():
    def __init__(self):
        pass

    def run(self):
        options = RGBMatrixOptions()

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

        matrix = RGBMatrix(options=options)

        #  Initialize the canvas
        offset_canvas = matrix.CreateFrameCanvas()

        #  Read in music file (wav only for now)
        amps, sample_rate = sf.read("africa-toto.wav")

        #  Flatten it, if needed
        if len(np.shape(amps)) > 1:
            amps = amps[:, 0] + amps[:, 1]

        #  Break buckets up linearly in each frequency range
        buckets_bass = vt.linear_buckets(60, 250, 10)
        buckets_mid = vt.linear_buckets(260, 2000, 100)
        buckets_high = vt.linear_buckets(2050, 6000, 5)

        big_bucket = buckets_bass + buckets_mid + buckets_high
        #  Start at the beginning
        fft_index = 0

        fft_timing_start = time.time()
        chunk_bucket = vt.bucket_chunk(amps, fft_index, big_bucket)

        max_amp = 1.25 * max(chunk_bucket)  # Scale the max so when we achieve a max we don't have such large spikes
        fft_timing_end = time.time()

        fft_timing = fft_timing_end - fft_timing_start

        time_frame_start = time.time()

        # TODO: Figure out why when i use sudo to run this the pygame sound causes an Exception
        #pygame.mixer.init()
        #pygame.mixer.music.load("africa-toto.wav")
        #pygame.mixer.music.play()

        while fft_index + buckets_high[-1]*2 < len(amps):
            # Create a visual frame for each range
            vf = vt.scaled_frequencies(chunk_bucket, max_amp, 100)

            im = CelestialVisuals(vf, fft_index, amps, max_amp, buckets_bass, buckets_mid, buckets_high)
            im = ImageOps.flip(im)  # Flip the image so the bars move from the floor up
            offset_canvas.SetImage(im, 0)  # Project the image to the RGB-Matrix
            offset_canvas = matrix.SwapOnVSync(offset_canvas)  # Update the matrix

            # Update frames to make the next visual frame
            time_frame_end = time.time()
            elapsed_time = time_frame_end - time_frame_start
            fft_index = int(elapsed_time * sample_rate) + int(fft_timing * sample_rate)
            chunk_bucket = vt.bucket_chunk(amps, fft_index, big_bucket)
            max_amp = 1.25*(max_amp + max(chunk_bucket))/2 # Average the two max amps and scale up


# Main
def startCelestialOrbs():
    
    celestial_orb = CelestialOrbs()
    celestial_orb.run()
