import json
import wave
from vosk import Model, KaldiRecognizer

from pydub import AudioSegment

# Load the audio file (works with formats like MP3, FLAC, etc.)
audio = AudioSegment.from_file("war.ogg")  # Or any other format

# Convert to 16-bit, mono, 16 kHz WAV
audio = audio.set_channels(1)  # Convert to mono
audio = audio.set_frame_rate(16000)  # Set sample rate to 16 kHz
audio = audio.set_sample_width(2)  # Set to 16-bit (2 bytes)

# Export the audio as a WAV file
audio.export("converted_audio.wav", format="wav")

# Initialize Google Translate API

# Load the Vosk model for the language of your choice
# Download and extract the model from https://alphacephei.com/vosk/models
model_path = "model"
model = Model(model_path)

# Open your audio file (ensure it's WAV format with a 16kHz sample rate)
audio_file = "converted_audio.wav"
wf = wave.open(audio_file, "rb")

# Initialize the recognizer with the correct sample rate
recognizer = KaldiRecognizer(model, wf.getframerate())

# Process the audio file and transcribe
text = ""
while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if recognizer.AcceptWaveform(data):
        result = recognizer.Result()
        result_dict = json.loads(result)
        text += result_dict.get("text", "") + " "

# Print transcribed text
print("Transcribed Text: ", text)

# Translate the transcribed text

