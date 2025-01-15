
import torch
import torchaudio
from transformers import pipeline
from flask import Flask, request, jsonify
import sys, os
from werkzeug.utils import secure_filename

print('Running....')

app = Flask(__name__)

cwd = os.getcwd()
arr = os.listdir()

print(cwd)
print(arr)

bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
# path_to_yml = os.path.abspath(os.path.join(bundle_dir, 'config.yml'))

print(bundle_dir)


def wisper_transcribe_audio(audio_path, model_path):
    # Load local model
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model_path,
        torch_dtype=torch.float16,
        device="cuda" if torch.cuda.is_available() else "cpu"
    )
    
    # Load and process audio
    audio, sr = torchaudio.load(audio_path)
    if sr != 16000:
        audio = torchaudio.functional.resample(audio, sr, 16000)
    
    # Transcribe
    result = pipe(audio.squeeze().numpy(), 
                 chunk_length_s=30,
                 batch_size=8,
                 return_timestamps=True)
    
    return result




# Configure this to your needs
UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {"wav", "mp3", "m4a"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        try:
            result = wisper_transcribe_audio(filepath, os.path.join(bundle_dir, "wisperx_models") )
            os.remove(filepath)  # Clean up the uploaded file
            return jsonify(result)
        except Exception as e:
            os.remove(filepath)  # Clean up the uploaded file
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "File type not allowed"}), 400



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)