from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *
import tkinter as tk
from tkinter import messagebox
from tkinter.messagebox import showinfo
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
import matplotlib 
from scipy import signal
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from funciones import *
import os 
from tkinter import messagebox
import pandas as pd


def buttonClicked():
    global smoothing, fs, audio_data, audio_len, stereo, audio_data_L, audio_data_R, tree, results, band
    global irSweep, ir_L, ir_R, stereo2

    band = band_option.get()
    smoothing = smoothing_option.get()

    Ch = channel.get()
    Ch2 = channel2.get()

    if msEntry.get() == '':
        window = fs/1000
    else:
        window = int(msEntry.get())*fs/1000

    if band == 'Third Octave Bands':
        band = 3
    else:
        band = 1
    
    if tabControl.index("current") == 0:
        stereo2 = 0
        if stereo == 1:
            if Ch == 'R':
                signal = audio_data_R
            elif Ch == 'L':
                signal = audio_data_L
        else:
            signal = audio_data
            audio_data_R = 0
            audio_data_L = 0
    elif tabControl.index("current") == 1:
        if stereo2 == 1:
            audio_data_L = ir_L
            audio_data_R = ir_R
            if Ch2 == 'R':
                signal = ir_R
            elif Ch2 == 'L':
                signal = ir_R
        else:
            try:
                signal = irSweep
            except:
                messagebox.showerror('Error', 'Please generate or load an inverse sine sweep.')
            audio_data_L = 0
            audio_data_R = 0
    signal = cut_ir(signal)
    lundebyButton = 1
    cols, t20, t30, c50, c80, tt, edt, edtt, iacc, ir_frec1k, smoothing_1k = Calculate(
        signal, fs, stereo, stereo2, band, smoothing, lundebyButton, window, audio_data_L, audio_data_R
        )
    
    #TABLE POPULATION
    results = (cols, 
               t20, 
               t30, 
               c50, 
               c80, 
               tt, 
               edt, 
               edtt, 
               iacc)
    
    # Borrar todas las columnas actuales
    tree.delete(*tree.get_children())
   
    # Crear las nuevas columnas en función de la opción seleccionada
    if band == 1:
        tree["columns"] = ["Param.", '31.5 Hz', '63 Hz', '125 Hz', '250 Hz', '500 Hz', '1 kHz', '2 kHz', '4 kHz', '8 kHz', '16 kHz']
        for i in range(len(tree["columns"])):
            tree.column(tree["columns"][i], width=60, anchor=CENTER, stretch= False)     
            tree.heading(tree["columns"][i], text=tree["columns"][i])
            
    elif band == 3:
        tree["columns"] = ["Param.",'25 Hz', '31.5 Hz', '40 Hz', '50 Hz', '63 Hz', '80 Hz',
                            '100 Hz', '125 Hz', '160 Hz', '200 Hz', '250 Hz', '315 Hz',
                            '400 Hz', '500 Hz', '630 Hz', '800 Hz', '1 kHz', '1.25 kHz',
                            '1.6 kHz', '2 kHz', '2.5 kHz', '3.15 kHz', '4 kHz', '5 kHz',
                            '6.3 kHz', '8 kHz', '10 kHz', '12.5 kHz', '16 kHz']
        for i in range(len(tree["columns"])):
            tree.column(tree["columns"][i], width=60, stretch= False)     
            tree.heading(tree["columns"][i], text=tree["columns"][i])
    
    # add data to the treeview
    tree.insert(parent='', index='end', values=t20, tags='odd')
    tree.insert(parent='', index='end', values=t30, tags='even')
    tree.insert(parent='', index='end', values=c50, tags='odd')
    tree.insert(parent='', index='end', values=c80, tags='even')
    tree.insert(parent='', index='end', values=tt, tags='odd')
    tree.insert(parent='', index='end', values=edt, tags='even')
    tree.insert(parent='', index='end', values=edtt, tags='odd')
    tree.insert(parent='', index='end', values=iacc, tags='even')
    
    tree.bind('<<TreeviewSelect>>', item_selected)
    tree.pack(side='left', fill=BOTH, expand=True)
    # add a scrollbar
    scrollbary = Scrollbar(tabFrame, orient=VERTICAL)
    scrollbary.pack(side='right', fill='y')

    scrollbarx = Scrollbar(tabFrame, orient=HORIZONTAL)
    scrollbarx.pack(side='bottom', fill='x')

    scrollbarx.configure(command=tree.xview)
    scrollbary.configure(command=tree.yview)

      
    #fig, ax = plt.subplots(figsize = (7,5), facecolor='#f0f0f0')
    ax.clear()
    ax.plot(np.arange(0,len(ir_frec1k)/fs, 1/fs), ir_frec1k, label='RMS')
    ax.plot(np.arange(0,len(ir_frec1k)/fs, 1/fs)[:len(smoothing_1k)], smoothing_1k, label=smoothing)
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Energy [dB]')
    ax.set_ylim(-100, 5)
    ax.legend()
    fig.tight_layout()
    ax.grid()
    #fig.subplots_adjust(left=0.11, right=0.98, bottom=0.15, top=0.98, wspace=0, hspace=0)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    
    clearButton.configure(state=ACTIVE)
    copyButton.configure(state=ACTIVE)
    exportButton.configure(state=ACTIVE)

def open_file_IR():
    global fs, audio_data, audio_len, stereo, audio_data_L, audio_data_R, channel, Ch
    
    
    file = filedialog.askopenfilename()
    IRName.insert(tk.END, file)
    audio_len, stereo, fs, audio_data, audio_data_L, audio_data_R = import_ir(file)
    channel.set('L')
    Ch = channel.get()
    if stereo != 1:
        CHleft.configure(state= DISABLED)
        CHright.configure(state= DISABLED)
        audio_data = cut_ir(audio_data)
    else:
        CHleft.configure(state= ACTIVE)
        CHright.configure(state= ACTIVE)
        audio_data_L = cut_ir(audio_data_L)
        audio_data_R = cut_ir(audio_data_R)
        
    file_label.config(text= f'File Name: {os.path.basename(file)}')
    fs_label.config(text= f'Sample Rate: {fs} Hz')
    ch_label.config(text= f'Number of channels: {stereo + 1}')
    len_label.config(text= f'File Duration: {round(audio_len,2)} s')
    
    plot_ir()


    return audio_len, stereo, fs, audio_data, audio_data_L, audio_data_R

def open_file_SS():
    global fs, sweep_data, sweep_len, stereo2, sweep_L, sweep_R, file_sine_sweep
    
    file_sine_sweep = filedialog.askopenfilename()
    SSName.insert(tk.END, file_sine_sweep)
    
    sweep_len, stereo2, fs, sweep_data, sweep_L, sweep_R = import_sweep(file_sine_sweep)
    
    if stereo2 != 1:
        CHleft2.configure(state= DISABLED)
        CHright2.configure(state= DISABLED)
    else:
        CHleft2.configure(state= ACTIVE)
        CHright2.configure(state= ACTIVE)

    file_label2.config(text= f'File Name: {os.path.basename(file_sine_sweep)}')
    fs_label2.config(text= f'Sample Rate: {fs} Hz')
    ch_label2.config(text= f'Number of channels: {stereo2 + 1}')
    len_label2.config(text= f'File Duration: {round(sweep_len,2)} s')
    invFiltButton.configure(state=ACTIVE)
    return sweep_len, stereo2, fs, sweep_data, sweep_L, sweep_R

def plot_ir():
    global audio_len, stereo, fs, audio_data, audio_data_L, audio_data_R, Ch
    Ch = channel.get()
    if len(audio_data)/fs > 10:
        audio_data = audio_data[::10*fs]
        audio_data_L = audio_data_L[::10*fs]
        audio_data_R = audio_data_R[::10*fs]
    if stereo == 1:
        if Ch == 'L':
            ax.clear()
            ax.plot(np.arange(0,len(audio_data_L)/fs, 1/fs), audio_data_L, label='Left Channel')
            ax.set_xlabel('Time [s]')
            ax.set_ylabel('Amplitude')
            ax.legend()
            fig.tight_layout()
            ax.grid()
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        elif Ch == 'R':
            ax.clear()
            ax.plot(np.arange(0,len(audio_data_R)/fs, 1/fs), audio_data_R, label='Right Channel')
            ax.set_xlabel('Time [s]')
            ax.set_ylabel('Amplitude')
            ax.legend()
            fig.tight_layout()
            ax.grid()
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    else: 
        ax.clear()
        ax.plot(np.arange(0,len(audio_data)/fs, 1/fs), audio_data, label='Mono IR')
        ax.set_xlabel('Time [s]')
        ax.set_ylabel('Amplitude')
        ax.legend()
        fig.tight_layout()
        ax.grid()
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

def plot_ir_ss():
    global stereo2, fs, irSweep, ir_L, ir_R, Ch2
    Ch2 = channel2.get()
    if len(irSweep)/fs > 10:
        irSweep = irSweep[0:10*fs]
        if ir_L != 0:
            ir_L = ir_L[0:10*fs]
            ir_R = ir_R[0:10*fs]
    if stereo2 == 1:
        if Ch == 'L':
            ax.clear()
            ax.plot(np.arange(0,len(ir_L)/fs, 1/fs), ir_L, label='Left Channel')
            ax.set_xlabel('Time [s]')
            ax.set_ylabel('Amplitude')
            ax.legend()
            fig.tight_layout()
            ax.grid()
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        elif Ch == 'R':
            ax.clear()
            ax.plot(np.arange(0,len(ir_R)/fs, 1/fs), ir_R, label='Right Channel')
            ax.set_xlabel('Time [s]')
            ax.set_ylabel('Amplitude')
            ax.legend()
            fig.tight_layout()
            ax.grid()
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    else: 
        ax.clear()
        ax.plot(np.arange(0,len(irSweep)/fs, 1/fs), irSweep, label='Mono IR')
        ax.set_xlabel('Time [s]')
        ax.set_ylabel('Amplitude')
        ax.legend()
        fig.tight_layout()
        ax.grid()
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

def smooth_select(smoothing):
    if smoothing == 'Moving Median Avg.':
        lundebyCheckbutton.configure(state=DISABLED)
        lundebyCheckbutton.configure(state = DISABLED ,variable= lundebyButton.set(False))
        msEntry.configure(state=ACTIVE)
    else:
        msEntry.delete(0,'')
        msEntry.configure(state=DISABLED)
        lundebyCheckbutton.configure(state = DISABLED ,variable= lundebyButton.set(True))
        
def CopyToClipboard():
    try:
        copy_result = pd.DataFrame(results)
        copy_result.to_clipboard(index=False,header=False)
    except:
        messagebox.showerror('Error', 'There is no data generated yet.')  
        
def CopyToCSV():
    try:
        export_result = pd.DataFrame(results)
        file_export = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=(("CSV File", "*.csv"),("All Files", "*.*") ))
        export_result.to_csv(file_export)
    except:
        messagebox.showerror('Error', 'There is no data generated yet.')
       
def export_to_png():
    try:
        png_export = filedialog.asksaveasfilename(defaultextension=".png", filetypes=(("PNG File", "*.png"),("All Files", "*.*") ))
        plt.savefig(png_export)
    except:
        messagebox.showerror('Error', 'There is no data generated yet.')
    
def clearButtonClicked():
    global file_name, sample_rate, ch_number, audio_len, file
    file_name = '--'
    sample_rate = '--'
    ch_number = '--'
    audio_len = '--'
    file = '--'
    stereo = '--'
    IRName.delete(0,END)
    SSName.delete(0,END)
    file_label.config(text= f'File Name: {os.path.basename(file)}')
    fs_label.config(text= f'Sample Rate: {sample_rate}')
    ch_label.config(text= f'Number of channels: {stereo}')
    len_label.config(text= f'File Duration: {audio_len}')
    band_option.set('Select filter')
    smoothing_option.set('Select smoothing')
    CHleft.configure(state= DISABLED)
    CHright.configure(state= DISABLED)
    
    file_label2.config(text= f'File Name: {os.path.basename(file)}')
    fs_label2.config(text= f'Sample Rate: {sample_rate}')
    ch_label2.config(text= f'Number of channels: {stereo}')
    len_label2.config(text= f'File Duration: {audio_len}')

    CHleft2.configure(state= DISABLED)
    CHright2.configure(state= DISABLED)
    ax.clear()
    ax.grid()
    
    ax.set_ylim(-100,5)
    ax.set_ylabel('Energy [dB]')
    ax.set_xlabel('Time [s]')
    fig.tight_layout()
    canvas.draw()
    
    clearButton.configure(state=DISABLED)
    copyButton.configure(state=DISABLED)
    exportButton.configure(state=DISABLED)
    invFiltButton.configure(state=DISABLED)
    
    tree.delete(*tree.get_children())
    tree["columns"] = ["Param.", '31.5 Hz', '63 Hz', '125 Hz', '250 Hz', '500 Hz', '1 kHz', '2 kHz', '4 kHz', '8 kHz', '16 kHz']
    cols = ["Param.", '31.5 Hz', '63 Hz', '125 Hz', '250 Hz', '500 Hz', '1 kHz', '2 kHz', '4 kHz', '8 kHz', '16 kHz']
    t20 = ['T20', '--', '--', '--', '--', '--', '--', '--', '--', '--', '--',]
    t30 = ['T30', '--', '--', '--', '--', '--', '--', '--', '--', '--', '--',]
    c50 = ['C50', '--', '--', '--', '--', '--', '--', '--', '--', '--', '--',]
    c80 = ['C80', '--', '--', '--', '--', '--', '--', '--', '--', '--', '--',]
    tt = ['Tt', '--', '--', '--', '--', '--', '--', '--', '--', '--', '--',]
    edt = ['Edt', '--', '--', '--', '--', '--', '--', '--', '--', '--', '--',]
    edtt = ['EDTt', '--', '--', '--', '--', '--', '--', '--', '--', '--', '--',]
    iacc = ['IACC', '--', '--', '--', '--', '--', '--', '--', '--', '--', '--',]
    
    # add a scrollbar
    scrollbary = Scrollbar(tabFrame, orient=VERTICAL)
    scrollbary.pack(side='right', fill='y')

    scrollbarx = Scrollbar(tabFrame, orient=HORIZONTAL)
    scrollbarx.pack(side='bottom', fill='x')
    tree.configure(xscrollcommand=scrollbarx.set, yscrollcommand=scrollbary.set)
    scrollbary.configure(command=tree.yview)
    scrollbarx.configure(command=tree.xview)
    
    tree.column("#0", width=80, stretch=False)
    for i in range(len(cols)):
        tree.column(cols[i], width=60, anchor=CENTER)     
        tree.heading(cols[i], text=cols[i])
    tree.tag_configure('odd', background='#f8f8f8')
    tree.tag_configure('even', background='#ffffff')
    # add data to the treeview
    tree.insert(parent='', index='end', values=t20, tags='odd')
    tree.insert(parent='', index='end', values=t30, tags='even')
    tree.insert(parent='', index='end', values=c50, tags='odd')
    tree.insert(parent='', index='end', values=c80, tags='even')
    tree.insert(parent='', index='end', values=tt, tags='odd')
    tree.insert(parent='', index='end', values=edt, tags='even')
    tree.insert(parent='', index='end', values=edtt, tags='odd')
    tree.insert(parent='', index='end', values=iacc, tags='even')

def openSweep():
    global sweep_len, stereo2, fs, sweep_data, sweep_L, sweep_R, irSweep, ir_L, ir_R
    # GUI Main Window
    sweepWindow = tk.Toplevel(root)  
    sweepWindow.iconbitmap('res/app.ico')# This is the section of code which creates the main window
    sweepWindow.geometry('250x150')  # Window dimensions  # Background Color
    sweepWindow.title('Generate inverse filter')  # Window title
    sweepWindow.resizable(False, False)  # Non-resizable

    # FUNCTIONS
    def helpFunction():
        # Toplevel object which will
        # be treated as a new window
        helpWindow = Toplevel(root)
        helpWindow.iconbitmap('res/app.ico')
        # Sets the title of the Toplevel widget
        helpWindow.title("Help")
        helpWindow.geometry("300x200")
        helpWindow.resizable(False, False)
        # sets the geometry of toplevel
        # A Label widget to show in toplevel
        Label(helpWindow,
              text=open('sweepHelp.txt', 'r').read(), wraplength=250, justify="left").pack()
        
        def on_closing_help():
            helpWindow.quit()
            helpWindow.destroy()

        helpWindow.protocol("WM_DELETE_WINDOW", on_closing_help)
        
    def iss(sweep, f1, f2, d, fs):
        """Function generates an inverse filter given a linear or logarithmic sine sweep between the specified input frequencies
        and sweep duration. Convolution between the sweep and its inverse gives IR response.
        INPUTS:
            f1: initial frequency of sweep [Hz]
            f2: final frequency of sweep [Hz]
            d: sweep length [s]
            fs: sample rate [Hz]
            """

        t = np.arange(0, round(d), 1 / fs)
        w1 = 2 * np.pi * f1
        w2 = 2 * np.pi * f2

        K = (w1 / np.log(w2 / w1)) * d
        L = d / np.log(w2 / w1)
        y = np.sin(K * (np.exp(t / L) - 1))  # Log Sine Sweep

        w = (K / L) * np.exp(t / L)
        m = w1 / w

        u = m * np.flip(y)
        u = u / max(abs(u))  # Inverse Log Sine Sweep

        lenDiff = len(sweep) - len(u)

        u = np.pad(u, (0, lenDiff))
    
        ir = signal.fftconvolve(sweep, u)

        return ir
    
    def generateFunction():

        global sweep_data, sweep_L, sweep_R, sweep_len, fs, irSweep, ir_L, ir_R, stereo2, Ch2

        try:
            f1 = np.float64(sweepStart.get())
            f2 = np.float64(sweepEnd.get())
            d = np.float64(duration.get())
            if f1 <= 0 or f2 <= 0 or d <= 0 or f1 > f2:
                raise ValueError('Invalid or empty values')
        except:
            messagebox.showwarning('Error', 'Please specify valid start and end frequencies [Hz], and duration [s].')
            raise ValueError('Invalid or empty values')
        
        Ch2 = channel2.get()
        if stereo2 == 1:
            ir_L = iss(sweep_L,f1,f2,d,fs)
            ir_R = iss(sweep_R,f1,f2,d,fs)
            ir_L = cut_ir(ir_L)
            ir_R = cut_ir(ir_R)
            if Ch2 == 'R':
                irSweep = ir_R
            elif Ch2 == 'L':
                irSweep = ir_L
        else:
            iss_data = iss(sweep_data,f1,f2,d,fs)
            irSweep = signal.fftconvolve(sweep_data, iss_data)
            ir_R = 0
            ir_L = 0

        sweepWindow.quit()
        sweepWindow.destroy()
        irSweep = cut_ir(irSweep)

        plot_ir_ss()
    
        return irSweep, ir_L, ir_R, stereo2, fs

    def load_iss():
        global sweep_data, sweep_L, sweep_R, sweep_len, fs, irSweep, ir_L, ir_R, stereo2, Ch2

        iss_path = filedialog.askopenfilename()
        iss_len, stereo2, fs, iss_data, iss_L, iss_R = import_sweep(iss_path)

        Ch2 = channel2.get()
        if stereo2 == 1:
            ir_L = signal.fftconvolve(sweep_L, iss_L)
            ir_R = signal.fftconvolve(sweep_R, iss_R)
            ir_L = cut_ir(ir_L)
            ir_R = cut_ir(ir_R)
            if Ch2 == 'R':
                irSweep = ir_R
            elif Ch2 == 'L':
                irSweep = ir_L
        else:
            irSweep = signal.fftconvolve(sweep_data, iss_data)
            ir_R = 0
            ir_L = 0
        sweepWindow.quit()
        sweepWindow.destroy()
        irSweep = cut_ir(irSweep)

        plot_ir_ss()

        return irSweep, ir_R, ir_L, stereo2, fs

    # Buttons
    button_help = Button(sweepWindow, text='Help', command=helpFunction)
    button_help.place(relx=0.03, rely=0.8)
    button_load = Button(sweepWindow, text='Load ISS', command=load_iss)  # Closes window
    button_load.place(relx=0.35, rely=0.8)
    button_generate = Button(sweepWindow, text='Generate ISS', command=generateFunction)
    button_generate.place(relx=0.68, rely=0.8)


    # Entries
    sweepStart = Entry(sweepWindow)
    sweepStart.place(relx=0.45, rely=0.1, relwidth=0.3)
    sweepEnd = Entry(sweepWindow)
    sweepEnd.place(relx=0.45, rely=0.3, relwidth=0.3)
    duration = Entry(sweepWindow)
    duration.place(relx=0.45, rely=0.5, relwidth=0.3)

     # Labels
    start_label = Label(sweepWindow, text= 'Start frequency:')
    start_label.place(relx=0.05, rely=0.1)
    end_label = Label(sweepWindow, text= 'End frequency:')
    end_label.place(relx=0.05, rely=0.3)
    dur_label = Label(sweepWindow, text= 'Duration:')
    dur_label.place(relx=0.05, rely=0.5)

    hz1_label = Label(sweepWindow, text= 'Hz')
    hz1_label.place(relx=0.8, rely=0.1)
    hz2_label = Label(sweepWindow, text= 'Hz')
    hz2_label.place(relx=0.8, rely=0.3)
    s_label = Label(sweepWindow, text= 's')
    s_label.place(relx=0.8, rely=0.5)

    def on_closing_sweep():
        sweepWindow.quit()
        sweepWindow.destroy()

    sweepWindow.protocol("WM_DELETE_WINDOW", on_closing_sweep)
    sweepWindow.mainloop()  # Main Loop of the program

def show_about():
    about_window = tk.Toplevel(root)
    #about_window.configure(background='#222831')
    about_window.geometry("600x450")
    about_window.iconbitmap("res/app.ico")
    about_window.resizable(False, False)
    about_window.title("About ImpulseAnalyzr")

    # Content of the "About" window
    tk.Label(about_window, text="ImpulseAnalyzr", font=("Helvetica", 16,'bold')).pack(pady=10)
    tk.Label(about_window, text="Version: 1.0", font=("Helvetica", 12,'bold')).pack()
    tk.Label(about_window, text="Release Date: September 2023\n", font=("Helvetica", 10)).pack()

    # Developers
    tk.Label(about_window, text="Developers:", font=("Helvetica", 12,'bold')).pack()
    tk.Label(about_window, text="- Franco Areco                                     - Juan Almaraz\n", font=("Helvetica", 10)).pack()
    tk.Label(about_window, text="- Juan Rucci                                       - Calquin Epullan\n", font=("Helvetica", 10)).pack()

    # Description
    tk.Label(about_window, text="Description:", font=("Helvetica", 12,'bold')).pack()
    tk.Label(about_window, text="ImpulseAnalyzr is a specialized tool for analyzing impulse responses to obtain acoustic\n parameters of rooms.\n", font=("Helvetica", 10)).pack()
 
    # Acknowledgments
    tk.Label(about_window, text="Acknowledgments:", font=("Helvetica", 12,'bold')).pack()
    tk.Label(about_window, text="We would like to express our gratitude to all the users who participated in the ImpulseAnalyzr\n beta testing phase and to the developers of open-source libraries used in this project.\n", font=("Helvetica", 10)).pack()

    # Version History
    tk.Label(about_window, text="Version History:", font=("Helvetica", 12,'bold')).pack()
    tk.Label(about_window, text="- Version 1.0 (September 2023): Initial release of ImpulseAnalyzr, enabling precise measurement of\n impulse response and extraction of key acoustic parameters from any room.\n", font=("Helvetica", 10)).pack()

def item_selected(event):
    try:    
        for selected_item in tree.selection():
            # show a message
            fig1, ax1 = plt.subplots(figsize = (7.5,4), facecolor='#f0f0f0')
            
            selected_rows = tree.selection()

            if selected_rows:
                tree.selection_remove
                for row_id in selected_rows:
                    # Obtener los datos de la fila seleccionada
                    row_data = tree.item(selected_item)['values']
                    row_data1 = row_data[1::]

                    if row_data:
                        # Suponemos que los datos en la fila son números (puedes ajustar esto según tus necesidades)
                        data_row = [float(value) for value in row_data1]

                        # Crear un gráfico de barras con matplotlib
                        ax1.plot(range(len(data_row)), data_row)
                        ax1.set_xlabel('Frequency [Hz]')
                        ax1.set_ylabel(f'{row_data[0]}')
                        
                        if len(data_row) == 10:
                            ax1.set_xticks(range(len(data_row)),['31.5 Hz', '63 Hz', '125 Hz', '250 Hz', '500 Hz', '1 kHz', '2 kHz', '4 kHz', '8 kHz', '16 kHz'],fontsize=8)
                        else: 
                            ax1.set_xticks(range(len(data_row)),['25', '31.5', '40', '50', '63', '80', '100', '125', '160', '200', '250', '315', '400', '500', '630', '800', '1 kHz', '1.25 kHz', '1.6 kHz', '2 kHz', '2.5 kHz', '3.15 kHz', '4 kHz', '5 kHz', '6.3 kHz', '8 kHz', '10 kHz', '12.5 kHz', '16 kHz'], rotation =45,fontsize=8)
                        
                        fig1.show()
                        ax1.grid()
                        fig1.tight_layout()
                        canvas1 = FigureCanvasTkAgg(fig)
                        toolbar1 = NavigationToolbar2Tk(canvas1)
                        toolbar1.update()
                        canvas1.draw()
                        canvas1.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    except:
        messagebox.showerror('Error', 'There is no data generated yet.')  

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.quit()
        root.destroy()

# Root config
root = Tk()
root.geometry("1000x600")
root.minsize(1000,600)
root.maxsize(1920, 1080)
root.iconbitmap("res/app.ico")
root.title('ImpulseAnalyzr')
file_name = '--'
sample_rate = '--'
ch_number = '--'
audio_len = '--'
file = ''

#------------------------ Menu bar ------------------------------
menubar = Menu(root)
root.config(menu=menubar)

filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Load IR",command=open_file_IR)
filemenu.add_command(label="Load sine sweep",command=open_file_SS)
filemenu.add_separator()
filemenu.add_command(label="Export table as CSV", command=CopyToCSV)
filemenu.add_command(label="Export graph as PNG", command = export_to_png)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=on_closing)

editmenu = Menu(menubar, tearoff=0)
editmenu.add_command(label="Copy to clipboard", command= CopyToClipboard)
editmenu.add_separator()
editmenu.add_command(label="Clear", command= clearButtonClicked)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="About...",command=show_about)

menubar.add_cascade(label="File", menu=filemenu)
menubar.add_cascade(label="Edit", menu=editmenu)
menubar.add_cascade(label="Help", menu=helpmenu)

#------------------------ MAIN ------------------------------
s = Style()
s.configure('TMenubutton', background="#D4E6F1")
s.configure('TButton', color="#D4E6F1")
s.configure('LFrame.TFrame')
s.configure('RFrame.TFrame')

LFrame = Frame(root, width=300, height=600)
LFrame.pack(side='left')

RFrame = Frame(root, width=700, height=600)
RFrame.pack(side='right', expand=True, fill=BOTH)

plotFrame = Frame(RFrame, height=300, width=700)
plotFrame.pack(side='top',expand=True, fill= BOTH, padx=10)

tabFrame = Frame(RFrame, height=300, width=700)
tabFrame.pack(side='bottom',expand=True, fill= BOTH, padx=10, pady=10)

logoFrame = Frame(LFrame, width=280, height=110)
logoFrame.pack(side='top', fill='x', padx=10)

loadFrame = Frame(LFrame, width=280, height=170)
loadFrame.pack(side='top', fill='x', padx=10, pady=10)

optFrame = LabelFrame(LFrame, text='Options', width=280, height=130)
optFrame.pack(side='top', fill='x', padx=10)

calcFrame = LabelFrame(LFrame, text='Actions', width=280, height=130)
calcFrame.pack(side='top', fill='x', padx=10, pady=10)

#------------------------ Contents ------------------------------
# Panel 1: Logo
logoCanvas=Canvas(logoFrame, width=280, height=90)
logoCanvas.pack()

img = Image.open("res/u3f.png")
resized_img=img.resize((280,90), Image.LANCZOS)
logo = ImageTk.PhotoImage(resized_img)
u3fLogo = Label(logoFrame, image=logo)
u3fLogo.place(relheight=1, relwidth=1, relx=0,rely=0)

# Panel 2: import
tabControl = Notebook(loadFrame)
tabIR = Frame(tabControl) 
tabSS = Frame(tabControl)

tabControl.add(tabIR, text = 'Import Impulse Response')
tabControl.add(tabSS, text= 'Import Sine Sweep')
tabControl.place(relheight=1,relwidth=1)

IRName = Entry(tabIR)
IRName.place(relx=0.05, rely=0.1, relwidth=0.6, relheight=0.15)

browseIRButton = Button(tabIR, text="Browse ...", command=open_file_IR)
browseIRButton.place(relx=0.7, rely=0.1, relwidth=0.25, relheight=0.16)

channel = StringVar()
CHleft = Radiobutton(tabIR, text = 'Left Channel', variable=channel, value = 'L', command=plot_ir)
CHleft.place(relx=0.03, rely=0.3)
CHright = Radiobutton(tabIR, text = 'Right Channel', variable=channel, value = 'R', command=plot_ir)
CHright.place(relx=0.43, rely=0.3)

file_label = Label(tabIR, text= f'File Name: {file_name}')
file_label.place(relx=0.03, rely=0.5)

fs_label = Label(tabIR, text= f'Sample Rate: {sample_rate}')
fs_label.place(relx=0.03, rely=0.65)

len_label = Label(tabIR, text= f'File Duration: {audio_len}')
len_label.place(relx=0.53, rely=0.65)

ch_label = Label(tabIR, text= f'Number of Channels: {ch_number}')
ch_label.place(relx=0.03, rely=0.8)

SSName = Entry(tabSS)
SSName.place(relx=0.05, rely=0.1, relwidth=0.6, relheight=0.15)

browseSSButton = Button(tabSS, text="Browse ...",command=open_file_SS)
browseSSButton.place(relx=0.7, rely=0.1, relwidth=0.25, relheight=0.16)

invFiltButton = Button(tabSS, text = 'Inverse filter ...', command = openSweep)
invFiltButton.place(relx=0.53, rely=0.8, relwidth=0.45, relheight=0.16)
invFiltButton.configure(state=DISABLED)

channel2 = StringVar()
CHleft2 = Radiobutton(tabSS, text = 'Left Channel', variable=channel2, value = 'L')
CHleft2.place(relx=0.03, rely=0.3)
CHright2 = Radiobutton(tabSS, text = 'Right Channel', variable=channel2, value = 'R')
CHright2.place(relx=0.43, rely=0.3)

file_label2 = Label(tabSS, text= f'File Name: {file_name}')
file_label2.place(relx=0.03, rely=0.5)

fs_label2 = Label(tabSS, text= f'Sample Rate: {sample_rate}')
fs_label2.place(relx=0.03, rely=0.65)

len_label2 = Label(tabSS, text= f'File Duration: {audio_len}')
len_label2.place(relx=0.53, rely=0.65)

ch_label2 = Label(tabSS, text= f'Number of Channels: {ch_number}')
ch_label2.place(relx=0.03, rely=0.8)

# Panel 3: options
filterLabel = Label(optFrame, text = 'Filter:')
filterLabel.place(relx=0.1, rely=0.1)

smoothLabel = Label(optFrame, text = 'Smoothing:')
smoothLabel.place(relx=0.1, rely=0.4)

band_option = StringVar(optFrame)
band_option.set('Select filter')
filter_options = {"Octave Bands": 1, "Third Octave Bands": 3}
filterOption = OptionMenu(optFrame, band_option,'Select filter', *filter_options.keys())
filterOption.config(width=20)
filterOption.place(relx=0.4, rely=0.1)

smoothing_option = StringVar(optFrame)
smoothing_option.set('Select smoothing')
smooth_options = {"Moving Median Avg.": 1, "Schroeder": 2}
smoothOption = OptionMenu(optFrame, smoothing_option,'Select smoothing', *smooth_options.keys(), command=smooth_select)
smoothOption.config(width=20)
smoothOption.place(relx=0.4, rely=0.4)

lundebyButton = tk.BooleanVar(value=False)
lundebyCheckbutton = Checkbutton(optFrame, text = 'Lundeby' ,variable=lundebyButton)
lundebyCheckbutton.place(relx=0.1, rely=0.7)
lundebyCheckbutton.configure(state=DISABLED)

msEntry = Entry(optFrame)
msEntry.place(relx=0.4, rely=0.7, relwidth=0.2)
msEntry.configure(state=DISABLED)

msLabel = Label(optFrame, text = 'w. length [ms]')
msLabel.place(relx=0.65, rely=0.7)

# Panel 4: Actions
audio_data = []
stereo = 0
calcButton = Button(calcFrame, text = 'Calculate!', command=buttonClicked)
calcButton.place(relx=0.1, rely=0.1, relwidth=0.55, relheight=0.4)

clearButton = Button(calcFrame, text = 'Clear', command = clearButtonClicked)
clearButton.place(relx=0.7, rely=0.1, relwidth=0.2, relheight=0.4)

exportButton = Button(calcFrame, text = 'Export as CSV', command = CopyToCSV)
exportButton.place(relx=0.1, rely=0.6, relwidth=0.35, relheight=0.3)

copyButton = Button(calcFrame, text = 'Copy to Clipboard', command= CopyToClipboard)
copyButton.place(relx=0.5, rely=0.6, relwidth=0.4, relheight=0.3)

#------------------------ PLOT AREA ------------------------------

fig, ax = plt.subplots(figsize = (7.5,3.3), facecolor='#f0f0f0')
ax.set_xlabel('Time [s]')
ax.set_ylabel('Energy [dB]')
fig.tight_layout()
ax.grid()
canvas = FigureCanvasTkAgg(fig,plotFrame)
toolbar = NavigationToolbar2Tk(canvas, plotFrame)
toolbar.update()
canvas.draw()
canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

#------------------------ TABLE AREA ------------------------------

cols = ["Param.", '31.5 Hz', '63 Hz', '125 Hz', '250 Hz', '500 Hz', '1 kHz', '2 kHz', '4 kHz', '8 kHz', '16 kHz']
t20 = ['T20', '--', '--', '--', '--', '--', '--', '--', '--', '--', '--',]
t30 = ['T30', '--', '--', '--', '--', '--', '--', '--', '--', '--', '--',]
c50 = ['C50', '--', '--', '--', '--', '--', '--', '--', '--', '--', '--',]
c80 = ['C80', '--', '--', '--', '--', '--', '--', '--', '--', '--', '--',]
tt = ['Tt', '--', '--', '--', '--', '--', '--', '--', '--', '--', '--',]
edt = ['Edt', '--', '--', '--', '--', '--', '--', '--', '--', '--', '--',]
edtt = ['EDTt', '--', '--', '--', '--', '--', '--', '--', '--', '--', '--',]
iacc = ['IACC', '--', '--', '--', '--', '--', '--', '--', '--', '--', '--',]

# add a scrollbar
scrollbary = Scrollbar(tabFrame, orient=VERTICAL)
scrollbary.pack(side='right', fill='y')

scrollbarx = Scrollbar(tabFrame, orient=HORIZONTAL)
scrollbarx.pack(side='bottom', fill='x')

tree = Treeview(tabFrame, columns=cols, show='headings',yscrollcommand=scrollbary, xscrollcommand=scrollbarx)
tree.configure(xscrollcommand=scrollbarx.set, yscrollcommand=scrollbary.set)

scrollbarx.configure(command=tree.xview)
scrollbary.configure(command=tree.yview)

tree.column("#0", width=80, stretch=False)
for i in range(len(cols)):
    tree.column(cols[i], width=60, anchor=CENTER)     
    tree.heading(cols[i], text=cols[i])
tree.tag_configure('odd', background='#f8f8f8')
tree.tag_configure('even', background='#ffffff')
# add data to the treeview
tree.insert(parent='', index='end', values=t20, tags='odd')
tree.insert(parent='', index='end', values=t30, tags='even')
tree.insert(parent='', index='end', values=c50, tags='odd')
tree.insert(parent='', index='end', values=c80, tags='even')
tree.insert(parent='', index='end', values=tt, tags='odd')
tree.insert(parent='', index='end', values=edt, tags='even')
tree.insert(parent='', index='end', values=edtt, tags='odd')
tree.insert(parent='', index='end', values=iacc, tags='even')

tree.bind('<<TreeviewSelect>>', item_selected)
tree.pack(side='left', fill=BOTH, expand=True)

# App
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()