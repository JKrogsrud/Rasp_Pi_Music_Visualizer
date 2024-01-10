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


def CelestialVisuals(vf_bass, vf_mid, vf_high, fft_index, amps, max_amp):
    im = Image.new("RGB", (32, 32))
    draw = ImageDraw.Draw(im, None)

    bass_max = max(vf_bass)
    mid_max = max(vf_mid)
    high_max = max(vf_mid)

    #  Create a High end warmth in background
    warmth_scale = max(vf_high) / max(high_max, 1)
    warm_color = (int(100*warmth_scale), 0, 0)

    draw.rectangle([(0, 0), (32, 32)], fill=warm_color)

    # Create Bass orbs
    for i in range(len(vf_bass)):
        theta = 2*i*np.pi/len(vf_bass) + 8 * np.pi * (fft_index / len(amps))  # Center of Bass Orbs

        x_center = (32/3)*np.cos(theta) + 16
        y_center = (32/3)*np.sin(theta) + 16

        radius = 4 * vf_bass[i]/bass_max

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

        x = (1 + (32/3)*vf_mid[i]/mid_max) * np.cos(theta) + 16
        y = (1 + (32/3)*vf_mid[i]/mid_max) * np.sin(theta) + 16

        polygon_sun.append((x, y))

    inside_color = (209, 222, 25)
    outside_color = (255, 128, 0)
    draw.polygon(polygon_sun, fill=inside_color, outline=outside_color)

    return im

class PracticeBoard(SampleBase):
    def __init__(self, *args, **kwargs):
        super(PracticeBoard, self).__init__(*args, **kwargs)

    def run(self):

        #  Initialize the canvas
        offset_canvas = self.matrix.CreateFrameCanvas()

        #  Read in music file (wav only for now)
        amps, sample_rate = sf.read("africa-toto.wav")

        #  Flatten it, if needed
        if len(np.shape(amps)) > 1:
            amps = amps[:, 0] + amps[:, 1]

        #  Buckets should be an option: default, linear bucketing, geometric bucketing
        #buckets = vt.default_buckets()
        buckets_bass = vt.linear_buckets(60, 250, 10)
        buckets_mid = vt.linear_buckets(260, 2000, 100)
        buckets_high = vt.linear_buckets(2050, 6000, 5)

        #  Start at the beginning
        fft_index = 0

        fft_timing_start = time.time()
        chunk_bucket_bass = vt.bucket_chunk(amps, fft_index, buckets_bass)
        chunk_bucket_mid = vt.bucket_chunk(amps, fft_index, buckets_mid)
        chunk_bucket_high = vt.bucket_chunk(amps, fft_index, buckets_high)
        max_amp = 1.25 * max(max(chunk_bucket_bass), max(chunk_bucket_mid), max(chunk_bucket_high)) # Scale the max so when we achieve a max we don't have such large spikes
        fft_timing_end = time.time()

        fft_timing = fft_timing_end - fft_timing_start

        time_frame_start = time.time()

        #pygame.mixer.init()
        #pygame.mixer.music.load("africa-toto.wav")
        #pygame.mixer.music.play()

        while fft_index + buckets_high[-1]*2 < len(amps):
            # Create a visual frame for each range
            vf_bass = vt.scaled_frequencies(chunk_bucket_bass, max_amp, 32)
            vf_mid = vt.scaled_frequencies(chunk_bucket_mid, max_amp, 32)
            vf_high = vt.scaled_frequencies(chunk_bucket_high, max_amp, 32)
            im = CelestialVisuals(vf_bass, vf_mid, vf_high, fft_index, amps, max_amp)
            im = ImageOps.flip(im)  # Flip the image so the bars move from the floor up
            offset_canvas.SetImage(im, 0)  # Project the image to the RGB-Matrix
            offset_canvas = self.matrix.SwapOnVSync(offset_canvas)  # Update the matrix

            # Update frames to make the next visual frame
            time_frame_end = time.time()
            elapsed_time = time_frame_end - time_frame_start
            fft_index = int(elapsed_time * sample_rate) + int(fft_timing * sample_rate)
            chunk_bucket_bass = vt.bucket_chunk(amps, fft_index, buckets_bass)
            chunk_bucket_mid = vt.bucket_chunk(amps, fft_index, buckets_mid)
            chunk_bucket_high = vt.bucket_chunk(amps, fft_index, buckets_high)
            max_amp = 1.25 * (((5/4) * max_amp*2 + max(max(chunk_bucket_bass), max(chunk_bucket_mid), max(chunk_bucket_high)))/3)


# Main
if __name__ == "__main__":
    practice_board = PracticeBoard()
    if (not practice_board.process()):
        practice_board.process()

