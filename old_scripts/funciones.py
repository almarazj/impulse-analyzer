import numpy as np
import scipy as sc
import matplotlib.pyplot as plt
import scipy.signal as sgn
import soundfile as sd
from acoustics import bands

def import_ir(ir_path):
    """
    Imports an Impulse Response.

    Args:
        ir_path (str): Relative or absolute path to audio file.

    Returns:
        audio_len (int): returns ir length.
        stereo_ir (int): returns 1 when importing a stereo ir, 0 if mono ir.
        sample_rate (int): sample rate of audio file. 
        audio_data (numpy array): Array containing audio data.
        audio_data_L (numpy array): Array containing audio data of left channel.
        audio_data_R (numpy array): Array containing audio data of right channel.
    """
    try:
        audio_data, sample_rate = sd.read(ir_path)
    except Exception as e:
        raise ValueError("Could not import audio file: " + str(e))

    audio_data_L = 0
    audio_data_R = 0
    stereo = 0
    audio_len = 0
    audio_len = len(audio_data)/sample_rate
    if len(audio_data.shape) != 1:
        stereo = 1
        audio_data_L = audio_data[:,0] #Save estereo ir for IACCe calculations
        audio_data_R = audio_data[:,1] #Save estereo ir for IACCe calculations        
    
    return audio_len, stereo, sample_rate, audio_data, audio_data_L, audio_data_R

def cut_ir(data):
    """Function used to split an impulse response from its maximum to its ending,
    resulting in a signal that only contains the slope of the IR and eliminates
    Harmonic distortion components of an IR obtained from a sine sweep recording.
    INPUT:
        data: IR one-dimensional vector signal"""

    in_max = np.where(abs(data) == np.max(abs(data)))[0]  # Windows signal from its maximum onwards.
    in_max = int(in_max[0])
    data = data[(in_max)+5:]
    return data

def import_sweep(sweep_path): 
    """
    Imports a Sine Sweep.

    Args:
        sweep_path (str): Absolute path to audio file.

    Returns:
        sweep_len (int): returns sine sweep length.
        stereo_ss (int): returns 1 when importing a stereo ss, 0 if mono ss.
        sample_rate (int): sample rate of sine sweep audio file. 
        sweep_data (numpy array): Array containing audio data.
        sweep_L (numpy array): Array containing audio data of left channel.
        sweep_R (numpy array): Array containing audio data of right channel.
    """

    try:
        sweep_data, sample_rate= sd.read(sweep_path)
    except Exception as e:
        raise ValueError("Could not import sweep file: " + str(e)) 
    
    stereo_ss = 0
    sweep_len = 0
    sweep_len = len(sweep_data)/sample_rate
    sweep_L=0
    sweep_R=0
    
    if len(sweep_data.shape) != 1:
        stereo_ss = 1
        sweep_L = sweep_data[:,0] #Save estereo ir for IACCe calculations
        sweep_R = sweep_data[:,1] #Save estereo ir for IACCe calculations  


    return sweep_len, stereo_ss, sample_rate, sweep_data, sweep_L, sweep_R

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

def Lundeby(signal, fs):
    '''
    Lundeby method as especified in "On the effects of pre-processing of impulse responses in the evaluation of
    acoustic parameters on room acoustics" by Venturio and Farina in 2013.

    Lundeby method is based on an iterative algorithm that chooses the right temporal interval to which the linear
    regression is calculated. This will leave out unwanted contributions.

    1. Average squared IR in local time intervals (10-50 ms)
    2. Estimate background noise level using tail (last 10% of the signal)
    3. Estimate slope of decay from 0 dB to noise level (the “left” point is 0 dB. Search the “right” point 5-10
    dB above noise level)
    4. Find the crosspoint defined by regression line and noise level
    5. Find a new local time intervals based on the actual slope (use 3-10 intervals per 10 dB of decay)
    6. Average squared IR in new local time intervals
    7. Estimate background noise (starting from a time corresponding to a decay of 5-10 dB based on actual
    slope after the actual crosspoint but 10% of length of IR should be the minimum length)
    8. Estimate late decay slope (a dynamic range of 10-20 dB should be evaluated, starting 5-10 dB above
    the noise level)
    9. Find a new crosspoint
    10. Repeat 7, 8 and 9 until convergence of crosspoint is achieved
    '''
    signal = signal[np.argmax(signal):]/np.max(signal)  #Normalize and cut the IR from peak and beyond
    
    #1
    window = int(10*(10**-3)*fs)  #Window in samples chosen as 30 ms
    
    signal_average_dB = []
    
    for i in range(0, int(len(signal)/window)):
        window_average_rms = np.sqrt(np.mean(signal[window*i:window*(i+1)]**2))
        window_average_rms_dB = 10*np.log10(np.abs(window_average_rms)/np.max(signal))
        signal_average_dB.append(window_average_rms_dB)

    t = np.linspace(window/2, len(signal), len(signal_average_dB))  # signal average time samples
    t = t.astype(int)
    
    #2
    signal_last10 = signal[int(0.9*len(signal)):]
    background_noise = np.sqrt(np.mean(signal_last10**2))
    background_noise_dB = 10*np.log10(background_noise/max(signal))  # Noise level of last 10% of signal
    
    #3
    if len(np.argwhere(signal_average_dB > background_noise_dB + 10)) < 1:
        return fs*3     # if the method fails a 3 seconds max TR is supossed
    
    cross_signal_noise = np.argwhere(signal_average_dB > background_noise_dB + 10)[-1][0]  # Crosspoint between signal and 10 dB above noise level 
    
    poly = np.polyfit(t[0:cross_signal_noise], signal_average_dB[0:cross_signal_noise],1)  #Regression linear (1 degree)

    #4
    cross = (background_noise_dB - poly[1])/poly[0]  #Crosspoint between regression and noise in samples 
    cross = int(cross)

    for i in range(0, 7):  # Do 7 iterations (it should converge after 5, but noisy signals converge after 7 using this script)
        
        #5
        divisions = 10  # 3 to 10 divisions per 10 dB of regeression slope (use 7)
        window_new = int(divisions/poly[0]/-10)  # new window length in samples [amount of divisions in segment (7) / slope (-x dB) / per (-10 dB) decay]

        #6
        signal_average_dB = []    
        for i in range(0, int(len(signal[:int((cross-(poly[0]/-10)))])/window_new)):  #calculation with new window
            window_average_rms = np.sqrt(np.mean(signal[window_new*i:window_new*(i+1)]**2))
            window_average_rms_dB = 10*np.log10(np.abs(window_average_rms)/np.max(signal))
            signal_average_dB.append(window_average_rms_dB)        

        t = np.linspace(window_new/2, len(signal[:int((cross-(poly[0]/-10)))]), len(signal_average_dB))  # signal average time samples
        
        if len(t) < 1:
            return fs*3     # if the method fails a 3 seconds max TR is supossed
        t = t.astype(int)
        
        #7
        signal_5dB_after_cross = signal[int(cross+(5/-poly[0])):]  # signal after 5 dB decay from crosspoint
        
        if len(signal_5dB_after_cross) < (len(signal)/10):
            signal_5dB_after_cross = signal[int(len(signal)*0.9):]  # It has to have at least 10% of the length of the original signal
            
        background_noise = np.sqrt(np.mean(signal_5dB_after_cross**2))
        background_noise_dB = 10*np.log10(background_noise/max(signal)) 
        
        #8
        poly = np.polyfit(t, signal_average_dB, 1)

        #9
        cross = (background_noise_dB - poly[1])/poly[0]  #Crosspoint between regression and noise in samples 
    
    return int(cross)

def RT(signal, fs):
    '''  
    Calculates the Reverberation time of signal by T20, T30 and EDT methods.

    Args:
        sig (numpy array): array containing the audio signal.
        fs (int): sample rate of audio file. 

    Returns:
        parameter_results (numpy array): array containing each parameter result.
        parameters_names (numpy array): array containing each parameter name.
    '''

    parameters_names = ['Edt', 'T20', 'T30']
    parameters_boundaries = [[-1, -11],[-5,-25],[-5,-35]]
    parameter_results = np.zeros(3)
    
    for idx, bound in enumerate(parameters_boundaries):
        start = np.where(signal >= -1 )[0][-1]

        end = np.where(signal>= bound[1])[0][-1]
        
        rt_i = 1/fs*np.arange(start, end)
        poly = np.polyfit(rt_i, signal[start:end],1)
        parameter_results[idx] = -60 / poly[0]

    return parameter_results, parameters_names
       
def C(signal,fs, ci):
    
    signal = 10**(signal/10)
    t = int(np.round((ci / 1000.0) * fs))
    c_i = 10 * np.log10((np.sum(signal[:t]**2))/(np.sum(signal[t:-1]**2)))
    if ~np.isfinite(c_i):
        c_i = '---'
    return c_i

def IACC(signal_L, signal_R, fs,band ,stereo, stereo_ss):
    iacc_coefficients =[]
    
    if stereo==0 and band==1 and stereo_ss==0:
        iacc_coefficients = np.array(['----']*10)
    elif stereo==0 and band==3 and stereo_ss==0:
        iacc_coefficients = np.array(['----']*29)
    else:
        try:
            frequency, ir_filter_L = filter(signal_L,fs,band)
            frequency, ir_filter_R = filter(signal_R,fs,band)

            for ir_L, ir_R in zip(ir_filter_L,ir_filter_R):
                t80 = int(0.08*fs)
                ir_L = ir_L[np.argmax(ir_L):] #Cut form peak beyond
                ir_R = ir_R[np.argmax(ir_R):]
            
                ir_L = ir_L[:t80] #Cut first 80 ms
                ir_R = ir_R[:t80]
                iacc = np.correlate(ir_L, ir_R, 'full')
                iacc_normalized = iacc/(np.sqrt(np.sum(ir_L**2)*np.sum(ir_R**2)))
                iacc_coefficient = round(np.max(np.abs(iacc_normalized)),3)
                iacc_coefficients = np.append(iacc_coefficients, iacc_coefficient)
        except Exception as e:
            raise ValueError("This is not a stereo file, choose mono. " + str(e))
      
    return iacc_coefficients

def Transition_time_and_Edt(ir, fs, ir_smoothing):
    '''  
    Calculates the transition time and EDTt values.

    Args:
        ir (numpy array): array containing the audio signal.
        fs (int): sample rate of audio file. 
        ir_smooth (numpy array): array containing the smoothed audio signal.

    Returns:
        Tt_time (float): Transition time value.
        edtt (float): EDTt value.
    '''
    ir = ir[np.argmax(ir):] #Cut from max value

    energy_99 = np.sum(ir**2)*0.99
    cummulative_energy = np.cumsum(ir**2)
    
    Tt = np.where(cummulative_energy <= energy_99)[0][-1] #Tt value in samples
    
    Tt_time = Tt/fs  #Tt value in seconds
    
    ir_edtt = ir_smoothing[:Tt]

    if Tt_time < 0.001:
        edtt = '---'
    else:
        poly = np.polyfit(np.arange(0, Tt_time, 1/fs)[:len(ir_edtt)], ir_edtt, 1)
        edtt = -60/poly[0]
    
    if ~np.isfinite(edtt):
        edtt = '---'
    
    return Tt_time, edtt

def Calculate(ir, sample_rate, stereo, stereo2, band, smoothing, lundebyButton, window=50, ir_L=0, ir_R=0):     
    """
    Calculate room acoustics parameters from impulse responses.

    Args:
        impulse_response (numpy.ndarray): The impulse response of the room or space.
        sample_rate (int): The sample rate of the impulse response in Hz.
        stereo (bool): 1 if the impulse response is stereo, 0 if mono.
        band (str): The frequency band for analysis (e.g., '125Hz - 4kHz').
        smoothing_option (str): Smoothing option for parameter calculation ('mms' or 'schroeder').
        window_length_ms (float): Length of the analysis window in milliseconds.
        left_channel_impulse_response (numpy.ndarray): Impulse response of the left channel (if stereo).
        right_channel_impulse_response (numpy.ndarray): Impulse response of the right channel (if stereo).

    Returns:
            - 'T20' (float): Reverberation time (T20) in seconds.
            - 'T30' (float): Reverberation time (T30) in seconds.
            - 'C50' (float): Clarity (C50) in dB.
            - 'C80' (float): Clarity (C80) in dB.
            - 'Tt' (float): Total decay time (Tt) in seconds.
            - 'EDT' (float): Early decay time (EDT) in seconds.
            - 'EDTt' (float): Early decay time (EDTt) in seconds.
            - 'IACC' (float): Interaural cross-correlation coefficient (IACC).
    """

    freqs_center, ir_filter = filter(ir, sample_rate, band)

    # list_results = np.zeros((9,1+len(freqs_center))).astype(str) #CAMBIAR ESTE 9 POR LA CANT DE PARAMETROS
    # list_results[0,:] = np.append(['Frequency[Hz]'], freqs_center.astype(int).astype(str))
    
    cols = np.append(['Params.'], freqs_center.astype(int).astype(str))
    t20 = []
    t30 = []
    c50 = []
    c80 = []
    tt = []
    edt = []
    edtt = []
    iacc = []

    for i in range(ir_filter.shape[0]):
        frecs_ir = ir_filter[i,:]
        if smoothing == 'Moving Median Avg.':
            hilbert = Hilbert(frecs_ir)
            smoothing_frec = mmf(hilbert,int(window))
        
        #smoothing
        elif smoothing =='Schroeder':
            t_max_lundeby = Lundeby(frecs_ir, sample_rate)
            if lundebyButton == 1 and t_max_lundeby <= len(frecs_ir):
                t_max = t_max_lundeby
            else:
                t_max = -1
            hilbert = Hilbert(frecs_ir[0:t_max])
            smoothing_frec = Schroeder(hilbert)
            
        #Parameter calculatuion
        smoothing_frec_db = 20*np.log10(np.abs(smoothing_frec)/np.max(smoothing_frec))
        if freqs_center[i] == 1000:

            smoothing_1k = smoothing_frec_db
            ir_frec1k = 20*np.log10((np.abs(frecs_ir))/np.max(frecs_ir))

        rts_i, rts_names =RT(smoothing_frec_db, sample_rate)
        c50_i = C(smoothing_frec_db,sample_rate,50)
        c80_i= C(smoothing_frec_db,sample_rate,80)
        tt_i, edtt_i = Transition_time_and_Edt(ir, sample_rate, smoothing_frec_db )

        #Results Table
        t20 = np.append(t20, round(rts_i[1], 3))
        t30 = np.append(t30, round(rts_i[2], 3))
        c50 = np.append(c50, round(c50_i, 3))
        c80 = np.append(c80, round(c80_i, 3))
        tt = np.append(tt, round(tt_i, 3))
        edt = np.append(edt, round(rts_i[0], 3))
        edtt = np.append(edtt, round(edtt_i, 3))

    iacc = IACC(ir_L,ir_R,sample_rate,band,stereo, stereo2)

    t20 = list(np.append('T20', t20))
    t30 = list(np.append('T30', t30))
    c50 = list(np.append('C50', c50))
    c80 = list(np.append('C80', c80))
    tt = list(np.append('Tt', tt))
    edt = list(np.append('Edt', edt))
    edtt = list(np.append('EDTt', edtt))
    iacc = list(np.append('IACC', iacc))

    return cols, t20, t30, c50, c80, tt, edt, edtt, iacc, ir_frec1k, smoothing_1k
        