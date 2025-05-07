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

VALID_WELL_TYPES = ["pumping", "slug", "observation"]


class Well:
    def __init__(
        self,
        well_id: str,
        well_type: str,
        location: Tuple[float, float],
        ground_surface_elevation: float,
        casing_radius: float,
        well_radius: float,
        screen_length: float,
        screen_top_depth: float,
    ) -> None:
        """
        A base class for wells

        :param well_id:
        :param well_type:
        :param location:
        :param ground_surface_elevation:
        :param casing_radius:
        :param well_radius:
        :param screen_length:
        :param screen_top_depth:
        """

        self.well_id = well_id
        self.location = location
        self.well_type = well_type  # ['pumping', 'slug', 'observation']
        self.ground_surface_elevation = ground_surface_elevation
        self.screen_length = screen_length
        self.casing_radius = casing_radius
        self.well_radius = well_radius
        self.screen_top_depth = screen_top_depth

        self.set_default_values()
        self.validate_casing_radius()
        self.validate_well_type()  # validate well type

    def __str__(self) -> str:
        return (
            f"==================================== \n"
            f"Well ID: {self.well_id}\n"
            f"Location: {self.location}\n"
            f"Well Type: {self.well_type.capitalize()}\n"
            f"Ground Surface Elevation: {self.ground_surface_elevation:.2f} m\n"
            f"Screen Length: {self.screen_length:.2f} m\n"
            f"Casing Radius: {self.casing_radius:.3f} m\n"
            f"Well Radius: {self.well_radius:.3f} m\n"
            f"Screen Top Depth: {self.screen_top_depth:.2f} m\n"
            f"==================================== \n"
        )

    def __repr__(self) -> str:
        return (
            f"Well ID: {self.well_id}, "
            f"Location: {self.location}, "
            f"Well Type: {self.well_type.capitalize()}, "
            f"Ground Surface Elevation: {self.ground_surface_elevation:.2f} m, "
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
        if self.ground_surface_elevation is None:
            self.ground_surface_elevation = 0.0
        if self.location is None:
            self.location = (0.0, 0.0)

    def validate_well_type(self) -> Union[None, str]:
        if self.well_type.lower() not in VALID_WELL_TYPES:
            return (
                f"Error: Invalid well type '{self.well_type}'. "
                f"Valid types are: {', '.join(VALID_WELL_TYPES)}."
            )
        return None


class PumpingWell(Well):
    """A class for pumping wells"""

    def __init__(
        self,
        well_id: str,
        pumping_rate: Union[float, pd.DataFrame],
        location: str,
        ground_surface_elevation: float,
        casing_radius: float,
        well_radius: float,
        screen_length: float,
        screen_top_depth: float,
    ) -> None:
        super().__init__(
            well_id,
            pumping_rate,
            location,
            ground_surface_elevation,
            casing_radius,
            well_radius,
            screen_length,
            screen_top_depth,
        )

    def __str__(self) -> str:
        return (
            f"==================================== \n"
            f"Pumping Well ID: {self.well_id}\n"
            f"Location: {self.location}\n"
            f"Ground Surface Elevation: {self.ground_surface_elevation:.2f} m\n"
            f"Screen Length: {self.screen_length:.2f} m\n"
            f"Casing Radius: {self.casing_radius:.3f} m\n"
            f"Well Radius: {self.well_radius:.3f} m\n"
            f"Screen Top Depth: {self.screen_top_depth:.2f} m\n"
            f"==================================== \n"
        )

    def __repr__(self) -> str:
        return (
            f"Pumping Well ID: {self.well_id}, "
            f"Location: {self.location}, "
            f"Ground Surface Elevation: {self.ground_surface_elevation:.2f} m, "
            f"Screen Length: {self.screen_length:.2f} m, "
            f"Casing Radius: {self.casing_radius:.3f} m, "
            f"Well Radius: {self.well_radius:.3f} m, "
            f"Screen Top Depth: {self.screen_top_depth:.2f} m"
        )


class ObservationWell(Well):
    def __init__(
        self,
        well_id: str,
        location: str,
        ground_surface_elevation: float,
        casing_radius: float,
        well_radius: float,
        screen_length: float,
        screen_top_depth: float,
    ) -> None:
        super().__init__(
            well_id,
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
            f"==================================== \n"
            f"Observation Well ID: {self.well_id}\n"
            f"Location: {self.location}\n"
            f"Ground Surface Elevation: {self.ground_surface_elevation:.2f} m\n"
            f"Screen Length: {self.screen_length:.2f} m\n"
            f"Casing Radius: {self.casing_radius:.3f} m\n"
            f"Well Radius: {self.well_radius:.3f} m\n"
            f"Screen Top Depth: {self.screen_top_depth:.2f} m\n"
            f"==================================== \n"
        )


class SlugTestWell(Well):
    def __init__(
        self,
        well_id: str,
        location: str,
        ground_surface_elevation: float,
        casing_radius: float,
        well_radius: float,
        screen_length: float,
        screen_top_depth: float,
    ) -> None:
        super().__init__(
            well_id,
            "slug",
            location,
            ground_surface_elevation,
            casing_radius,
            well_radius,
            screen_length,
            screen_top_depth,
        )

    def __str__(self) -> str:
        return (
            f"==================================== \n"
            f"Slug Test Well ID: {self.well_id}\n"
            f"Location: {self.location}\n"
            f"Ground Surface Elevation: {self.ground_surface_elevation:.2f} m\n"
            f"Screen Length: {self.screen_length:.2f} m\n"
            f"Casing Radius: {self.casing_radius:.3f} m\n"
            f"Well Radius: {self.well_radius:.3f} m\n"
            f"Screen Top Depth: {self.screen_top_depth:.2f} m\n"
            f"==================================== \n"
        )

    def __repr__(self) -> str:
        return (
            f"Slug Test Well ID: {self.well_id}, "
            f"Location: {self.location}, "
            f"Ground Surface Elevation: {self.ground_surface_elevation:.2f} m, "
            f"Screen Length: {self.screen_length:.2f} m, "
            f"Casing Radius: {self.casing_radius:.3f} m, "
            f"Well Radius: {self.well_radius:.3f} m, "
            f"Screen Top Depth: {self.screen_top_depth:.2f} m"
        )
