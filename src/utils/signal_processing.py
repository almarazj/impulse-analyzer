import numpy as np
import scipy.signal as sgn
from acoustics import bands


def Schroeder(signal: np.ndarray) -> np.ndarray:
    '''Smooth the signal (signal) utilizing the Schroeder integral method'''
    return np.sum(signal) - np.cumsum(signal)
    

def mmf(signal: np.ndarray, window_size: int) -> np.ndarray:
    """Applies a moving mean filter with a specified window length to a 1D signal.
    The values when the window is half empty (beggining and end) are discarted."""
    return np.convolve(signal, np.ones(window_size)/window_size, mode='valid')


def Hilbert(signal: np.ndarray) -> np.ndarray:
    '''Smooth the signal (signal) utilizing the Hilbert Transform method'''
    return np.abs(sgn.hilbert(signal))


def bandpass_filter(signal: np.ndarray, sample_rate: int, octave_fraction: int) -> tuple[np.ndarray, np.ndarray]:
    """
    Apply octave or third-octave bandpass filtering to a signal.
    
    For third-octave filtering, the signal is reversed before processing to reduce 
    filter ringing interference (Rasmussen, 1991), then reversed again after filtering.
    
    Args:
        signal: Input audio signal as a numpy array
        sample_rate: Sampling rate of the audio signal in Hz
        octave_fraction: Bandwidth specification (1 for octave, 3 for third-octave)
        
    Returns:
        center_frequencies: Array of center frequencies for each band
        filtered_signals: 2D array where each row contains the signal filtered at the 
                         corresponding center frequency
    """
    # Determine center frequencies based on bandwidth specification
    if octave_fraction == 1:
        center_frequencies = bands.octave(31.5, 16000)
    elif octave_fraction == 3:
        signal = signal[::-1]  # Reverse for third-octave to reduce ringing
        center_frequencies = bands.third(25, 16000)
    else:
        raise ValueError("octave_fraction must be either 1 (octave) or 3 (third-octave)")
        
    # Calculate band edges
    bandwidth_factor = 2 ** (1 / (2 * octave_fraction))
    lower_frequencies = center_frequencies / bandwidth_factor
    upper_frequencies = center_frequencies * bandwidth_factor
    
    # Ensure highest band doesn't exceed Nyquist frequency
    nyquist = sample_rate / 2
    upper_frequencies[-1] = min(upper_frequencies[-1], nyquist - 1)
    
    # Initialize array for filtered signals
    filtered_signals = np.zeros((len(center_frequencies), len(signal)))
    
    # Apply bandpass filters for each frequency band
    for i, (f_low, f_high) in enumerate(zip(lower_frequencies, upper_frequencies)):
        sos = sgn.butter(
            order=8, 
            Wn=[f_low, f_high], 
            btype='bandpass', 
            analog=False, 
            fs=sample_rate, 
            output='sos'
        )
        filtered_signals[i, :] = sgn.sosfilt(sos, signal)
        
    # Reverse back for third-octave results
    if octave_fraction == 3:
        filtered_signals = np.flip(filtered_signals, axis=1)
    
    # Remove last 3% of samples to eliminate NaN artifacts
    truncate_index = int(filtered_signals.shape[1] * 0.97)
    filtered_signals = filtered_signals[:, :truncate_index]
    
    return center_frequencies, filtered_signals

