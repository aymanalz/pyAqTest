"""
Well Module

This module defines classes for different types of wells, including
PumpingWell, ObservationWell, and SlugTestWell.

Note:
- The units for all parameters must be consistent. For example, if the
    casing radius is in meters, all other dimensions should also be in
    meters.
- The same applies to time units, such as seconds or hours.
"""

from typing import Union, Tuple
import pandas as pd
import numpy as np

VALID_WELL_TYPES = ["pumping", "slug", "observation"]


class Well:
    def __init__(
        self,
        name: str,
        well_type: str,
        location: Tuple[float, float],
        casing_radius: float,
        well_radius: float,
        screen_length: float,
        screen_top_depth: float,
        length_unit: str = None,
        time_unit: str = None,
    ) -> None:
        """
        A base class for wells

        :param name:
        :param well_type:
        :param location:

        :param casing_radius:
        :param well_radius:
        :param screen_length:
        :param screen_top_depth:
        """

        self.name = name
        self.location = location
        self.well_type = well_type  # ['pumping', 'slug', 'observation']
        self.screen_length = screen_length
        self.casing_radius = casing_radius
        self.well_radius = well_radius
        self.screen_top_depth = screen_top_depth
        self.length_unit = length_unit
        self.time_unit = time_unit
         
        self.validate_casing_radius()
        self.validate_well_type()  # validate well type
        self.validate_length_and_time_units()

    def __str__(self) -> str:
        return (
            f"===========================================================\n"
            f"Well Name: {self.name}\n"
            f"Location: {self.location}\n"
            f"Well Type: {self.well_type.capitalize()}\n"
            f"Screen Length: {self.screen_length:.2f} m\n"
            f"Casing Radius: {self.casing_radius:.3f} m\n"
            f"Well Radius: {self.well_radius:.3f} m\n"
            f"Screen Top Depth: {self.screen_top_depth:.2f} m\n"
            f"===========================================================\n"
        )

    def __repr__(self) -> str:
        return (
            f"Well Name: {self.name}, "
            f"Location: {self.location}, "
            f"Well Type: {self.well_type.capitalize()}, "
            f"Screen Length: {self.screen_length:.2f} m, "
            f"Casing Radius: {self.casing_radius:.3f} m, "
            f"Well Radius: {self.well_radius:.3f} m, "
            f"Screen Top Depth: {self.screen_top_depth:.2f} m"
        )

    def validate_positive_values(self) -> Union[None, str]:
        if self.casing_radius <= 0:
            return "Error: Casing radius must be positive."
        if self.well_radius <= 0:
            return "Error: Well radius must be positive."
        if self.screen_length <= 0:
            return "Error: Screen length must be positive."
        if self.screen_top_depth <= 0:
            return "Error: Screen top depth must be positive."
        return None

    def validate_casing_radius(self) -> Union[None, str]:
        if self.casing_radius >= self.well_radius:
            return (
                f"Error: Casing radius ({self.casing_radius:.3f} m) "
                f"must be less than well radius ({self.well_radius:.3f} m)."
            )
        return None

    def set_default_values(self) -> None:
        if self.casing_radius is None:
            self.casing_radius = 0.1
        if self.well_radius is None:
            self.well_radius = 0.15
        if self.screen_length is None:
            self.screen_length = 10.0
        if self.screen_top_depth is None:
            self.screen_top_depth = 5.0
        if self.location is None:
            self.location = (0.0, 0.0)

    def validate_well_type(self) -> Union[None, str]:
        if self.well_type.lower() not in VALID_WELL_TYPES:
            return (
                f"Error: Invalid well type '{self.well_type}'. "
                f"Valid types are: {', '.join(VALID_WELL_TYPES)}."
            )
        return None
    
    def validate_length_and_time_units(self) -> Union[None, str]:
        if self.length_unit not in ["m", "ft"]:
            return (
                f"Error: Invalid length unit '{self.length_unit}'. "
                f"Must be 'm' or 'ft'."
            )
        if self.time_unit not in ["s", "min", "h"]:
            return (
                f"Error: Invalid time unit '{self.time_unit}'. "
                f"Must be 's', 'min', or 'h'."
            )
        return None


class PumpingWell(Well):
    """A class for pumping wells"""

    def __init__(
        self,
        name: str,
        well_type: str,
        location: str,
        ground_surface_elevation: float,
        casing_radius: float,
        well_radius: float,
        screen_length: float,
        screen_top_depth: float,
        pumping_rate: Union[float, pd.DataFrame],
        pumping_period: float,
    ) -> None:

        super().__init__(
            name,
            well_type,
            location,
            ground_surface_elevation,
            casing_radius,
            well_radius,
            screen_length,
            screen_top_depth,
        )

        print("init...........")
        self.validate_pumping_date(pumping_rate, pumping_period)

    def __str__(self) -> str:
        return (
            f"===========================================================\n"
            f"Pumping Well Name: {self.name}\n"
            f"Location: {self.location}\n"
            f"Ground Surface Elevation: {self.ground_surface_elevation:.2f} m\n"
            f"Screen Length: {self.screen_length:.2f} m\n"
            f"Casing Radius: {self.casing_radius:.3f} m\n"
            f"Well Radius: {self.well_radius:.3f} m\n"
            f"Screen Top Depth: {self.screen_top_depth:.2f} m\n"
            f"===========================================================\n"
        )

    def __repr__(self) -> str:
        return (
            f"Pumping Well Name: {self.name}, "
            f"Location: {self.location}, "
            f"Ground Surface Elevation: {self.ground_surface_elevation:.2f} m, "
            f"Screen Length: {self.screen_length:.2f} m, "
            f"Casing Radius: {self.casing_radius:.3f} m, "
            f"Well Radius: {self.well_radius:.3f} m, "
            f"Screen Top Depth: {self.screen_top_depth:.2f} m"
        )

    def validate_pumping_date(self, pumping_rate, pumping_period) -> Union[None, str]:

        if isinstance(pumping_rate, float):
            if pumping_period is not None:
                self.pumping_rate = pd.DataFrame(
                    {
                        "time": [0, pumping_period],
                        "rate": [pumping_rate, pumping_rate],
                    }
                )
            else:
                raise ValueError(
                    "Error: Pumping period must be provided if pumping rate is a float."
                )

        # Check if pumping_rate is a dataframe
        elif isinstance(pumping_rate, pd.DataFrame):
            if "time" not in pumping_rate.columns:
                raise ValueError(
                    "Error: Pumping rate DataFrame must contain a 'time' column."
                )

            if "rate" not in pumping_rate.columns:
                raise ValueError(
                    "Error: Pumping rate DataFrame must contain a 'rate' column."
                )
            # Check if time is numeric
            if not pd.api.types.is_numeric_dtype(pumping_rate["time"]):
                if not pd.api.types.is_datetime64_any_dtype(pumping_rate["time"]):
                    raise ValueError(
                        "Error: 'time' column must be numeric or datetime."
                    )

            # Check if rate is numeric
            if not pd.api.types.is_numeric_dtype(pumping_rate["rate"]):
                raise ValueError("Error: 'rate' column must be numeric.")

            self.pumping_rate = pumping_rate

        else:  # Pumping rate is not a float or DataFrame
            raise ValueError("Pumping rate must be a float or a pandas DataFrame.")


class ObservationWell(Well):
    def __init__(
        self,
        name: str,
        location: str,
        ground_surface_elevation: float,
        casing_radius: float,
        well_radius: float,
        screen_length: float,
        screen_top_depth: float,
    ) -> None:
        super().__init__(
            name,
            "observation",
            location,
            ground_surface_elevation,
            casing_radius,
            well_radius,
            screen_length,
            screen_top_depth,
        )

    def __str__(self) -> str:
        return (
            f"===========================================================\n"
            f"Observation Well Name: {self.name}\n"
            f"Location: {self.location}\n"
            f"Ground Surface Elevation: {self.ground_surface_elevation:.2f} m\n"
            f"Screen Length: {self.screen_length:.2f} m\n"
            f"Casing Radius: {self.casing_radius:.3f} m\n"
            f"Well Radius: {self.well_radius:.3f} m\n"
            f"Screen Top Depth: {self.screen_top_depth:.2f} m\n"
            f"===========================================================\n"
        )


class SlugWell(Well):
    def __init__(
        self,
        name: str = "unamed_slug_well",
        well_type: str = "slug",
        location: Tuple[float, float] = None,
        casing_radius: float = None,
        well_radius: float = None,
        screen_length: float = None,
        screen_top_depth: float = None,
        head: Union[np.array, pd.DataFrame] = None,
        time: Union[np.array, pd.DataFrame] = None,
        slug_volume: float = None,
        is_recovery_data: bool = False,
        length_unit: str = "m",
        time_unit: str = "s"
    ) -> None:

        super().__init__(
            name,
            well_type,
            location,
            casing_radius,
            well_radius,
            screen_length,
            screen_top_depth,
            length_unit=length_unit,
            time_unit=time_unit,
        )

        self.well_type = "slug"
        self.head = head
        self.time = time
        self.slug_volume = slug_volume
        self.is_recovery_data = is_recovery_data

    def __str__(self) -> str:
        return (
            f"==================================== \n"
            f"Slug Test Well Name: {self.name}\n"
            f"Location: {self.location}\n"
            f"Well Type: {self.well_type.capitalize()}\n"
            f"Casing Radius: {self.casing_radius if self.casing_radius is not None else 'N/A'} m\n"
            f"Well Radius: {self.well_radius if self.well_radius is not None else 'N/A'} m\n"
            f"Screen Length: {self.screen_length if self.screen_length is not None else 'N/A'} m\n"
            f"Screen Top Depth: {self.screen_top_depth if self.screen_top_depth is not None else 'N/A'} m\n"
            f"Slug Volume: {self.slug_volume if hasattr(self, 'slug_volume') and self.slug_volume is not None else 'N/A'} m³\n"
            f"==================================== \n"
        )

    def __repr__(self) -> str:
        return (
            f"Slug Test Well Name: {self.name}, "
            f"Location: {self.location}, "
            f"Well Type: {self.well_type.capitalize()}, "
            f"Casing Radius: {self.casing_radius if self.casing_radius is not None else 'N/A'} m, "
            f"Well Radius: {self.well_radius if self.well_radius is not None else 'N/A'} m, "
            f"Screen Length: {self.screen_length if self.screen_length is not None else 'N/A'} m, "
            f"Screen Top Depth: {self.screen_top_depth if self.screen_top_depth is not None else 'N/A'} m, "
            f"Slug Volume: {self.slug_volume if hasattr(self, 'slug_volume') and self.slug_volume is not None else 'N/A'} m³"
        )
