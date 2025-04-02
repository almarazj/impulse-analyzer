import numpy as np
from src.utils.audio_utils import AudioData
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QVBoxLayout


def plot_ir(figure, audio_data: AudioData, channel = None) -> None:
    """
    Plot the impulse response (IR) on the given Matplotlib figure.

    Args:
        figure: Matplotlib figure object to plot on.
        audio_data: AudioData class instance containing the IR data.
    """
    figure.clear()
    ax = figure.add_subplot(111)
    time = np.arange(0, len(audio_data.raw_data)) / audio_data.sample_rate
    
    if channel:
        if channel == "L":
            ax.plot(time, audio_data.left_channel, label="Left Channel")
        elif channel == "R":
            ax.plot(time, audio_data.right_channel, label="Right Channel")
    else:
        if audio_data.is_stereo:
            ax.plot(time, audio_data.left_channel, label="Left Channel")
            ax.plot(time, audio_data.right_channel, label="Right Channel")
        else:
            ax.plot(time, audio_data, label="Mono IR")
    

    ax.set_title("Impulse Response")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Amplitude")
    ax.legend()
    ax.grid()

    figure.canvas.draw()

def placeholder_plot(plot_frame):
    """
    Set up a placeholder plot in the given plot frame.

    Args:
        plot_frame: The QFrame where the plot will be embedded.
    """
    # Create the Matplotlib figure and canvas
    figure = Figure()
    canvas = FigureCanvas(figure)

    # Add the canvas to the plot frame
    layout = QVBoxLayout(plot_frame)
    layout.addWidget(canvas)

    # Create the placeholder plot
    ax = figure.add_subplot(111)
    ax.plot([0, 1, 2, 3], [0, 1, 0, 1], label="Placeholder Line")
    ax.set_title("Placeholder Plot")
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.legend()

    # Apply tight layout and draw the canvas
    figure.tight_layout()
    canvas.draw()

    return figure, canvas