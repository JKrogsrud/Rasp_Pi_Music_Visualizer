from flask import Flask, render_template, request, json
from CelestialOrbsV3 import *
from ClassicBars import *
import os.path
import sys
import alsaaudio

orbs = CelestialOrbs('UpbeatFunk.wav','RED','BLUE','GREEN')
orbs.run()