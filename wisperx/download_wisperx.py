import torch
import os
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

# Define paths for model storage
model_path = "wisperx_models"
os.makedirs(model_path, exist_ok=True)

# Load the model and processor
model_id = "openai/whisper-tiny"
processor = AutoProcessor.from_pretrained(model_id)
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto",
)

# Save models locally
processor.save_pretrained(model_path)
model.save_pretrained(model_path)
