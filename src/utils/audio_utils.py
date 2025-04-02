import os
from dataclasses import dataclass
from typing import Optional
import numpy as np
from scipy.io import wavfile

@dataclass
class AudioData:
    sample_rate: int
    duration: float
    is_stereo: bool
    raw_data: np.ndarray
    left_channel: Optional[np.ndarray] = None
    right_channel: Optional[np.ndarray] = None

def import_ir(file_path: str) -> AudioData:

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    sample_rate, audio_data = wavfile.read(file_path)
    duration = len(audio_data) / sample_rate
    is_stereo = len(audio_data.shape) > 1 and audio_data.shape[1] >= 2
    
    left_channel = None
    right_channel = None
    
    if is_stereo:
        left_channel = audio_data[:, 0]
        right_channel = audio_data[:, 1]
    
    return AudioData(
        sample_rate=sample_rate,
        duration=duration,
        is_stereo=is_stereo,
        raw_data=audio_data,
        left_channel=left_channel,
        right_channel=right_channel
    )

def cut_ir(audio_data, max_duration=10):
    """Cut the impulse response to a maximum duration."""
    if len(audio_data.duration) > max_duration:
        audio_data.raw_data = audio_data.raw_data[:max_duration * audio_data.sample_rate]
        return audio_data
    return audio_data