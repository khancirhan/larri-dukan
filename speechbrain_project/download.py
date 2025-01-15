import os
import torch
import torchaudio
from speechbrain.pretrained import EncoderDecoderASR
from speechbrain.utils.data_utils import download_file
import urllib.request
import json

class LocalModelDownloader:
    def __init__(self, model_name="asr-crdnn-rnnlm-librispeech"):
        self.model_name = model_name
        self.save_dir = f"pretrained_models/{model_name}"
        os.makedirs(self.save_dir, exist_ok=True)
        
    def download_model(self):
        """Download model files directly without HuggingFace"""
        base_url = "https://huggingface.co/speechbrain"
        model_files = [
            "hyperparams.yaml",
            "asr.ckpt",
            "tokenizer.ckpt",
            "lm.ckpt",
            "normalizer.ckpt"
        ]
        
        # Create and save model cards
        model_card = {
            "source": f"speechbrain/{self.model_name}",
            "savedir": self.save_dir
        }
        with open(f"{self.save_dir}/model_card.json", 'w') as f:
            json.dump(model_card, f)
            
        # Download each file
        for file in model_files:
            url = f"{base_url}/{self.model_name}/resolve/main/{file}"
            local_path = f"{self.save_dir}/{file}"
            
            if not os.path.exists(local_path):
                print(f"Downloading {file}...")
                try:
                    download_file(url, local_path)
                except Exception as e:
                    print(f"Error downloading {file}: {e}")
                    continue
            else:
                print(f"{file} already exists locally.")

def transcribe_audio(audio_file, model_name="asr-crdnn-rnnlm-librispeech"):
    """Transcribe audio using local model"""
    # Set up model path
    save_dir = f"pretrained_models/{model_name}"
    
    # Initialize ASR model
    asr_model = EncoderDecoderASR.from_hparams(
        source=save_dir,
        savedir=save_dir
    )
    
    # Load audio
    waveform, sample_rate = torchaudio.load(audio_file)
    
    # Resample if needed
    # if sample_rate != 16000:
    # resampler = torchaudio.transforms.Resample(sample_rate, 16000)
    # waveform = resampler(waveform)
    
    # Transcribe
    transcription = asr_model.transcribe_file(audio_file)
    return transcription

def main():
    # Example usage
    MODEL_NAME = "asr-crdnn-rnnlm-librispeech"  # You can change this to other models
    
    # Download model
    print("Downloading model files...")
    downloader = LocalModelDownloader(MODEL_NAME)
    downloader.download_model()
    
    # Create a test audio if needed
    if not os.path.exists("test_audio.wav"):
        print("\nGenerating test audio...")
        import numpy as np
        import soundfile as sf
        
        sample_rate = 16000
        duration = 3
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)
        sf.write('test_audio.wav', audio, sample_rate)
    
    # Test transcription
    print("\nTranscribing test audio...")
    result = transcribe_audio("test_audio_1.mp3", MODEL_NAME)
    print(f"Transcription: {result}")

if __name__ == "__main__":
    main()