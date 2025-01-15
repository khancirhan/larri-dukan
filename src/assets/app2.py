from flask import Flask, request, jsonify

print('Running....')

app = Flask(__name__)

@app.route("/transcribe", methods=["GET"])
def transcribe_audio():
    return jsonify({"message": "test"}), 200


if __name__ == "__main__":
    print('....')
    app.run(host="0.0.0.0", port=5004)