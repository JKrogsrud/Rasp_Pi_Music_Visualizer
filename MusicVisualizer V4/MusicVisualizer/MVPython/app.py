from flask import Flask, render_template, request, json
from CelestialOrbsV3 import *
from ClassicBars import *
import os.path
import sys
import alsaaudio

app = Flask(__name__)
UPLOAD_FOLDER = "/home/pi/MusicVisualizer/uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


class Audio:
    def __init__(self, file, filename, filesize):
        self.status = False
        self.file = file
        self.filename = filename
        self.filesize = filesize
        
    def get_status(self): 
        return self.status
    
    def set_status(self, status):
        self.status = status

    def get_file(self):
        return self.file

    def set_file(self, file):
        self.file = file
        
    def get_filename(self):
        return self.filename
    
    def set_filename(self, filename):
        self.filename = filename

    def get_filesize(self):
        return self.filesize

    def set_filesize(self, filesize):
        self.filesize = filesize

    def to_string(self):
        if self.filename is None:
            filename = "None"
        else:
            filename = self.filename
        if self.file is None:
            file = "None"
        else:
            file = str(self.file)
        return str(self.status) + " " + filename + " " + file


class Control:
    def __init__(self, file):
        self.file = file
        self.visual = None
        self.option1 = None  # low_range  # bass_color
        self.option2 = None  # high_range # mid_color
        self.option3 = None  # color      # treble_color
        self.playing = False

    def visualize_audio(self):
        if self.visual == "CELESTIAL ORBS":
            print(self.option1, self.option2, self.option3, file=sys.stdout)
            orbs = CelestialOrbs(UPLOAD_FOLDER + "/" + self.file.get_filename(), self.option1, self.option2, self.option3)
            orbs.run()
            print("DONE", file=sys.stdout)

        elif self.visual == "CLASSIC BARS":
            bars = ClassicBars(UPLOAD_FOLDER + "/" + self.file.get_filename(), self.option1, self.option2, self.option3)
            bars.run()



    def play_audio(self):
        self.playing = True
        self.visualize_audio()
        self.playing = False

    def get_file(self):
        return self.file

    def set_visual(self, v):
        self.visual = v

    def set_option1(self, op1):
        self.option1 = op1

    def set_option2(self, op2):
        self.option2 = op2

    def set_option3(self, op3):
        self.option3 = op3



class Volume:
    def __init__(self, cur_vol):
        self.cur_vol = cur_vol
        self.mixer = alsaaudio.Mixer()

    def get_vol(self):
        return self.cur_vol

    def set_vol(self, vol):
        self.cur_vol = vol
        self.mixer.setvolume(self.cur_vol)

    def vol_up(self):
        if self.cur_vol < 100:
            self.cur_vol += 10
            self.mixer.setvolume(self.cur_vol)

    def vol_down(self):
        if self.cur_vol > 0:
            self.cur_vol -= 10
            self.mixer.setvolume(self.cur_vol)


audio1 = Audio(file=None, filename=None, filesize=None)
audio2 = Audio(file=None, filename=None, filesize=None)
audio3 = Audio(file=None, filename=None, filesize=None)
audio4 = Audio(file=None, filename=None, filesize=None)
audio5 = Audio(file=None, filename=None, filesize=None)
audio_list = [audio1, audio2, audio3, audio4, audio5]

control1 = Control(file=audio1)
control2 = Control(file=audio2)
control3 = Control(file=audio3)
control4 = Control(file=audio4)
control5 = Control(file=audio5)
control_list = [control1, control2, control3, control4, control5]

volume = Volume(50)


@app.route("/", methods=["GET"])
def initial():
    return render_template("smartSpeaker.html")


@app.route("/uploadInfo", methods=["POST", "GET"])
def uploadInfo():
    if request.method == "POST":
        # Returned from data of /uploadInfo post
        filename = request.values["fileName"]
        filesize = request.values["fileSize"]
        file_inputted = False
        for audio in audio_list:
            if file_inputted is False and audio.get_status() is False:
                audio.set_filename(filename)
                audio.set_filesize(filesize)
                audio.set_status(True)
                file_inputted = True
        return "success"
    elif request.method == "GET":
        return_array = {
            "audioFiles": [
            ]
        }
        for audio in audio_list:
            if audio.get_status() is True:
                return_array["audioFiles"].append({"name": audio.get_filename(),
                                                   "size": audio.get_filesize()})
        return json.dumps(return_array)


@app.route("/uploadFile", methods=["POST"])
def uploadFile():
    file = request.files["myFile"]
    file_inputted = False
    it = len(audio_list) - 1
    while file_inputted is False:
        if audio_list[it].get_status() is True:
            audio_list[it].set_file(file)
            file_inputted = True
        else:
            it -= 1
    print("Successful File Upload", file=sys.stdout)
    print(audio_list[it].get_filename(), file=sys.stdout)
    print(audio_list[it].get_file(), file=sys.stdout)
    for audio in audio_list:
        print(audio.to_string(), file=sys.stdout)
    if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], file.filename)):
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return "success"
    else:
        return "file already present"


@app.route("/deleteFile", methods=["POST", "GET"])
def deleteFile():
    if request.method == "POST":
        str_position = request.values["position"]
        index_to_delete = int(str_position)
        audio = audio_list[index_to_delete]
        # Delete audio object contents and file
        audio.set_status(False)
        can_remove = True
        for audioObj in audio_list:
            if audioObj != audio and audioObj.get_file() == audio.get_file():
                can_remove = False
        if can_remove is True:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], audio.get_file().filename))
        print("Deleted File: " + audio.get_file().filename, file=sys.stdout)
        audio.set_file(None)
        audio.set_filename(None)
        audio.set_filesize(None)
        # Move down to fill empty spaces
        next_empty = index_to_delete
        for i in range(index_to_delete + 1, len(audio_list)):
            if audio_list[i].get_status() is True:
                audio_list[next_empty].set_status(audio_list[i].get_status())
                audio_list[next_empty].set_file(audio_list[i].get_file())
                audio_list[next_empty].set_filename(audio_list[i].get_filename())
                audio_list[next_empty].set_filesize(audio_list[i].get_filesize())
                audio_list[i].set_status(False)
                audio_list[i].set_file(None)
                audio_list[i].set_filename(None)
                audio_list[i].set_filesize(None)
                has_changed = False
                while has_changed is False:
                    if audio_list[next_empty].get_status() is False:
                        has_changed = True
                    else:
                        next_empty += 1
        for audio in audio_list:
            print(audio.to_string(), file=sys.stdout)
        return "deleted"
    if request.method == "GET":
        return_array = {
            "audioFiles": [
            ]
        }
        for audio in audio_list:
            if audio.get_status() is True:
                return_array["audioFiles"].append({"name": audio.get_filename(),
                                                   "size": audio.get_filesize()})
        return json.dumps(return_array)


@app.route("/play", methods=["POST"])
def play():
    selected = request.values["Selected"]
    index = int(selected[len(selected) - 1]) - 1
    control_list[index].play_audio()
    return "play " + control_list[index].get_file().to_string()


@app.route("/applyCustom", methods=["POST"])
def applyCustom():
    selected = request.values["Selected"]
    index = int(selected[len(selected) - 1]) - 1
    v = request.values["Visual"]
    op1 = request.values["Option1"]
    op2 = request.values["Option2"]
    op3 = request.values["Option3"]
    control_list[index].set_visual(v)
    control_list[index].set_option1(op1)
    control_list[index].set_option2(op2)
    control_list[index].set_option3(op3)
    return "success"


@app.route("/vol_up", methods=["POST"])
def vol_up():
    volume.vol_up()
    return "success"


@app.route("/vol_down", methods=["POST"])
def vol_down():
    volume.vol_down()
    return "success"


@app.route("/close", methods=["POST"])
def close():
    for audio in audio_list:
        if audio.get_status() is True:
            audio.set_status(False)
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], audio.get_file().filename))
            print("Deleted File: " + audio.get_file().filename, file=sys.stdout)
            audio.set_file(None)
            audio.set_filename(None)
            audio.set_filesize(None)
    volume.set_vol(50)
    return "success"
