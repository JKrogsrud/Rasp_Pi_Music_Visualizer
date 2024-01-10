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

def update_frame(visual_frame, fft_index, amps, image):
    new_image = Image.new("RGB", (32,32))

    shrunk_image = image.resize((28, 28), resample=Image.NEAREST)

    new_image.paste(shrunk_image, (2, 2))
    draw = ImageDraw.Draw(image, None)

    sub_bass_vf = visual_frame[:2]
    bass_vf = visual_frame[2:4]
    mid_vf = visual_frame[4:6]
    high_vf = visual_frame[6:]

    # Draw a flying circle for each frequency range
    x = int(32 * sub_bass_vf[0] / max(visual_frame))
    y = int(32 * sub_bass_vf[1] / max(visual_frame))

    color = (25, 70 + int(20 * np.sin(fft_index/(333*np.pi))), int(170 + 85 * np.sin(fft_index/(333*np.pi))))

    draw.rectangle([x, y, x+2, y+2], color)

    # Draw a flying circle for each frequency range
    x = int(32 * bass_vf[0] / max(visual_frame))
    y = int(32 * bass_vf[1] / max(visual_frame))

    color = (25, 60 + int(20 * np.sin(fft_index / (79*np.pi))), 140 + 55 * int(np.sin(fft_index/(57*np.pi))))

    draw.rectangle([x, y, x + 2, y + 2], color)

    # Draw a flying circle for each frequency range
    x = int(32 * mid_vf[0] / max(visual_frame))
    y = int(32 * mid_vf[1] / max(visual_frame))

    color = (30 + int(25 * np.sin(fft_index/(17*np.pi))), 60 + int(20 * np.sin(fft_index/(3*np.pi))), 25)

    draw.rectangle([x, y, x + 2, y + 2], color)

    # Draw a flying circle for each frequency range
    x = int(32 * high_vf[0] / max(visual_frame))
    y = int(32 * high_vf[1] / max(visual_frame))

    color = (100 + int(55 * np.sin(fft_index/(37*np.pi))), 50 + int(55 * np.cos(fft_index/(39*np.pi))), 25)

    draw.rectangle([x, y, x + 2, y + 2], color)

    return image

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
        # buckets = vt.default_buckets()
        sub_bass_buckets = vt.linear_buckets(20, 60, 2)
        bass_buckets = vt.linear_buckets(80, 250, 2)
        mid_buckets = vt.linear_buckets(300, 2000, 3)
        high_buckets = vt.linear_buckets(2500, 6000, 2)

        buckets = sub_bass_buckets + bass_buckets + mid_buckets + high_buckets

        #  Start at the beginning
        fft_index = 0

        fft_timing_start = time.time()
        chunk_bucket = vt.bucket_chunk(amps, fft_index, buckets)
        max_amp = max(chunk_bucket)
        fft_timing_end = time.time()

        fft_timing = fft_timing_end - fft_timing_start

        time_frame_start = time.time()

        image = Image.new("RGB", (32, 32))

        pygame.mixer.init()
        pygame.mixer.music.load("africa-toto.wav")
        pygame.mixer.music.play()

        while fft_index + buckets[-1]*2 < len(amps):
            # Create a visual frame
            visual_frame = vt.scaled_frequencies(chunk_bucket, max_amp, 32)
            im = update_frame(visual_frame, fft_index, amps, image)  # Create an image of colorful bars
            im = ImageOps.flip(im)  # Flip the image so the bars move from the floor up
            offset_canvas.SetImage(im, 0)  # Project the image to the RGB-Matrix
            offset_canvas = self.matrix.SwapOnVSync(offset_canvas)  # Update the matrix

            # Update frames to make the next visual frame
            time_frame_end = time.time()
            elapsed_time = time_frame_end - time_frame_start
            fft_index = int(elapsed_time * sample_rate) + int(fft_timing * sample_rate)
            chunk_bucket = vt.bucket_chunk(amps, fft_index, buckets)
            max_amp = 1.15 * ((max_amp*2 + max(chunk_bucket))/3)

# Main
if __name__ == "__main__":
    practice_board = PracticeBoard()
    if (not practice_board.process()):
        practice_board.process()

