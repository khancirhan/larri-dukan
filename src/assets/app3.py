import os
import subprocess
import sys
from pathlib import Path
import urllib.request
import tarfile

def setup_speechbrain():
    """Set up SpeechBrain environment and dependencies"""
    # Create a new virtual environment
    print("Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "speechvenv", "speechbrain_env"])
    
    # Determine the pip path
    if sys.platform == "darwin":  # Mac OS
        pip_path = "./speechbrain_env/bin/pip"
        python_path = "./speechbrain_env/bin/python"
    else:
        pip_path = "./speechbrain_env/Scripts/pip"
        python_path = "./speechbrain_env/Scripts/python"
    
    # Install required packages
    print("Installing required packages...")
    packages = [
        "torch",
        "torchaudio",
        "speechbrain",
        "numpy",
        "scipy",
        "tqdm",
        "hydra-core",
        "soundfile",
        "sentencepiece"
    ]
    
    for package in packages:
        subprocess.run([pip_path, "install", package])
    
    return python_path



def main():
    # Setup directory
    work_dir = Path("speechbrain_project")
    work_dir.mkdir(exist_ok=True)
    os.chdir(work_dir)
    
    # Setup environment
    python_path = setup_speechbrain()

    print(python_path)
    
    # Create example and test scripts
    print("\nSetup complete! Follow these steps to use SpeechBrain:")
    print("1. Activate the virtual environment:")
    print("   source speechbrain_env/bin/activate  # On Mac/Linux")
    print("   .\\speechbrain_env\\Scripts\\activate  # On Windows")
    print("\n2. Create a test audio file:")
    print("   python create_test_audio.py")
    print("\n3. Run speech recognition:")
    print("   python speech_recognition.py test_audio.wav")

if __name__ == "__main__":
    main()