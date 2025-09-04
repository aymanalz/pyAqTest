import numpy as np
import pandas as pd
from scipy.stats import linregress
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("Qt5Agg")  # or 'Qt5Agg', depending on your system


class Bouwer_Rice_1976(object):
    def __init__(self):
        pass

    def fit(x, y):

        result = linregress(x, y)
        return result

    def isolate_recovery(self, time, head, window_size=10):
        """
        Slug data can be for a case were water table is lowered or raised, so
        we need first to isolate the part related to recovery

        :param window_size:
        :param time:
        :param head:
        :return:
        """

        max_change = 0
        max_i = 0
        signed_max_diff = 0

        for i in range(window_size, len(head) - window_size):
            window_before = head[i - window_size : i]
            window_after = head[i : i + window_size]

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
            j = np.argmax(head[max_i - window_size : max_i + window_size])
        else:
            j = np.argmin(head[max_i - window_size : max_i + window_size])

        static_level = np.mean(head[j - window_size : j - 1])
        recovery_start = max_i + j
        recovery_depth = head[recovery_start:] - static_level
        recovery_time = time[recovery_start:]
        return recovery_depth, recovery_time

    def analyze(self, time, head, rc, rw, anis, d, b, D, H0=None):
        """

        :param time:
        :param head:
        :param rc: raduis of the casing
        :param rw: raduis of the well hole
        :param anis: anisotropy ratio kz/kr
        :param d: distance between water-table level and the top of the screen.
        :param b: length of the screen, or length of the screen below water table.
        :param D: saturated thickness of the aquifer
        :param H0: theoretical increase (or decrease) in water level after adding the slug.
        :return:
        """

        rec_head, rec_time = isolate_recovery(time, head, window_size=10)
        if H0 is None:
            H0 = rec_head[0]

        fit_result = fit(x=rec_time, y=np.log(rec_head / H0))

        # plot
        x = rec_time
        y = np.log(rec_head / H0)
        y_fit = fit_result.slope * x + fit_result.intercept
        plt.scatter(x, y, label="Data")
        plt.plot(x, y_fit, color="red", label="Fitted Line")
        plt.legend()
        plt.title("Linear Fit using SciPy")
        plt.show()
        #

        rw_star = rw * (anis**0.5)
        x = np.log10(b / rw_star)

        xs = np.array([1, x, x**2.0, x**3.0, x**4.0])
        betaA = np.array([1.353, 2.157, -4.0270, 2.777, -0.460])
        betaB = np.array([-0.401, 2.619, -3.2670, 1.548, -0.210])
        betaC = np.array([-1.605, 9.496, -12.317, 6.528, -0.986])
        A = np.dot(xs, betaA)
        B = np.dot(xs, betaB)
        C = np.dot(xs, betaC)

        part1 = 1.1 / (np.log((d + b) / rw_star))
        term6 = np.log((D - (d + b)) / rw_star)
        if term6 > 6.0:
            term6 = 6.0
        part2 = (A + B * term6) / (b / rw_star)
        lnRw_rw = np.power((part1 + part2), -1.0)
        T0 = -1.0 / fit_result.slope
        k = (rc**2.0) * lnRw_rw / (2 * b * T0)

        return k


if __name__ == "__main__":
    fn = r"C:\workspace\projects\pump_tests\pyAqTest\tests\datasets\Butler_1.txt"
    df = pd.read_csv(fn, delim_whitespace=True)
    del df["NormalizedHead"]

    # make the data realistic by adding pre-test static level
    t = np.arange(0, 10, 0.1)
    h = len(t) * [0.0]
    df_static = pd.DataFrame(columns=df.columns)
    df_static["Time(s)"] = t
    df_static["Head(m)"] = h
    df["Time(s)"] = df["Time(s)"] + t[-1]
    df = pd.concat([df_static, df])
    # noise = 0.06 * np.random.randn(len(df))
    rng = np.random.default_rng(seed=42)
    noise = rng.normal(loc=0.0, scale=0.0, size=len(df))
    df["Head(m)"] = 1.0 + df["Head(m)"] + noise

    # dfi = isolate_recovery(time=df['Time(s)'].values, head=df['Head(m)'].values)

    Bouwer_Rice_1976(
        time=df["Time(s)"].values,
        head=df["Head(m)"].values,
        rc=0.064,
        rw=0.125,
        b=1.52,
        D=50.60,
        d=18.59,
        anis=1.0,
    )

    v = 1
    pass
