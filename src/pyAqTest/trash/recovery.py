import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter


def detect_recovery(
    time,
    hydraulic_head,
    window_size=10,
    slope_threshold=0.001,
    smoothing_window=101,
    polyorder=3,
):
    """
    Detect the start of recovery in a time series of hydraulic heads.

    Parameters:
        time (array): time values
        hydraulic_head (array): measured hydraulic head values
        window_size (int): number of consecutive points to confirm recovery
        slope_threshold (float): minimum slope to count as recovery
        smoothing_window (int): window length for smoothing (must be odd)
        polyorder (int): polynomial order for smoothing

    Returns:
        recovery_start_idx (int or None): index where recovery starts
        recovery_start_time (float or None): time where recovery starts
        smooth_head (array): smoothed hydraulic head series
    """
    smooth_head = savgol_filter(
        hydraulic_head, window_length=smoothing_window, polyorder=polyorder
    )
    derivative = np.gradient(smooth_head, time)

    recovery_start_idx = None
    for i in range(len(derivative) - window_size):
        window = derivative[i : i + window_size]
        if np.all(window > slope_threshold):
            recovery_start_idx = i
            break

    recovery_start_time = (
        time[recovery_start_idx] if recovery_start_idx is not None else None
    )
    return recovery_start_idx, recovery_start_time, smooth_head


# Example usage
time = np.linspace(0, 100, 1000)
hydraulic_head = 10 - 0.05 * time
hydraulic_head[700:] += 0.1 * (time[700:] - time[700])
np.random.seed(42)
hydraulic_head += np.random.normal(0, 0.05, size=hydraulic_head.shape)

idx, rec_time, smooth_head = detect_recovery(time, hydraulic_head)

if idx is not None:
    print(f"Recovery starts at index {idx}, time {rec_time:.2f}")
else:
    print("No recovery point detected.")

# Plot the result
plt.figure(figsize=(12, 6))
plt.plot(time, hydraulic_head, label="Noisy Data", alpha=0.5)
plt.plot(time, smooth_head, label="Smoothed Data", linewidth=2)
if idx is not None:
    plt.axvline(x=rec_time, color="r", linestyle="--", label="Recovery Start")
plt.xlabel("Time")
plt.ylabel("Hydraulic Head")
plt.title("Detection of Recovery Start (Robust)")
plt.legend()
plt.show()
