import numpy as np

def plot_ir(figure, fs, audio_data, audio_data_L=None, audio_data_R=None):
    """
    Plot the impulse response (IR) on the given Matplotlib figure.

    Args:
        figure: Matplotlib figure object to plot on.
        fs: Sampling rate of the audio data.
        audio_data: Mono audio data.
        audio_data_L: Left channel audio data (for stereo).
        audio_data_R: Right channel audio data (for stereo).
    """
    figure.clear()
    ax = figure.add_subplot(111)

    if audio_data_L is not None and audio_data_R is not None:  # Stereo
        time = np.arange(0, len(audio_data_L)) / fs
        ax.plot(time, audio_data_L, label="Left Channel")
        ax.plot(time, audio_data_R, label="Right Channel")
    else:  # Mono
        time = np.arange(0, len(audio_data)) / fs
        ax.plot(time, audio_data, label="Mono IR")

    ax.set_title("Impulse Response")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Amplitude")
    ax.legend()
    ax.grid()

    figure.canvas.draw()