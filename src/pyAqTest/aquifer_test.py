# -*- coding: utf-8 -*-
"""
AquiferTest class for pumping/slug test analysis.

It includes methods for initializing the aquifer test, validating its properties,
and calculating transmissivity and storage coefficient.

"""


from typing import Dict, Any
from pyAqTest import Aquifer
from pyAqTest import Well

VALID_AQUIFER_TEST_TYPES = ["pumping", "slug"]

# make an abstract class for aquifer test
class AquiferTestBase:
    """
    Base class for aquifer tests.
    """

    def __init__(self, name:str, test_type:str = 'slug', aquifer: Aquifer = None, well: Well = None) -> None:
        self.name = name
        self.test_type = test_type
        self.aquifer = aquifer
        self.well = well
    
    def validate_required_properties(self) -> None:
        """
        Validate required properties of the aquifer test. This methood should ensure that the data
        provided for the aquifer test is complete.
        """
        pass
    def analyze(self) -> None:
        """
        Analyze the aquifer test.
        """
        pass
    def fit(self) -> None:
        """
        Fit the aquifer test data to a model.
        """
        pass
    def plot(self) -> None:
        """
        Plot the aquifer test data.
        """
        pass
    def __str__(self) -> str:
        return (
            f"AquiferTestBase(aquifer={self.aquifer}, "
               f"well={self.well})"
        )

   

# class AquiferTest:
#     def __init__(self,
#     test_id: str,
#      test_type: str,
#      aquifer: str,     
#      fitting_statistics: dict) -> None:
#         """
#         Initialize an AquiferTest object.
#         """

#         self.test_id = test_id
#         self.aquifer = aquifer
#         self.test_type = test_type
#         self.fitting_statistics = fitting_statistics

#     def __str__(self) -> str:
#         return (
#             f"AquiferTest(test_id={self.test_id}, "
#             f"aquifer={self.aquifer}, "
#             f"test_type={self.test_type}, "
#             f"fitting_statistics={self.fitting_statistics})"
#         )
#     def __repr__(self) -> str:
#         return (
#             f"AquiferTest(test_id={self.test_id}, "
#             f"aquifer={self.aquifer}, "
#             f"test_type={self.test_type}, "
#             f"fitting_statistics={self.fitting_statistics})"
#         )
#     def validate_required_properties(self) -> None:
#         """
