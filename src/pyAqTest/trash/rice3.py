import numpy as np
import matplotlib.pyplot as plt


def detect_change_points(signal, window_size=20, threshold=2.0):
    """
    Detect major change points using a sliding window comparison.

    Parameters:
    - signal: 1D numpy array of time series data
    - window_size: number of points before/after to compare
    - threshold: minimum absolute mean difference to flag a change

    Returns:
    - change_points: list of indices where change is detected
    """
    change_points = []
    max_change = 0
    max_i = 0
    signed_max_diff = 0

    for i in range(window_size, len(signal) - window_size):
        window_before = signal[i - window_size : i]
        window_after = signal[i : i + window_size]

        mean_before = np.mean(window_before)
        mean_after = np.mean(window_after)

        diff = abs(mean_after - mean_before)
        if diff > max_change:
            max_change = diff
            max_i = i
            signed_max_diff = mean_after - mean_before

    # within the window around max_i, choose the maximum (or the minimum) chane
    # depending on the sign of the change
    if signed_max_diff > 0:
        j = np.argmax(signal[max_i : max_i + window_size])
    else:
        j = np.argmin(signal[max_i : max_i + window_size])

    recovery_start = max_i + j

    return recovery_start


# Example usage
if __name__ == "__main__":
    np.random.seed(42)
    # Create synthetic data: flat, then jump, then flat
    signal = np.concatenate(
        [
            np.random.normal(0, 0.5, 100),
            np.random.normal(5, 0.5, 100),
            np.random.normal(0, 0.5, 100),
        ]
    )

    cp = detect_change_points(signal, window_size=10, threshold=1.5)

    # Plot
    plt.figure(figsize=(12, 4))
    plt.plot(signal, label="Signal")

    plt.axvline(
        cp, color="red", linestyle="--", label="Change Point"
    )  # if cp == change_points[0] else ""
    plt.legend()
    plt.title("Sliding Window Change Point Detection")
    plt.show()
