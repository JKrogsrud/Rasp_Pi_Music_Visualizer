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

# Fix this so it can be adjusted!
def CreateBars(array, fft_index, amps):
    im = Image.new("RGB", (32, 32))
    draw = ImageDraw.Draw(im,None)
    max_height = max(array)

    for x in range(len(array)):
        x1 = 2 * x
        x2 = x * 2 + 1
        y1 = 0
        y2 = int(array[x])
        fill = (int((y2/max_height) * 120), 55 + int(200*x/len(array)), int(255 * fft_index/len(amps)))
        draw.rectangle([x1, y1, x2, y2], fill, width=0)
    return im

def RadialVisuals(array, fft_index, amps, max_amp):
    im = Image.new("HSV", (32, 32))
    draw = ImageDraw.Draw(im, None)
    max_height = max(array)

    polygon = []
    polygon2 = []
    for i in range(len(array)):
        theta = 2*i*np.pi/len(array)
        x = (1 + array[i]/3)*np.cos(theta)+16
        y = (1 + array[i]/3)*np.sin(theta)+16

        x2 = (4 + array[i]/3)*np.cos(theta)+16
        y2 = (4 + array[i]/3)*np.sin(theta)+16
        polygon.append((x,y))
        polygon2.append((x2,y2))

    fill = (120, 100, 100)
    draw.polygon(polygon, fill=fill, outline=None)
    outline = (240, 100, 1000)
    draw.polygon(polygon2, fill=None, outline=outline)
    im = im.convert('RGB')
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
        buckets = vt.linear_buckets(200, 1000, 100)

        #  Start at the beginning
        fft_index = 0

        fft_timing_start = time.time()
        chunk_bucket = vt.bucket_chunk(amps, fft_index, buckets)
        max_amp = max(chunk_bucket)
        fft_timing_end = time.time()

        fft_timing = fft_timing_end - fft_timing_start

        time_frame_start = time.time()

        pygame.mixer.init()
        pygame.mixer.music.load("africa-toto.wav")
        pygame.mixer.music.play()

        while fft_index + buckets[-1]*2 < len(amps):
            # Create a visual frame
            visual_frame = vt.scaled_frequencies(chunk_bucket, max_amp, 32)
            #im = CreateBars(visual_frame, fft_index, amps)  # Create an image of colorful bars
            im = RadialVisuals(visual_frame, fft_index, amps, max_amp)
            im = ImageOps.flip(im)  # Flip the image so the bars move from the floor up
            offset_canvas.SetImage(im, 0)  # Project the image to the RGB-Matrix
            offset_canvas = self.matrix.SwapOnVSync(offset_canvas)  # Update the matrix

            time.sleep(0.01)

            # Update frames to make the next visual frame
            time_frame_end = time.time()
            elapsed_time = time_frame_end - time_frame_start
            fft_index = int(elapsed_time * sample_rate) + int(fft_timing * sample_rate)
            chunk_bucket = vt.bucket_chunk(amps, fft_index, buckets)
            max_amp = (max_amp*2 + max(chunk_bucket))/3


# Main
if __name__ == "__main__":
    practice_board = PracticeBoard()
    if (not practice_board.process()):
        practice_board.process()

