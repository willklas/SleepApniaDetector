from flask import Flask, Response, request, jsonify
from scipy.io import wavfile
from scipy import signal
import numpy as np
# import matplotlib.pyplot as plt
import time


app = Flask(__name__)

users = ['1','2','3','4','5']
months = {1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'}
sample_freq   = 1000
apnia_seconds = 10

class time_class:
    def __init__(self):
        temp = time.localtime()
        self.year   = temp[0]
        self.month  = temp[1]
        self.day    = temp[2]
        self.hour   = temp[3] 
        self.minute = temp[4] 

    def update_time(self, delta_seconds):
        delta_minutes = delta_seconds / 60
        if delta_minutes < 1:
            return
        else:
            self.minute += int(delta_minutes)
            if self.minute > 60:
                self.hour += 1
                self.minute -= 60
                if self.hour > 24:
                    self.hour -= 24
                    self.day += 1
    
    def to_string(self):
        return str(self.year) + ', ' + months[self.month] + ' ' + str(self.day) + ' ' + str(self.hour) + ':' + str(self.minute)


def get_apnia_info(audio_path):
    try:
        # audio_path = 'sample_'+ user_id + '.wav'
        # get the sample frequence and sound array
        sampFreq, snd_arr = wavfile.read(audio_path)

        # cut out one of the audio channels 
        new_snd_arr = snd_arr[:,0] 
        
        # down sample the sound array 
        secs = int(len(new_snd_arr)/sampFreq)
        samps = secs*sample_freq
        new_snd_arr = signal.resample(new_snd_arr, samps)

        # scale the data between -1 and +1
        new_snd_arr  = new_snd_arr / np.max(np.abs(new_snd_arr))

        # convert any negative values to positive
        new_snd_arr = np.absolute(new_snd_arr)

        # determine threshold for audio level that determines any time inbetween breaths
        threshold = np.mean(new_snd_arr) * 4

        apnia_tracker = []

        apnia_state    = 0
        sample_counter = 0
        # time_stop      = 0
        time_obj = time_class()
        # find periods of encounterd apnia
        for i in range(len(new_snd_arr)):
        # for sample in new_snd_arr:
            if not apnia_state:
                if new_snd_arr[i] < threshold:
                    apnia_state = 1
                    # time_stop = 
            elif apnia_state:
                if new_snd_arr[i] < threshold:
                    sample_counter += 1
                else:
                    apnia_state = 0
                    if (sample_counter / sample_freq) >= apnia_seconds:
                        delta_seconds = sample_counter / sample_freq
                        time_obj.update_time(delta_seconds)
                        apnia_tracker.append((time_obj.to_string(), delta_seconds))
                    sample_counter = 0
        print('tracker....', apnia_tracker)
        return len(apnia_tracker)
    except:
        return 0


@app.route('/get_data')
def get_data():
    file_name = request.args.get('file_name')
    num_apnia_tracker = get_apnia_info(file_name)
    return jsonify(num_apnia_tracker)


@app.route('/put_data')
def put_data():
    return "api in developement..."


if __name__ == '__main__':
    app.run(debug=True)