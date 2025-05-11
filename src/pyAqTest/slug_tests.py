# -*- coding: utf-8 -*-

""" """

import numpy as np
from scipy.special import expi
import numpy as np
import pandas as pd
from scipy.stats import linregress
import matplotlib.pyplot as plt

from pyAqTest import Aquifer
from pyAqTest import PumpingWell, SlugWell, Well, ObservationWell
from pyAqTest import AquiferTestBase
from typing import Dict, Any, List

class Bouwer_Rice_1976(AquiferTestBase):
    """
    SlugTest class for slug test analysis.

    This class is used to analyze slug tests in aquifers. It includes methods for
    initializing the slug test, validating its properties, and calculating transmissivity
    and storage coefficient.

    """    

    def __init__(self, name: str, test_type: str = 'slug', aquifer: Aquifer = None, slug_well: SlugWell = None) -> None:
        super().__init__(name, test_type, aquifer=aquifer, well=slug_well)
        self.name = name
        self.test_type = 'slug'
        self.aquifer = aquifer
        self.slug_well = slug_well
        self.validate_required_properties()
        
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
            window_before = head[i - window_size: i]
            window_after = head[i: i + window_size]

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
            j = np.argmax(head[max_i - window_size: max_i + window_size])
        else:
            j = np.argmin(head[max_i - window_size: max_i + window_size])

        static_level = np.mean(head[j - window_size: j - 1])
        recovery_start = max_i + j
        recovery_depth = head[recovery_start:] - static_level
        recovery_time = time[recovery_start:]
        return recovery_depth, recovery_time
    
    def fit(self, x, y):
        result = linregress(x, y)
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
        b = self.slug_well.screen_length

        rec_head, rec_time = self.isolate_recovery(time, head, window_size=10)
        if H0 is None:
            H0 = rec_head[0]

        fit_result = self.fit(x=rec_time, y=np.log(rec_head / H0))

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

        self.estimated_parameters = {
            "transmissivity": k*D,
            "hydraulic_conductivity": k
        }
        self.fitting_statistics = {
            "slope": fit_result.slope,
            "intercept": fit_result.intercept,
            "r_value": fit_result.rvalue,
            "p_value": fit_result.pvalue,
            "std_err": fit_result.stderr,
        }
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
       

    
    
# if __name__ == "__main__":
    

# class Bouwer_Rice_1976(object):
#     """
#     Bouwer and Rice (1976) method for slug test analysis.

#     Bouwer, H., & Rice, R. C. (1976). A slug test for determining hydraulic conductivity
#     of unconfined aquifers with completely or partially penetrating wells. Water
#     Resources Research, 12(3), 423–428. https://doi.org/10.1029/WR012i003p00423

#     This method is used to determine the hydraulic conductivity of unconfined aquifers
#     using slug tests. The method is based on the analysis of the recovery of water levels
#     in a well after a slug is added or removed. The method assumes that the aquifer is
#     homogeneous and isotropic, and that the well is fully penetrating.
#     """


#     def __init__(self, aquifer: Aquifer, slug_well: SlugWell) -> None:

#         self.aquifer = aquifer
#         self.slug_well = slug_well

#     def fit(self, x, y):
#         result = linregress(x, y)
#         return result

#     def isolate_recovery(self, time, head, window_size=10):
#         """
#         Slug data can be for a case were water table is lowered or raised, so
#         we need first to isolate the part related to recovery

#         :param window_size:
#         :param time:
#         :param head:
#         :return:
#         """

#         max_change = 0
#         max_i = 0
#         signed_max_diff = 0

#         for i in range(window_size, len(head) - window_size):
#             window_before = head[i - window_size: i]
#             window_after = head[i: i + window_size]

#             mean_before = np.mean(window_before)
#             mean_after = np.mean(window_after)

#             diff = abs(mean_after - mean_before)
#             if diff > max_change:
#                 max_change = diff
#                 max_i = i
#                 signed_max_diff = mean_after - mean_before

#         # within the window around max_i, choose the maximum (or the minimum) chane
#         # depending on the sign of the change
#         if signed_max_diff > 0:
#             j = np.argmax(head[max_i - window_size: max_i + window_size])
#         else:
#             j = np.argmin(head[max_i - window_size: max_i + window_size])

#         static_level = np.mean(head[j - window_size: j - 1])
#         recovery_start = max_i + j
#         recovery_depth = head[recovery_start:] - static_level
#         recovery_time = time[recovery_start:]
#         return recovery_depth, recovery_time

#     def analyze(self, time, head, rc, rw, anis, d, b, D, H0=None):
#         """

#         :param time:
#         :param head:
#         :param rc: raduis of the casing
#         :param rw: raduis of the well hole
#         :param anis: anisotropy ratio kz/kr
#         :param d: distance between water-table level and the top of the screen.
#         :param b: length of the screen, or length of the screen below water table.
#         :param D: saturated thickness of the aquifer
#         :param H0: theoretical increase (or decrease) in water level after adding the slug.
#         :return:
#         """
        
#         D = self.aquifer.saturated_thickness
#         rc = self.slug_well.casing_radius
#         rw = self.slug_well.well_radius
#         anis = self.aquifer.anisotropy_ratio

#         rec_head, rec_time = self.isolate_recovery(time, head, window_size=10)
#         if H0 is None:
#             H0 = rec_head[0]

#         fit_result = fit(x=rec_time, y=np.log(rec_head / H0))

#         # plot
#         x = rec_time
#         y = np.log(rec_head / H0)
#         y_fit = fit_result.slope * x + fit_result.intercept
#         plt.scatter(x, y, label="Data")
#         plt.plot(x, y_fit, color="red", label="Fitted Line")
#         plt.legend()
#         plt.title("Linear Fit using SciPy")
#         plt.show()
#         #

#         rw_star = rw * (anis**0.5)
#         x = np.log10(b / rw_star)

#         xs = np.array([1, x, x**2.0, x**3.0, x**4.0])
#         betaA = np.array([1.353, 2.157, -4.0270, 2.777, -0.460])
#         betaB = np.array([-0.401, 2.619, -3.2670, 1.548, -0.210])
#         betaC = np.array([-1.605, 9.496, -12.317, 6.528, -0.986])
#         A = np.dot(xs, betaA)
#         B = np.dot(xs, betaB)
#         C = np.dot(xs, betaC)

#         part1 = 1.1 / (np.log((d + b) / rw_star))
#         term6 = np.log((D - (d + b)) / rw_star)
#         if term6 > 6.0:
#             term6 = 6.0
#         part2 = (A + B * term6) / (b / rw_star)
#         lnRw_rw = np.power((part1 + part2), -1.0)
#         T0 = -1.0 / fit_result.slope
#         k = (rc**2.0) * lnRw_rw / (2 * b * T0)

#         return k
