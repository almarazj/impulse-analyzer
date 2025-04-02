import os
import numpy as np
from scipy.io import wavfile

def import_ir(file_path):
    """Import an impulse response from a .wav file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    fs, audio_data = wavfile.read(file_path)
    audio_len = len(audio_data) / fs
    stereo = 1 if len(audio_data.shape) > 1 else 0

    if stereo:
        audio_data_L = audio_data[:, 0]
        audio_data_R = audio_data[:, 1]
    else:
        audio_data_L = audio_data_R = None

    return audio_len, stereo, fs, audio_data, audio_data_L, audio_data_R

def cut_ir(audio_data, max_duration=10):
    """Cut the impulse response to a maximum duration."""
    if len(audio_data) > max_duration * 44100:  # Assuming 44.1 kHz sample rate
        return audio_data[:max_duration * 44100]
    return audio_data