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
def CreateBars(array):
    im = Image.new("RGB", (32, 32))
    draw = ImageDraw.Draw(im,None)

    for x in range(len(array)):
        fill = ((10*(x+1))%255, (15*(x+1))%255, (25*(x+1))%255)
        x1= 2*x
        x2= x*2+1
        y1= 0
        y2= int(array[x])
        draw.rectangle([x1, y1, x2, y2], fill, width=0)
    return im

class PracticeBoard(SampleBase):
    def __init__(self, *args, **kwargs):
        super(PracticeBoard, self).__init__(*args, **kwargs)

    def run(self):

        #  Initialize the canvas
        offset_canvas = self.matrix.CreateFrameCanvas()

        #  Read in music file (wav only for now)
        amps, sample_rate = sf.read("UpbeatFunk.wav")

        #  Flatten it, if needed
        if len(np.shape(amps)) > 1:
            amps = amps[:, 0] + amps[:, 1]

        #  Compute the number of frames to skip between FFT frames (frame_jump)
        frame_rate = 30  # This should be something we can alter
        frame_jump = int(sample_rate / frame_rate)

        #  Buckets should be an option: default, linear bucketing, geometric bucketing
        buckets = vt.default_buckets()

        #  Start at the beginning
        fft_index = 0
        frames = []  # List of FFTs that have been computed to be frames

        #  Peform the first 10 computations so we have a way of scaling the bars
        for i in range(10):
            chunk_bucket = vt.bucket_chunk(amps, fft_index, buckets)
            frames.append(chunk_bucket)
            fft_index += frame_jump
        # After the above, our fft_index is at 10 * frame_jump

        # Determine the starting maximal amps for scaling
        max_amp = vt.max_amps(frames)

        pygame.mixer.init()
        pygame.mixer.music.load("UpbeatFunk.wav")
        pygame.mixer.music.play()

        while fft_index + frame_jump < len(amps):
            # Create a visual frame
            visual_frame = vt.scaled_frequencies(frames[0], max_amp, 32)
            im = CreateBars(visual_frame)  # Create an image of colorful bars
            im = ImageOps.flip(im)  # Flip the image so the bars move from the floor up
            offset_canvas.SetImage(im,0)  # Project the image to the RGB-Matrix
            offset_canvas = self.matrix.SwapOnVSync(offset_canvas)  # Update the matrix

            # Update frames to make the next visual frame
            chunk_bucket = vt.bucket_chunk(amps, fft_index, buckets)
            frames.append(chunk_bucket)
            frames = frames[1:]  # Keep frames at looking just 10 ahead
            if len(frames) == 10:
                max_amp = (vt.max_amps(frames) + 2 * max_amp) / 3
            fft_index += frame_jump  # Jump to next spot we will perform the fft

            time.sleep(0.0233)
# Main
if __name__ == "__main__":
    practice_board = PracticeBoard()
    if (not practice_board.process()):
        practice_board.process()

