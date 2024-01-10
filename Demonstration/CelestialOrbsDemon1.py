#!/usr/bin/env python
from samplebase import SampleBase
import time
import numpy as np
from PIL import Image
from PIL import ImageDraw
from PIL import ImageOps
import VisualizerTools as vt
import soundfile as sf
import pygame
from rgbmatrix import RGBMatrix, RGBMatrixOptions


def CelestialVisuals(vf, fft_index, amps, buckets_bass, buckets_mid):
    im = Image.new("RGB", (32, 32))
    draw = ImageDraw.Draw(im, None)

    #  Break the frames into the bass, mid and high range
    vf_bass = vf[:len(buckets_bass)]
    vf_mid = vf[len(buckets_bass):len(buckets_bass) + len(buckets_mid)]
    vf_high = vf[len(buckets_bass) + len(buckets_mid):]

    # Bass Color (BLUE)
    bass_color = (20, 2, 200)
    bass_outline = (25, 25, 250)

    # Set background High Color (RED)
    high_scale = sum(vf_high) / len(vf_high)  # Average height of higher frequencies
    high_color = (int(50 * high_scale), 10, 10)

    # Color for Mids (GREEN)
    mid_color = (25, 200, 25)
    mid_outline = (75, 250, 75)

    # Fill the background with said color
    draw.rectangle([(0, 0), (32, 32)], fill=high_color)

    # Create Bass orbs
    for i in range(len(vf_bass)):
        # Determines the angle each orb should be at
        theta = 2 * i * np.pi / len(vf_bass) + 8 * np.pi * (fft_index / len(amps))

        # Center of Bass Orbs
        x_center = (32 / 3) * np.cos(theta) + 16
        y_center = (32 / 3) * np.sin(theta) + 16

        if max(vf_bass) > 0:
            radius = 4 * vf_bass[i] / max(vf_bass)
        else:
            radius = 1

        (x1, y1) = (x_center - radius * np.sqrt(2) / 2, y_center - radius * np.sqrt(2) / 2)
        (x2, y2) = (x_center + radius * np.sqrt(2) / 2, y_center + radius * np.sqrt(2) / 2)

        draw.ellipse([x1, y1, x2, y2], fill=bass_color, outline=bass_outline)

    # Draw the Midrange Sun
    # Create the polygonal shape for the sun
    polygon_sun = []

    for i in range(len(vf_mid)):
        theta = 2 * i * np.pi / len(vf_mid) - 4 * np.pi * (fft_index / len(amps))
        if max(vf_mid) > 0:
            x = (3 + (16) * vf_mid[i] / max(vf_mid)) * np.cos(theta) + 16
            y = (3 + (16) * vf_mid[i] / max(vf_mid)) * np.sin(theta) + 16
        else:
            x = (1 + (32 / 3) * vf_mid[i] / 1) * np.cos(theta) + 16
            y = (1 + (32 / 3) * vf_mid[i] / 1) * np.sin(theta) + 16

        polygon_sun.append((x, y))

    draw.polygon(polygon_sun, fill=mid_color, outline=mid_outline)

    return im

class PracticeBoard(SampleBase):
    def __init__(self, *args, **kwargs):
        super(PracticeBoard, self).__init__(*args, **kwargs)

    def run(self):

        # Song to be imported
        song = "africa-toto.wav"

        # Read in music file
        amps, sample_rate = sf.read(song)

        # Flatten if needed
        if len(np.shape(amps)) > 1:
            amps = amps[:, 0] + amps[:, 1]

        fft_index = 0  # Current position of the visualizer
        song_length = len(amps)  # Length of song in terms of frames in amplitude array

        buckets_bass = vt.linear_buckets(60, 250, 10) # Break the Bass range into 10 buckets
        buckets_mid = vt.linear_buckets(260, 2000, 100) # Break the midrange into 100 buckets
        buckets_high = vt.linear_buckets(2050, 6000, 5) # Break the high range and presence into 5 buckets

        big_bucket = buckets_bass + buckets_mid + buckets_high
        fft_timing_start = time.time()
        chunk_bucket = vt.bucket_chunk(amps, fft_index, big_bucket)
        fft_timing_end = time.time()
        fft_timing = fft_timing_end - fft_timing_start
        max_amp = max(chunk_bucket)

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
        pygame.mixer.music.load(song)
        pygame.mixer.music.play()

        while fft_index + buckets_high[-1]*2 < song_length:
            # Create a visual frame for each range, scale them by a little over the max to keep in range
            vf = vt.scaled_frequencies(chunk_bucket, 1.25*max_amp, 100)

            im = CelestialVisuals(vf, fft_index, amps, buckets_bass, buckets_mid)
            im = ImageOps.flip(im)  # Flip the image so the bars move from the floor up
            offset_canvas.SetImage(im, 0, unsafe=False)  # Project the image to the RGB-Matrix
            offset_canvas = matrix.SwapOnVSync(offset_canvas)  # Update the matrix

            # Update frames to make the next visual frame
            time_frame_end = time.time()
            elapsed_time = time_frame_end - time_frame_start
            # Update the current index to keep up with the song
            fft_index = int(elapsed_time * sample_rate) + int(fft_timing * sample_rate)

            # Take FFT of amps starting at index up to max of bucket
            chunk_bucket = vt.bucket_chunk(amps, fft_index, big_bucket)
            max_amp = (max_amp + max(chunk_bucket))/2  # Average the two max amps


# Main
if __name__ == "__main__":
    practice_board = PracticeBoard()
    if (not practice_board.process()):
        practice_board.process()

