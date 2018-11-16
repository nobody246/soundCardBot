#(c) 2018 github.com/nobody246 nothing that happens from this software is my liability, enjoy

#! /usr/bin/env python
import pyaudio
import wave
import numpy as np
from aubio import pitch
from os import system
from time import sleep
import time
import subprocess
import random

#TODO make args
soundFilePath = '/location/of/your/characters/mp3/files/'
pitchMin = 80
pitchMax = 230
exitWhenFilesDone = False
debugFrames = False
phraseBufferMin = 3
phraseBufferMax = 45
sleepBeforeSoundMin = 1.8
sleepBeforeSoundMax = 2.8
startConversationWhenSilent = True
silenceMin = 5
silenceMax = 20
multipleAfterSilentMin = 2
multipleAfterSilentMax = 3.5

CHUNK = 1024
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100

inSound = False
lastSoundTime = 0
lastSoundFileLen = 0
soundFiles = []
usedFiles = []

def soundFileLength(filename):
    try:
        result = subprocess.Popen(['mplayer', '-vo', 'null', '-ao', 'null',
                                   '-frames', '0', '-identify',
                                   filename],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        duration = [x for x in result.stdout.readlines() if "ID_LENGTH" in x]
        return duration[0].split('=')[1].strip('\n')
    except:
        pass
        return 0

def getSoundFiles(path):
    result = subprocess.Popen(['ls', path],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)
    return result.stdout.readlines()


def playSound():
    global lastSoundTime,lastSoundFileLen,inSound,soundFiles, usedFiles, soundFilePath;
    global sleepBeforeSoundMin, sleepBeforeSoundMax
    currFile = None
    if len(usedFiles) == 0:
        currFile = soundFiles[int(random.uniform(0, len(soundFiles)))].strip('\n');
    elif len(usedFiles) < len(soundFiles):
        currFile = soundFiles[int(random.uniform(0, len(soundFiles)))].strip('\n');
        while (currFile in usedFiles):
            currFile = soundFiles[int(random.uniform(0, len(soundFiles)))].strip('\n');
    elif exitWhenFilesDone:
        print "done."
        exit(0)
    else:
        print "restarting."
        usedFiles = []
        soundFiles = getSoundFiles(soundFilePath)
    if not currFile:
        return
    f=str("{}{}".format(soundFilePath, currFile))
    usedFiles.append(currFile)
    lastSoundTime = time.time()
    lastSoundFileLen = float(soundFileLength(f))
    inSound = True
    sleep(random.uniform(sleepBeforeSoundMin, sleepBeforeSoundMax))
    system("mplayer {}".format(f))

getSoundFiles(soundFilePath)
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                input_device_index=4)


# Pitch
tolerance = 0.8
downsample = 1
win_s = 4096 // downsample # fft size
hop_s = 1024  // downsample # hop size
pitch_o = pitch("yin", win_s, hop_s, RATE)
pitch_o.set_unit("midi")
pitch_o.set_tolerance(tolerance)

silenceSince = 0
soundFiles = getSoundFiles(soundFilePath)
while True:
    random.seed()
    buffer = stream.read(CHUNK, False)
    signal = np.fromstring(buffer, dtype=np.float32)
    pitch =  pitch_o(signal)[0]
    confidence = pitch_o.get_confidence()
    if not inSound:
        timeDiff = (time.time() - lastSoundTime)
        if (pitch > pitchMin and pitch < pitchMax)\
           or (startConversationWhenSilent and timeDiff > lastSoundFileLen + random.uniform(silenceMin, silenceMax))\
           and (time.time() - lastSoundTime) >= random.uniform(phraseBufferMin, phraseBufferMax):
            print "playing sound"
            playSound()
        else:
            print "silence detected.."
        if debugFrames: print "{} / {}".format(pitch,confidence)
    if (time.time() - lastSoundTime) >= lastSoundFileLen * random.uniform(multipleAfterSilentMin, multipleAfterSilentMax):
        inSound = False
        lastSoundFileTime = 0;
        lastSoundFileLen = 0


stream.stop_stream()
stream.close()
p.terminate()
