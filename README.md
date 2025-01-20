pyinstaller --onefile transcribe.py --add-data="wisperx_model:wisperx_model"
pyinstaller --onedir transcribe.py --add-data="wisperx_model:wisperx_model"

pyinstaller --onedir \
  --add-binary='/opt/homebrew/bin/ffmpeg:ffmpeg' \
  --add-binary='/opt/homebrew/bin/ffprobe:ffmpeg' \
  transcribe.py