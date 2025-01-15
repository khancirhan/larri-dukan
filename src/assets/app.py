from flask import Flask, request, jsonify
import whisperx
import torch
import os
from werkzeug.utils import secure_filename

print('Running....')

app = Flask(__name__)


# Configure this to your needs
UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {"wav", "mp3", "m4a"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisperx.load_model("base", device, compute_type="float32")


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
            result = model.transcribe(filepath)
            os.remove(filepath)  # Clean up the uploaded file
            return jsonify(result)
        except Exception as e:
            os.remove(filepath)  # Clean up the uploaded file
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "File type not allowed"}), 400



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5003)
