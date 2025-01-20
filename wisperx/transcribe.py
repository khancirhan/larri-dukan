
print('Before imports...')

from torch import float16, cuda
from torchaudio import load,functional
from transformers import pipeline
from flask import Flask, request, jsonify
import os, sys
import time
from werkzeug.utils import secure_filename
from pydub import AudioSegment
import subprocess

print('Starting point...')

app = Flask(__name__)


def get_binary_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.join(sys._MEIPASS, 'ffmpeg')  # Note: adding 'ffmpeg' subfolder
    else:
        base_path = '/opt/homebrew/bin'
    
    ffmpeg_path = os.path.join(base_path, 'ffmpeg')
    ffprobe_path = os.path.join(base_path, 'ffprobe')

     # Test if they work
    # subprocess.run(['ffmpeg/ffprobe', '-version'], check=True, capture_output=True)
    r1 = subprocess.run(['/Applications/desktop-app.app/Contents/Resources/transcribe/_internal/ffmpeg/ffprobe', '-version'], check=True, capture_output=True)
    r2 = subprocess.run([ffprobe_path, '-version'], check=True, capture_output=True)

    print("\nFFmpeg Version Output r1:")
    print(f"stdout: {r1.stdout}")
    print(f"stderr: {r1.stderr}")
    print(f"return code: {r1.returncode}")

    print("\nFFmpeg Version Output r2:")
    print(f"stdout: {r2.stdout}")
    print(f"stderr: {r2.stderr}")
    print(f"return code: {r2.returncode}")
    
    # Print absolute paths
    print(f"Absolute ffmpeg path: {os.path.abspath(ffmpeg_path)}")
    print(f"Absolute ffprobe path: {os.path.abspath(ffprobe_path)}")
    
    return ffmpeg_path, ffprobe_path

# Set the paths
ffmpeg_path, ffprobe_path = get_binary_path()

# Try setting them both as absolute paths
AudioSegment.converter = os.path.abspath(ffmpeg_path)
AudioSegment.ffmpeg = os.path.abspath(ffmpeg_path)
AudioSegment.ffprobe = os.path.abspath(ffprobe_path)

# Verify the settings took effect
print(f"AudioSegment converter: {AudioSegment.converter}")
print(f"AudioSegment ffmpeg: {AudioSegment.ffmpeg}")
print(f"AudioSegment ffprobe: {AudioSegment.ffprobe}")

def normalize_audio(audio_path):
    try:
        # Add error logging
        print(f"Processing audio file: {audio_path}")
        
        # Check if file exists and is readable
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        # Check upload folder permissions
        upload_folder = app.config["UPLOAD_FOLDER"]
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder, exist_ok=True)
            
        if not os.access(upload_folder, os.W_OK):
            raise PermissionError(f"Upload folder not writable: {upload_folder}")
            
        # Load audio with explicit error handling
        try:
            audio = AudioSegment.from_file(audio_path)
        except Exception as e:
            raise Exception(f"Failed to load audio: {str(e)}")
            
        # Convert to mono
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)  # Set sample rate to 16 kHz
        audio = audio.set_sample_width(2)  # Set to 16-bit (2 bytes)
        
        # Generate unique filename to avoid conflicts
        filename = f"converted_audio_{int(time.time())}.wav"
        new_filepath = os.path.join(upload_folder, filename)
        
        # Export with explicit error handling
        try:
            audio.export(new_filepath, format="wav")
        except Exception as e:
            raise Exception(f"Failed to export audio: {str(e)}")
            
        return new_filepath
        
    except Exception as e:
        # Log the error and re-raise
        print(f"Error in normalize_audio: {str(e)}")
        raise


def wisper_transcribe_audio(audio_path, model_path):
    # Load local model
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model_path,
        torch_dtype=float16,
        device="cuda" if cuda.is_available() else "cpu"
    )
    
    # Load and process audio
    audio, sr = load(audio_path)
    if sr != 16000:
        audio = functional.resample(audio, sr, 16000)
    
    # Transcribe
    result = pipe(audio.squeeze().numpy(), 
                 chunk_length_s=30,
                 batch_size=8,
                 return_timestamps=True)
    
    return result


# Configure this to your needs
UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = { "mp3", "wav", "ogg", "flac", "m4a", "aac" }

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            
            new_filepath = normalize_audio(filepath)

            result = wisper_transcribe_audio(new_filepath, "wisperx_model")
            os.remove(new_filepath)  # Clean up the uploaded file
            os.remove(filepath)  # Clean up the uploaded file
            return jsonify(result)
    except Exception as e:
        # os.remove(new_filepath)
        os.remove(filepath)  # Clean up the uploaded file
        return jsonify({"error": str(e)}), 500
    return jsonify({"error": "File type not allowed"}), 400


if __name__ == "__main__":
    print('App listening on port 5003')
    app.run(host="0.0.0.0", port=5003)