import tkinter as tk
from tkinter import ttk, filedialog, Menu
import numpy as np
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

data = None
signal_type = None
n = None

def browse_file():
    global data, signal_type, n
    file_path = filedialog.askopenfilename()
    try:
        if file_path.endswith('.txt'):
            temp_data = np.loadtxt(file_path, max_rows=3)
            signal_type = int(temp_data[0])
            is_periodic = int(temp_data[1])
            n = int(temp_data[2])
            data = np.loadtxt(file_path, skiprows=3)
            browse_label.config(text="File successfully read with NumPy!", fg='green')
        else:
            browse_label.config(text="Selected file is not a .txt file.", fg='red')
    except Exception as e:
        browse_label.config(text=f"Error reading the file: {e}", fg='red')

def generate_waves():
    global fig, ax1, ax2,n
    if data is not None:
        t = data[:, 0]
        y = data[:, 1]
        ax1.plot(t, y, label=f'{signal_type}(t)', color='blue')
        ax1.set_xlabel('Time (seconds)')
        ax1.set_ylabel('Amplitude')
        ax1.legend(loc='upper right')
        ax1.grid(True)
        ax2.stem(t, y, linefmt='b-', markerfmt='bo', basefmt='k-')
        ax2.set_title("Digital Signal")
        ax2.set_xlabel("Samples")
        ax2.set_ylabel("Amplitude")
        ax2.grid(True)
        if n > 50 :
            ax1.set_xlim([0, 15])
            ax2.set_xlim([0, 15])
    else:
        error = False
        freq_error.config(text="")
        amp_error.config(text="")
        sample_freq_error.config(text="")
        phase_error.config(text="")
        try:
            freq = float(freq_entry.get())
        except ValueError:
            freq_error.config(text="Frequency must be a number")
            error = True
        try:
            sampling_freq = float(sample_freq_entry.get())
        except ValueError:
            sample_freq_error.config(text="Sampling frequency must be a number")
            error = True
        try:
            phase = float(phase_entry.get())
        except ValueError:
            phase_error.config(text="Phase must be a number")
            error = True
        try:
            amp = float(amp_entry.get())
        except ValueError:
            amp_error.config(text="Amplitude must be a number")
            error = True
        if error:
            return
        if sampling_freq < 2 * freq:
            sample_freq_error.config(text="Sampling frequency must obey the sampling theorem")
            return
        t = np.arange(0, 1, 1 / sampling_freq)
        n = np.arange(0, len(t))
        if combo_box.get() == "sin":
            y_analog = amp * np.sin(2 * np.pi * freq * t + phase)
            y_digital = amp * np.sin(2 * np.pi * (freq / sampling_freq) * n + phase)
            SignalSamplesAreEqual("SinOutput.txt", n, y_digital)
        else:
            y_analog = amp * np.cos(2 * np.pi * freq * t + phase)
            y_digital = amp * np.cos(2 * np.pi * (freq / sampling_freq) * n + phase)
            SignalSamplesAreEqual("CosOutput.txt", n, y_digital)
        save_wave_data(t, y_analog, n, y_digital)
        ax1.plot(t, y_analog, label="Analog Signal", color='b')
        ax1.set_title("Analog Signal")
        ax1.set_xlabel("Time (seconds)")
        ax1.set_ylabel("Amplitude")
        ax1.grid(True)
        ax2.stem(n, y_digital, linefmt='b-', markerfmt='bo', basefmt='k-')
        ax2.set_title("Digital Signal")
        ax2.set_xlabel("Samples")
        ax2.set_ylabel("Amplitude")
        ax2.grid(True)
        ax1.set_ylim([-1.5 * amp, 1.5 * amp])
        ax2.set_ylim([-1.5 * amp, 1.5 * amp])
        ax1.set_xlim([0, 0.01])
        ax2.set_xlim([0, 15])
    canvas.draw()

def generate_sine_wave():
    combo_box.set("sin")
    generate_waves()

def generate_cosine_wave():
    combo_box.set("cos")
    generate_waves()

def save_wave_data(t, continuous_wave, t_discrete, discrete_wave):
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text files", ".txt"), ("All files", ".*")],
                                             title="Save Wave Data")
    if file_path:
        try:
            with open(file_path, 'w') as file:
                #file.write("Continuous Wave Data:\n")
                # file.write("Time (s), Amplitude\n")
                # for time, amplitude in zip(t, continuous_wave):
                #     file.write(f"{time:.5f}, {amplitude:.10f}\n")
                # file.write("\nDiscrete Wave Data:\n")
                file.write(f"0\n")
                file.write(f"0\n")
                file.write(f"{len(t_discrete)}\n")

                for time, amplitude in zip(t_discrete, discrete_wave):
                    file.write(f"{time} {amplitude:.8f}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save wave data: {e}")


def SignalSamplesAreEqual(file_name, indices, samples):
    expected_indices = []
    expected_samples = []
    with open(file_name, 'r') as f:
        line = f.readline()
        line = f.readline()
        line = f.readline()
        line = f.readline()
        while line:
            # process line
            L = line.strip()
            if len(L.split(' ')) == 2:
                L = line.split(' ')
                V1 = int(L[0])
                V2 = float(L[1])
                expected_indices.append(V1)
                expected_samples.append(V2)
                line = f.readline()
            else:
                break

    if len(expected_samples) != len(samples):
        print("Test case failed, your signal have different length from the expected one")
        return
    for i in range(len(expected_samples)):
        if abs(samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Test case failed, your signal have different values from the expected one")
            return
    print("Test case passed successfully")


def clear_waves():
    global data, signal_type, n
    ax1.clear()
    ax2.clear()
    ax1.set_title("")
    ax2.set_title("")
    canvas.draw()
    freq_entry.delete(0, tk.END)
    sample_freq_entry.delete(0, tk.END)
    amp_entry.delete(0, tk.END)
    phase_entry.delete(0, tk.END)
    combo_box.set("sin")
    data = None
    signal_type = None
    n = None
    freq_error.config(text="")
    amp_error.config(text="")
    sample_freq_error.config(text="")
    phase_error.config(text="")
    browse_label.config(text="")

root = tk.Tk()
root.title("Signal Generator")
control_frame = tk.Frame(root)
control_frame.pack(side=tk.TOP, pady=10)
menu_bar = Menu(root)
root.config(menu=menu_bar)
signal_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Signal Generation", menu=signal_menu)
signal_menu.add_command(label="Sine Wave", command=generate_sine_wave)
signal_menu.add_command(label="Cosine Wave", command=generate_cosine_wave)
browse_button = tk.Button(control_frame, text='Get signals file', width=25, command=browse_file)
browse_button.grid(row=0, column=0, pady=5)
browse_label = tk.Label(control_frame, text="")
browse_label.grid(row=0, column=1, pady=5)
freq_label = tk.Label(control_frame, text="Analog Frequency (Hz)")
freq_label.grid(row=1, column=0)
freq_entry = tk.Entry(control_frame)
freq_entry.grid(row=1, column=1)
freq_error = tk.Label(control_frame, fg="red")
freq_error.grid(row=1, column=2)
sample_freq_label = tk.Label(control_frame, text="Sampling Frequency (Hz)")
sample_freq_label.grid(row=2, column=0)
sample_freq_entry = tk.Entry(control_frame)
sample_freq_entry.grid(row=2, column=1)
sample_freq_error = tk.Label(control_frame, fg="red")
sample_freq_error.grid(row=2, column=2)
amp_label = tk.Label(control_frame, text="Amplitude")
amp_label.grid(row=3, column=0)
amp_entry = tk.Entry(control_frame)
amp_entry.grid(row=3, column=1)
amp_error = tk.Label(control_frame, fg="red")
amp_error.grid(row=3, column=2)
phase_label = tk.Label(control_frame, text="Phase (radians)")
phase_label.grid(row=4, column=0)
phase_entry = tk.Entry(control_frame)
phase_entry.grid(row=4, column=1)
phase_error = tk.Label(control_frame, fg="red")
phase_error.grid(row=4, column=2)
combo_box_label = tk.Label(control_frame, text="Select Signal Type (sin / cos)")
combo_box_label.grid(row=5, column=0)
combo_box = ttk.Combobox(control_frame, values=["Sine", "Cosine"])
combo_box.grid(row=5, column=1)
combo_box.set("sin")
generate_button = tk.Button(control_frame, text='Generate', bg='green', width=25, command=generate_waves)
generate_button.grid(row=6, column=0, pady=10)
clear_button = tk.Button(control_frame, text='Clear', bg='red', width=25, command=clear_waves)
clear_button.grid(row=6, column=1, pady=10)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack()
root.mainloop()
