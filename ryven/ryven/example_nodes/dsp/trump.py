import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import remez, freqz

# Parameters
Fs = 96000  # Sampling Frequency
N = 5       # Filter Order

# Define your bands, desired response (approximation), and weights
bands = [0, 32000]  # Frequency bands
desired = [6]        # Desired slope of the frequency response
weights = [2]        # Weight for the band

# Design the filter using the remez function
b = remez(N+1, bands, desired, weight=weights, fs=Fs, type='differentiator')
print(b)
# Compute the frequency response
w, h = freqz(b, worN=1024, fs=Fs)

# Plot the magnitude response
plt.figure()
plt.plot(w, np.abs(h))
plt.title('Magnitude Response')
plt.xlabel('Frequency [Hz]')
plt.ylabel('Magnitude [dB]')
plt.grid()
plt.show()
