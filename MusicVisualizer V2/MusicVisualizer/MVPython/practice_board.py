#!/usr/bin/env python
from samplebase import SampleBase
import time
import numpy as np
import PIL
import random
from PIL import Image
from PIL import ImageDraw
from PIL import ImageOps
from FrequencyArray import freq_array
import soundfile as sf

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
        offset_canvas = self.matrix.CreateFrameCanvas()
        amplitudes, frame_rate = sf.read("UpbeatFunk.wav")
        song_bars = freq_array(frame_rate, amplitudes, 10)

        for array in song_bars:
            im = CreateBars(array)
            im = ImageOps.flip(im)
            offset_canvas.SetImage(im,0)
            offset_canvas = self.matrix.SwapOnVSync(offset_canvas)
            time.sleep(0.1)
# Main
if __name__ == "__main__":
    practice_board = PracticeBoard()
    if (not practice_board.process()):
        practice_board.process()

