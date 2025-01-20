# First install required packages:
# pip install vosk
# pip install sounddevice
# pip install numpy

import vosk
import sounddevice as sd
import numpy as np
import json
import queue

# Initialize audio input queue
q = queue.Queue()

def callback(indata, frames, time, status):
    """This is called for each audio block"""
    if status:
        print(status)
    q.put(bytes(indata))

def process_audio():
    # Download model from https://alphacephei.com/vosk/models
    # and unpack it into 'model' folder
    model = vosk.Model("model")
    
    device_info = sd.query_devices(None, 'input')
    samplerate = int(device_info['default_samplerate'])
    
    # Create recognizer instance
    rec = vosk.KaldiRecognizer(model, samplerate)
    
    # Start audio stream
    with sd.RawInputStream(samplerate=samplerate, 
                         blocksize=8000,
                         dtype='int16',
                         channels=1,
                         callback=callback):
        print("Listening... Press Ctrl+C to stop")
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                print(result['text'])

if __name__ == '__main__':
    try:
        process_audio()
    except KeyboardInterrupt:
        print("\nDone")