# -*- coding: utf-8 -*-

""" """
import matplotlib

matplotlib.use("TkAgg")
import numpy as np
import math

from scipy.stats import linregress
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import statsmodels.api as sm

from pyAqTest import Aquifer
from pyAqTest import SlugWell
from pyAqTest import AquiferTestBase
from pyAqTest.utils import evaluate_regression_fit, harmonize_units, get_static_level


# todo: think about simplifying the code by assuming that all data is recovery data


class Bouwer_Rice_1976(AquiferTestBase):
    """
    SlugTest class for slug test analysis.

    This class is used to analyze slug tests in aquifers. It includes methods for
    initializing the slug test, validating its properties, and calculating transmissivity
    and storage coefficient.

    """

    def __init__(
        self,
        name: str,
        test_type: str = "slug",
        aquifer: Aquifer = None,
        slug_well: SlugWell = None,
    ) -> None:
        super().__init__(name, test_type, aquifer=aquifer, well=slug_well)
        self.name = name
        self.test_type = "slug"
        self.aquifer = aquifer
        self.slug_well = slug_well
        self.validate_required_properties()
        self.harmonize_units()

        if self.slug_well.time_unit == "min":
            self.slug_well.time = self.slug_well.time * 60
        elif self.slug_well.time_unit == "hr":
            self.slug_well.time = self.slug_well.time * 3600
        self.slug_well.time_unit = "s"  # always in seconds

    def harmonize_units(self):
        """Harmonize the units of the slug test with the aquifer."""
        aquifer_length_unit = self.aquifer.length_unit
        slug_well_length_unit = self.slug_well.length_unit

        if aquifer_length_unit != slug_well_length_unit:
            # all should be in well length unit
            attribues = [
                "ground_surface_elevation",
                "saturated_thickness",
                "water_table_depth",
                "screen_length",
                "screen_top_depth",
                "casing_radius",
                "well_radius",
            ]

            for attr in attribues:
                if hasattr(self.aquifer, attr):
                    value = getattr(self.aquifer, attr)
                    new_value = harmonize_units(
                        value=value,
                        from_unit=aquifer_length_unit,
                        to_unit=slug_well_length_unit,
                    )
                    setattr(self.aquifer, attr, new_value)

    def validate_required_properties(self) -> None:
        """
        Validate required properties of the slug test. This method should ensure that the data
        provided for the slug test is complete.
        """
        # check data provided for the aquifer
        if not isinstance(self.aquifer, Aquifer):
            raise ValueError("Invalid aquifer object.")

        if not isinstance(self.slug_well, SlugWell):
            raise ValueError("Invalid slug well object.")
        if self.aquifer.saturated_thickness <= 0:
            raise ValueError("Saturated thickness must be greater than zero.")
        if self.slug_well.casing_radius <= 0:
            raise ValueError("Casing radius must be greater than zero.")

        # check length and time units
        if self.slug_well.length_unit not in ["m", "ft"]:
            raise ValueError("Length unit must be either 'm' or 'ft'.")
        if self.slug_well.time_unit not in ["s", "min", "hr"]:
            raise ValueError("Time unit must be either 's', 'min', or 'hr'.")

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

    def fit(self, x, y, method='scipy'):
        if method == 'scipy':
            result = linregress(x, y)
        elif method == 'Huber':
            huber_model = sm.RLM(y, x, M=sm.robust.norms.HuberT())
            huber_results = huber_model.fit()
            result = huber_results
        elif method == 'Tukey':
            tukey_model = sm.RLM(y, x, M=sm.robust.norms.TukeyBiweight())
            tukey_results = tukey_model.fit()
            result = tukey_results
        else:
            raise ValueError(f"Invalid method: {method}")
        return result

    def analyze(self) -> None:
        """
        Analyze the slug test.
        """
        # :param rc: raduis of the casing
        # :param rw: raduis of the well hole
        # :param anis: anisotropy ratio kz/kr
        # :param d: distance between water-table level and the top of the screen.
        # :param b: length of the screen, or length of the screen below water table.
        # :param D: saturated thickness of the aquifer
        # :param H0: theoretical increase (or decrease) in water level after adding the slug.
        # todo: H0 is the theoretical increase (or decrease) in water level after adding the slug.
        # head: head is groundwater level above the static level

        H0 = None
        gs_elev = self.aquifer.ground_surface_elevation
        gw_elv = gs_elev - self.aquifer.water_table_depth
        sreen_top_elev = gs_elev - self.slug_well.screen_top_depth
        screen_bottom_elev = sreen_top_elev - self.slug_well.screen_length
        head = self.slug_well.head
        time = self.slug_well.time
        D = self.aquifer.saturated_thickness
        rc = self.slug_well.casing_radius
        rw = self.slug_well.well_radius
        anis = self.aquifer.anisotropy
        d = gw_elv - sreen_top_elev
        b = np.abs(self.slug_well.screen_length)  # L

        if d < 0:
            d = 0

        # if self.slug_well.is_recovery_data:
        #     rec_depth = np.abs(head - head[-1])
        #     rec_time = time
        # else:
        #     rec_depth, rec_time = self.isolate_recovery(time, head, window_size=10)

        # get static level
        static_level = get_static_level(head)
        dev_static = head - static_level
        H0 = dev_static[0]
        h_normalized = dev_static / H0

        # min_non_zero = min(abs(x) for x in rec_depth if x != 0)
        # rec_depth[rec_depth == 0] = min_non_zero
        # if H0 is None:
        #     H0 = rec_depth[0]

        # h_h0 = rec_depth / H0
        mask = np.logical_and(h_normalized >= 0.1, h_normalized <= 0.3)
        mask2 = np.abs(h_normalized) > 10e-6
        mask = np.logical_and(mask2, mask)
        fit_result = self.fit(x=time[mask], y=np.log(np.abs(h_normalized[mask])), robust=True)

        # plot
        fig = plt.figure()
        x = time[mask2]
        y = h_normalized[mask2]
        y_fit = fit_result.slope * x + fit_result.intercept
        plt.scatter(x, y, label="Data")
        plt.plot(x, np.exp(y_fit), color="red", label="Fitted Line")
        plt.xlabel("Time")
        plt.ylabel(r"$\frac{H}{H_0}$")
        plt.yscale("log")
        plt.grid()
        plt.legend()
        plt.title(f"Linear Fit for test {self.name}")
        plt.ylim(1e-6, 1.2)
        self.viz_fig = fig
        plt.close()

        # evaluate model fit
        y_fit = fit_result.slope * time + fit_result.intercept
        fit_states = evaluate_regression_fit(
            y_obs=h_normalized[mask],
            y_pred=np.exp(y_fit[mask]),
            num_predictors=1,
            verbose=False,
        )

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
        term6 = np.log(np.abs(D - (d + b)) / rw_star) # todo: handle negative values
        if term6 > 6.0:
            term6 = 6.0
        part2 = (A + B * term6) / (b / rw_star)
        lnRw_rw = np.power((part1 + part2), -1.0)
        T0 = -1.0 / fit_result.slope
        k = (rc**2.0) * lnRw_rw / (2 * b * T0)

        self.estimated_parameters = {
            "transmissivity": k * D,
            "hydraulic_conductivity": k,
        }
        # self.fitting_statistics = {
        #     "slope": fit_result.slope,
        #     "intercept": fit_result.intercept,
        #     "r_value": fit_result.rvalue,
        #     "p_value": fit_result.pvalue,
        #     "std_err": fit_result.stderr,
        # }

        self.fitting_statistics = fit_states

    # wrie a function that print estimated parameters and fitting statistics in pretty format
    def print_estimated_parameters(self):

        print("\nSlug Test Analysis:")
        print(f"    Slug Test Name: {self.name}")
        print(f"    Slug Test Type: {self.test_type}")
        print(f"    Aquifer Name: {self.aquifer.name}")
        print(f"    Slug Well Name: {self.slug_well.name}")

        print("\nEstimated Parameters:")
        for key, value in self.estimated_parameters.items():
            print(f"    {key}: {value}")
        print("\nFitting Statistics:")
        for key, value in self.fitting_statistics.items():
            print(f"    {key}: {value}")


class Butler_2003(AquiferTestBase):
    def __init__(
        self,
        name: str,
        test_type: str = "slug",
        aquifer: Aquifer = None,
        slug_well: SlugWell = None,
    ) -> None:
        super().__init__(name, test_type, aquifer=aquifer, well=slug_well)
        self.name = name
        self.test_type = "slug"
        self.aquifer = aquifer
        self.slug_well = slug_well

        self.validate_required_properties()

        # harmonize units. Time is always in seconds!
        # length is well length unit
        self.harmonize_units()
        if self.slug_well.time_unit == "min":
            self.slug_well.time = self.slug_well.time * 60
        elif self.slug_well.time_unit == "hr":
            self.slug_well.time = self.slug_well.time * 3600

    def harmonize_units(self):
        """Harmonize the units of the slug test with the aquifer."""
        aquifer_length_unit = self.aquifer.length_unit
        slug_well_length_unit = self.slug_well.length_unit

        if aquifer_length_unit != slug_well_length_unit:
            # all should be in well length unit
            attribues = [
                "ground_surface_elevation",
                "saturated_thickness",
                "water_table_depth",
                "screen_length",
                "screen_top_depth",
                "casing_radius",
                "well_radius",
            ]

            for attr in attribues:
                if hasattr(self.aquifer, attr):
                    value = getattr(self.aquifer, attr)
                    new_value = harmonize_units(
                        value=value,
                        from_unit=aquifer_length_unit,
                        to_unit=slug_well_length_unit,
                    )
                    setattr(self.aquifer, attr, new_value)

    def validate_required_properties(self) -> None:
        """
        Validate required properties of the slug test. This method should ensure that the data
        provided for the slug test is complete.
        """
        # check data provided for the aquifer
        if not isinstance(self.aquifer, Aquifer):
            raise ValueError("Invalid aquifer object.")

        if not isinstance(self.slug_well, SlugWell):
            raise ValueError("Invalid slug well object.")
        if self.aquifer.saturated_thickness <= 0:
            raise ValueError("Saturated thickness must be greater than zero.")
        if self.slug_well.casing_radius <= 0:
            raise ValueError("Casing radius must be greater than zero.")

    def model(self, t, Cd, mod_factor):

        # ==========================
        # alpha is Cd
        if self.slug_well.length_unit == "m":
            g = 9.81  # time always in seconds
        else:
            g = 32.174
        # =============================
        omg = np.sqrt(abs(1 - (Cd / 2) ** 2))
        omg_pos = -Cd / 2 + np.sqrt(abs(1 - (Cd / 2) ** 2))
        omg_neg = -Cd / 2 - np.sqrt(abs(1 - (Cd / 2) ** 2))
        t_adj = t * mod_factor
        if Cd > 2:
            wd = (1 / (omg_neg - omg_pos)) * (
                omg_neg * np.exp(omg_pos * t_adj) - omg_pos * np.exp(omg_neg * t_adj)
            )
        elif Cd == 2:
            wd = np.exp(-t_adj) * (1 + t_adj)
        else:
            wd = np.exp(-Cd * t_adj / 2) * (
                np.cos(omg * t_adj) + (Cd / (2 * omg)) * np.sin(omg * t_adj)
            )

        return wd

    def fit(self, xdata, ydata, p0):
        # Use self.model — it's already bound to self
        popt, pcov = curve_fit(self.model, xdata, ydata, p0=p0)
        return popt, pcov

    def analyze(self) -> None:

        radius_of_transducer_cable = 0.003  # todo: make it a parameter
        if self.slug_well.length_unit == "m":
            g = 9.81  # todo: depends on units
        else:
            g = 32.174

        rtc = radius_of_transducer_cable
        depth_screen_bottom = (
            self.slug_well.screen_top_depth + self.slug_well.screen_length
        )
        water_table_depth = self.aquifer.water_table_depth
        b = self.slug_well.screen_length
        B = self.aquifer.saturated_thickness

        # Top of Screen to Water Table
        d = self.aquifer.water_table_depth - self.slug_well.screen_top_depth
        d = np.abs(d)
        rw = self.slug_well.well_radius
        rnc = self.slug_well.casing_radius
        head = self.slug_well.head
        time = self.slug_well.time

        # get static level
        static_level = get_static_level(head)
        dev_static = head - static_level
        H0 = dev_static[0]
        h_normalized = dev_static / H0

        p0 = [1.99, 1.0]
        popt, pcov = self.fit(time, h_normalized, p0=p0)
        cd = popt[0]
        modfac = popt[1]

        h_ = self.model(time, cd, modfac)

        # plot
        fig = plt.figure()
        plt.scatter(
            time,
            h_normalized,
            label="Normalized Data",
            facecolors="none",
            edgecolors="red",
            s=10,
        )
        plt.plot(time, h_, label="Fitted Model (Type Curve)")
        plt.xlabel("Time")
        plt.ylabel(r"Normalized head \n $\frac{H}{H_0}$")
        plt.grid()
        plt.legend()
        plt.title(f"Data Fit for test {self.name}")
        self.viz_fig = fig
        plt.close()

        # evaluate model fit
        fit_states = evaluate_regression_fit(
            y_obs=h_normalized, y_pred=h_, num_predictors=1, verbose=False
        )

        # compute k
        tfac = modfac

        N8 = 32.174 / (tfac**2)
        N9 = depth_screen_bottom - (b + water_table_depth) + b / 2 * (rnc**2 / rw**2)
        N10 = abs(N8 - N9) / N9

        # Already defined in names: rc = I9, ar = I11
        rc = math.sqrt(rnc**2 - rtc**2)
        ar = b / rw
        V7 = (ar / 2) + math.sqrt(1 + (ar / 2) ** 2)

        # V18 polynomial
        V18 = (
            1.472
            + 0.03537 * ar
            - 0.00008148 * ar**2
            + 0.0000001028 * ar**3
            - 0.00000000006484 * ar**4
            + 0.00000000000001573 * ar**5
        )

        # V19 polynomial
        V19 = (
            0.2372
            + 0.005151 * ar
            - 0.000002682 * ar**2
            - 0.0000000003491 * ar**3
            + 0.0000000000004738 * ar**4
        )

        # T21 and U24 logic
        T21 = 1.1 / math.log((d + b) / rw)
        X24 = math.log(np.abs(B - (d + b)) / rw)
        U24 = min(6, X24)
        U23 = (V18 + V19 * U24) / ar
        S18 = 1 / (T21 + U23)

        # Hydraulic conductivity (kr) calculations
        kr_conf = (tfac * rc**2 * math.log(V7)) / (2 * b * cd)
        kr_unconf = (tfac * rc**2 * S18) / (2 * b * cd)

        if self.aquifer.aquifer_type.lower() == "unconfined":
            k = kr_unconf

        elif self.aquifer.aquifer_type.lower() == "confined":
            k = kr_conf
        else:
            raise ValueError(
                f"Aquifer type '{self.aquifer.aquifer_type.lower()}' is unknown ... "
            )

        self.estimated_parameters = {
            "transmissivity": k * B,
            "hydraulic_conductivity": k,
        }
        self.fitting_statistics = fit_states

    def print_estimated_parameters(self):
        print("\nSlug Test Analysis:")
        print(f"    Slug Test Name: {self.name}")
        print(f"    Slug Test Type: {self.test_type}")
        print(f"    Aquifer Name: {self.aquifer.name}")
        print(f"    Slug Well Name: {self.slug_well.name}")

        print("\nEstimated Parameters:")
        for key, value in self.estimated_parameters.items():
            print(f"    {key}: {value}")
        print("\nFitting Statistics:")
        for key, value in self.fitting_statistics.items():
            print(f"    {key}: {value}")
