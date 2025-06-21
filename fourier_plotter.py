import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SignalPlotter:
    def __init__(self, root):
        self.root = root
        self.root.title("Fourier Plotter")
        self.root.resizable(False, False)
        
        # Application Icon
        try:
            self.root.iconbitmap('refik.ico')
        except:
            # In case of any error
            pass

        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Mode selection
        mode_frame = ttk.LabelFrame(main_frame, text="Plot Mode", padding="5")
        mode_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.mode_var = tk.StringVar(value="regular")
        ttk.Radiobutton(mode_frame, text="Sinusoidal Signals", variable=self.mode_var, 
                       value="regular", command=self.update_input_fields).grid(row=0, column=0, padx=5)
        ttk.Radiobutton(mode_frame, text="Fourier Series", variable=self.mode_var,
                       value="fourier", command=self.update_input_fields).grid(row=0, column=1, padx=5)

        # Input fields frame
        self.input_frame = ttk.LabelFrame(main_frame, text="Signal Parameters", padding="5")
        self.input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Input fields for regular mode
        self.regular_entries = {}
        params = ['A', 'f', 'θ']
        for i in range(3):
            ttk.Label(self.input_frame, text=f"Signal {i+1}:").grid(row=i, column=0, pady=2)
            for j, param in enumerate(params):
                ttk.Label(self.input_frame, text=param).grid(row=i, column=j*2+1, padx=5)
                self.regular_entries[f"{i}_{param}"] = ttk.Entry(self.input_frame, width=10)
                self.regular_entries[f"{i}_{param}"].grid(row=i, column=j*2+2, padx=5)
                self.regular_entries[f"{i}_{param}"].insert(0, "1.0")
        
        # Input fields for fourier series
        self.fourier_entries = {}
        
        # a0, w0, T input fields
        ttk.Label(self.input_frame, text="Core Parameters").grid(row=0, column=0, pady=2)
        for i, param in enumerate(['a0', 'w0', 'T']):
            ttk.Label(self.input_frame, text=param).grid(row=0, column=i*2+1, padx=5)
            self.fourier_entries[param] = ttk.Entry(self.input_frame, width=10)
            self.fourier_entries[param].grid(row=0, column=i*2+2, padx=5)
            # Set specific default values for each parameter
            if param == 'T':
                self.fourier_entries[param].insert(0, "6.283185")
            else:
                self.fourier_entries[param].insert(0, "1.0")
        
        # Bind w0 and T input fields
        self.fourier_entries['w0'].bind('<KeyRelease>', self.update_T_from_w0)
        self.fourier_entries['T'].bind('<KeyRelease>', self.update_w0_from_T)
        
        # Cosine coefficients (ak)
        ttk.Label(self.input_frame, text="Cosine Coefficients").grid(row=1, column=0, pady=2)
        for k in range(1, 10):
            ttk.Label(self.input_frame, text=f"a{k}").grid(row=1, column=k*2+1, padx=5)
            self.fourier_entries[f"ak_{k}"] = ttk.Entry(self.input_frame, width=10)
            self.fourier_entries[f"ak_{k}"].grid(row=1, column=k*2+2, padx=5)
            self.fourier_entries[f"ak_{k}"].insert(0, "0.0")
        
        # Sine coefficients (bk)
        ttk.Label(self.input_frame, text="Sine Coefficients").grid(row=2, column=0, pady=2)
        for k in range(1, 10):
            ttk.Label(self.input_frame, text=f"b{k}").grid(row=2, column=k*2+1, padx=5)
            self.fourier_entries[f"bk_{k}"] = ttk.Entry(self.input_frame, width=10)
            self.fourier_entries[f"bk_{k}"].grid(row=2, column=k*2+2, padx=5)
            self.fourier_entries[f"bk_{k}"].insert(0, "0.0")
        
        # Hide fourier input fields at start
        self.update_input_fields()
        
        # Plot button
        ttk.Button(main_frame, text="Plot Signals", command=self.plot_signals).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Scrollable frame
        self.scrollable_frame = ttk.Frame(main_frame)
        self.scrollable_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Canvas and scrollbar
        self.canvas = tk.Canvas(self.scrollable_frame, width=1000, height=800)
        self.scrollbar = ttk.Scrollbar(self.scrollable_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame2 = ttk.Frame(self.canvas)
        
        self.scrollable_frame2.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame2, anchor="nw", width=1000)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Place canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Graph area
        self.fig, self.axes = plt.subplots(3, 1, figsize=(15, 12))
        self.canvas_widget = FigureCanvasTkAgg(self.fig, master=self.scrollable_frame2)
        self.canvas_widget.get_tk_widget().pack(fill="both", expand=True)
        
    def update_input_fields(self):
        mode = self.mode_var.get()
        if mode == "regular":
            # Show regular mode input fields
            for widget in self.input_frame.winfo_children():
                widget.grid_remove()
            for i in range(3):
                ttk.Label(self.input_frame, text=f"Signal {i+1}:").grid(row=i, column=0, pady=2)
                for j, param in enumerate(['A', 'f', 'θ']):
                    ttk.Label(self.input_frame, text=param).grid(row=i, column=j*2+1, padx=5)
                    self.regular_entries[f"{i}_{param}"].grid(row=i, column=j*2+2, padx=5)
        else:
            # Show fourier mode input fields
            for widget in self.input_frame.winfo_children():
                widget.grid_remove()
            
            # a0, w0, T input fields
            ttk.Label(self.input_frame, text="Core Parameters").grid(row=0, column=0, pady=2)
            for i, param in enumerate(['a0', 'w0', 'T']):
                ttk.Label(self.input_frame, text=param).grid(row=0, column=i*2+1, padx=5)
                self.fourier_entries[param].grid(row=0, column=i*2+2, padx=5)
            
            # Cosine coefficients (ak)
            ttk.Label(self.input_frame, text="Cosine Coefficients").grid(row=1, column=0, pady=2)
            for k in range(1, 10):
                ttk.Label(self.input_frame, text=f"a{k}").grid(row=1, column=k*2+1, padx=5)
                self.fourier_entries[f"ak_{k}"].grid(row=1, column=k*2+2, padx=5)
            
            # Sine coefficients (bk)
            ttk.Label(self.input_frame, text="Sine Coefficients").grid(row=2, column=0, pady=2)
            for k in range(1, 10):
                ttk.Label(self.input_frame, text=f"b{k}").grid(row=2, column=k*2+1, padx=5)
                self.fourier_entries[f"bk_{k}"].grid(row=2, column=k*2+2, padx=5)

    def plot_signals(self):
        # Clear all graphs
        for ax in self.axes:
            ax.clear()
        
        if self.mode_var.get() == "regular":
            self.plot_regular_signals()
        else:
            self.plot_fourier_series()

    def plot_regular_signals(self):
        # Time vector
        t = np.linspace(0, 2*np.pi, 1000)
        
        # Plot each signal
        for i in range(3):
            # Get parameters
            A = float(self.regular_entries[f"{i}_A"].get())
            f = float(self.regular_entries[f"{i}_f"].get())
            theta = float(self.regular_entries[f"{i}_θ"].get())
            
            # Sinus and cosine signals
            sin_signal = A * np.sin(2*np.pi*f*t + theta)
            cos_signal = A * np.cos(2*np.pi*f*t + theta)
            
            # Plot
            self.axes[0].plot(t, sin_signal, label=f'Signal {i+1}')
            self.axes[1].plot(t, cos_signal, label=f'Signal {i+1}')
            
            # Calculate total signal
            if i == 0:
                total_signal = sin_signal + cos_signal
            else:
                total_signal += sin_signal + cos_signal
        
        # Plot total signal
        self.axes[2].plot(t, total_signal, 'r-', label='Aggregated Signal')
        
        # Graph titles and labels
        self.axes[0].set_title('Sine Signals')
        self.axes[1].set_title('Cosine Signals')
        self.axes[2].set_title('Aggregated Signal')
        
        for ax in self.axes:
            ax.grid(True)
            ax.legend()
            ax.set_xlabel('Time')
            ax.set_ylabel('Amplitude')
        
        # Adjust graph layout
        self.fig.tight_layout()
        self.canvas_widget.draw()

    def plot_fourier_series(self):
        # Get parameters
        a0 = float(self.fourier_entries['a0'].get())
        w0 = float(self.fourier_entries['w0'].get())
        T = float(self.fourier_entries['T'].get())
        
        # Create coefficient lists
        ak_list = [float(self.fourier_entries[f"ak_{k}"].get()) for k in range(1, 10)]
        bk_list = [float(self.fourier_entries[f"bk_{k}"].get()) for k in range(1, 10)]
        
        # Time vector
        t = np.linspace(0, T, 1000)
        
        # Fourier series calculation
        signal = a0/2  # DC bileşeni
        
        # For each harmonic
        for k in range(9):
            # Calculate harmonic components
            harmonic = ak_list[k] * np.cos((k+1)*w0*t) + bk_list[k] * np.sin((k+1)*w0*t)
            signal += harmonic
            
            # Plot each harmonic component
            self.axes[0].plot(t, ak_list[k] * np.cos((k+1)*w0*t), label=f'a{k+1}*cos({k+1}w0t)')
            self.axes[1].plot(t, bk_list[k] * np.sin((k+1)*w0*t), label=f'b{k+1}*sin({k+1}w0t)')
        
        # Plot total signal
        self.axes[2].plot(t, signal, 'r-', label='Aggregated Signal')
        
        # Graph titles and labels
        self.axes[0].set_title('Cosine Components')
        self.axes[1].set_title('Sine Components')
        self.axes[2].set_title('Aggregated Signal')
        
        for ax in self.axes:
            ax.grid(True)
            ax.legend()
            ax.set_xlabel('Time')
            ax.set_ylabel('Amplitude')
        
        # Adjust graph layout
        self.fig.tight_layout()
        self.canvas_widget.draw()

    def update_T_from_w0(self, event=None):
        try:
            w0 = float(self.fourier_entries['w0'].get())
            if w0 != 0:
                T = 2 * np.pi / w0
                self.fourier_entries['T'].delete(0, tk.END)
                self.fourier_entries['T'].insert(0, f"{T:.6f}")
        except ValueError:
            pass

    def update_w0_from_T(self, event=None):
        try:
            T = float(self.fourier_entries['T'].get())
            if T != 0:
                w0 = 2 * np.pi / T
                self.fourier_entries['w0'].delete(0, tk.END)
                self.fourier_entries['w0'].insert(0, f"{w0:.6f}")
        except ValueError:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = SignalPlotter(root)
    root.mainloop()
