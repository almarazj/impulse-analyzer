import numpy as np
import scipy.signal as sgn
from acoustics import bands


def Schroeder(signal):
    '''Smooth the signal (signal) utilizing the Schroeder integral method'''
    return np.sum(signal) - np.cumsum(signal)
    

def mmf(signal, window_size):
    """Applies a moving mean filter with a specified window length to a 1D signal.
    The values when the window is half empty (beggining and end) are discarted."""
    return np.convolve(signal, np.ones(window_size)/window_size, mode='valid')


def Hilbert(signal):
    '''Smooth the signal (signal) utilizing the Hilbert Transform method'''
    return np.abs(sgn.hilbert(signal))


def filter(signal, fs, band):
    global frequency
    '''  
    Takes the signal, the sample_rate and the octave fraction and returns 2 arrays, the first with 
    the center frequency of each band, and another with each row being the signal filtered for their respective frequency.
    If the filter is a third octave one, the signal is reversed to reduce the interferience produce by the ringing of the filter
    as proposed by Rasmussen in 1991. Then the filtered results are reversed again.

    Args:
        signal (numpy array): array containing the audiosignal.
        fs (int): sample rate of audio file. 
        octave (bool): 1 if its filtered by octave, 3 if it's filtered by third octave.

    Returns:
        freq_center (numpy array): array contining every band central frequency.
        filtered (numpy array): each row being the signal filtered for their respective frequency.
    '''
    
    if band == 1:
        frequency = bands.octave(31.5,16000)
    elif band == 3:
        signal = signal[::-1]
        frequency = bands.third(25,16000)
        
    frequency_low = frequency*2**(-1/2/band)  #lower freq for each band
    frequency_high = frequency*2**(1/2/band)  #higher freq for each band
    
    if frequency_high[-1] > fs/2: frequency_high[-1] = fs/2 - 1
    
    signal_filter = np.zeros((len(frequency),len(signal)))
    
    for i in range(0, len(frequency)):
        sos = sgn.butter(8, (frequency_low[i], frequency_high[i]), 'bandpass', analog=False, fs=fs, output='sos')  #SOS for each band
        signal_filter[i,:] = sgn.sosfilt(sos, signal)  #Filtering
        
    if band == 3: 
        signal_filter = np.flip(signal_filter,1)  #(De-)reverse  the results
    
    signal_filter = signal_filter[:,:int(signal_filter.shape[1]*0.97)]  #Eliminate NaN values at the last 3% of signal
    
    return frequency, signal_filter