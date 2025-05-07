# -*- coding: utf-8 -*-
# """
# AquiferTest class for pumping/slug test analysis.
#
# It includes methods for initializing the aquifer test, validating its properties,
# and calculating transmissivity and storage coefficient.
#
# """


from typing import Dict, Any
from aquifer import Aquifer
from wells import Well, PumpingWell, SlugWell



VALID_AQUIFER_TEST_TYPES = ["pumping", "slug"]



class AquiferTest:
    def __init__(self,
    test_id: str,
     test_type: str,
     aquifer: str,
     analytical_solution: str,
     fitting_method: str,
     fitting_statistics: dict) -> None:
        """
        Initialize an AquiferTest object.
        """

        self.test_id = test_id
        self.aquifer = aquifer
        self.test_type = test_type
        self.solution_type = solution_type
        self.fitting_method = fitting_method
        self.fitting_statistics = fitting_statistics

    def __str__(self) -> str:
        return (
            f"Aquifer Test ID: {self.test_id}\n"
            f"Aquifer ID: {self.aquifer_id}\n"
            f"Test Type: {self.test_type}\n"
            f"Solution Type: {self.solution_type}\n"
            f"Fitting Method: {self.fitting_method}\n"
            f"Fitting Statistics: {self.fitting_statistics}\n"
        )
