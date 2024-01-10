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


def CreateBars(array):
    im = Image.new("RGB", (32, 32))
    draw = ImageDraw.Draw(im, None)
    max_height = max(max(array), 1)

    for x in range(len(array)):
        x1 = 2 * x
        x2 = x * 2 + 1
        y1 = 0
        y2 = int(array[x])

        fill = (10 + int((y2 / max_height) * 180), int((y2 / max_height) * 180), 255 - int(175 * x / len(array)))
        draw.rectangle([x1, y1, x2, y2], fill, width=0)
    return im

class PracticeBoard(SampleBase):
    def __init__(self, *args, **kwargs):
        super(PracticeBoard, self).__init__(*args, **kwargs)

    def run(self):
        song = "africa-toto.wav"  # Song file to pass into soundfile module

        lower_bound = int(50)
        upper_bound = int(2000)

        #  Read in music file (wav only for now)
        amps, sample_rate = sf.read(song)

        #  Flatten it, if needed
        if len(np.shape(amps)) > 1:
            amps = amps[:, 0] + amps[:, 1]

        song_length = len(amps)  # Length of song in terms of frames in amplitude array

        #  Buckets are lists of endpoints used to establish what frequency ranges
        #  we care about in the process of visualizing
        bucket = vt.linear_buckets(lower_bound, upper_bound, 16)

        #  Start at the beginning
        fft_index = 0

        chunk_bucket = vt.bucket_chunk(amps, fft_index, bucket)

        max_amp = max(max(chunk_bucket), 1)

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

        while fft_index + bucket[-1]*2 < song_length:
            # Create a visual frame
            vf = vt.scaled_frequencies(chunk_bucket, 1.25*max_amp, 32)

            im = CreateBars(vf)  # Create an image of colorful bars
            im = ImageOps.flip(im)  # Flip the image so the bars move from the floor up
            offset_canvas.SetImage(im, 0, unsafe=False)  # Project the image to the RGB-Matrix
            offset_canvas = matrix.SwapOnVSync(offset_canvas)  # Update the matrix

            # Update frames to make the next visual frame
            time_frame_end = time.time()
            elapsed_time = time_frame_end - time_frame_start
            # Update the current index to keep up with the song
            fft_index = int(elapsed_time * sample_rate)
            # + int(fft_timing * sample_rate)

            # Take FFT of amps starting at fft_index up to max of bucket
            chunk_bucket = vt.bucket_chunk(amps, fft_index, bucket)
            max_amp = (max_amp + max(chunk_bucket))/2  # Average the two max amps


# Main
if __name__ == "__main__":
    practice_board = PracticeBoard()
    if (not practice_board.process()):
        practice_board.process()

