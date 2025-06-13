# -*- coding: utf-8 -*-
"""
Aquifer class for pumping/slug test analysis.

It includes methods for initializing the aquifer, validating its properties,
and calculating transmissivity and storage coefficient.
"""

VALID_AQUIFER_TYPES = ["unconfined", "confined", "semi-confined"]


class Aquifer:

    def __init__(
        self,
        name: str,
        aquifer_type: str,
        ground_surface_elevation: float,
        saturated_thickness: float,
        water_table_depth: float,
        radial_conductivity: float = None,
        vertical_conductivity: float = None,
        specific_yield: float = None,
        specific_storage: float = None,
        anisotropy: float = 1.0,
    ) -> None:
        """
        Initialize an Aquifer object.

        Parameters:
        aquifer_id (str): Unique identifier for the aquifer.
        aquifer_type (str): Type of the aquifer (e.g., "unconfined", "confined", "semi-confined").
        ground_surface_elevation (float): Elevation of the ground surface.
        saturated_thickness (float): Saturated thickness of the aquifer.
        water_table_depth (float): Depth to the groundwater table.
        radial_conductivity (float): Radial hydraulic conductivity of the aquifer.
        vertical_conductivity (float): Vertical hydraulic conductivity of the aquifer.
        specific_yield (float): Specific yield (Sy) of the aquifer.
        specific_storage (float): Specific storage (Ss) of the aquifer.
        anisotropy (float): Ratio of horizontal to vertical hydraulic conductivity.

        """
        # required properties
        self.name = name
        self.aquifer_type = aquifer_type
        self.saturated_thickness = saturated_thickness
        self.water_table_depth = water_table_depth
        self.anisotropy = anisotropy
        self.ground_surface_elevation = ground_surface_elevation
        self.set_default_values()
        self.validate_required_properties()

        # optional properties
        self.radial_conductivity = radial_conductivity
        self.vertical_conductivity = vertical_conductivity
        self.specific_yield = specific_yield
        self.specific_storage = specific_storage

    def __str__(self) -> str:
        # todo: fix all units
        return (
            "===========================================================\n"
            f"Aquifer Name: {self.name}\n"
            f"Aquifer Type: {self.aquifer_type}\n"
            f"Ground Surface Elevation: {self.ground_surface_elevation:.2f} m\n"
            f"Saturated Thickness: {self.saturated_thickness:.2f} m\n"
            f"Depth to Water Table: {self.water_table_depth:.2f} m\n"
            + (
                f"Radial Conductivity: {self.radial_conductivity:.3f} m/s\n"
                if self.radial_conductivity is not None
                else "Radial Conductivity: None\n"
            )
            + (
                f"Vertical Conductivity: {self.vertical_conductivity:.3f} m/s\n"
                if self.vertical_conductivity is not None
                else "Vertical Conductivity: None\n"
            )
            + (
                f"Storage Coefficient: {self.storage_coefficient:.3f}\n"
                if self.storage_coefficient is not None
                else "Storage Coefficient: None\n"
            )
            + (
                f"Specific Yield: {self.specific_yield:.3f}\n"
                if self.specific_yield is not None
                else "Specific Yield: None\n"
            )
            + (
                f"Specific Storage: {self.specific_storage:.3f} 1/m\n"
                if self.specific_storage is not None
                else "Specific Storage: None\n"
            )
            + f"Hydraulic Conductivity Anisotropy Ratio: {self.anisotropy:.3f}\n"
            "===========================================================\n"
        )

    # add a method to validate aquifer type
    def validate_aquifer_type(self) -> None:
        if self.aquifer_type not in VALID_AQUIFER_TYPES:
            raise ValueError(
                f"Invalid aquifer type: {self.aquifer_type}. Valid types are: {VALID_AQUIFER_TYPES}."
            )
        return None

        # add a property to calculate the storage coefficient

    @property
    def storage_coefficient(self) -> float:

        if self.aquifer_type == "unconfined":
            if self.specific_yield is None:
                return None
            self.storage_coefficient = self.specific_yield * self.saturated_thickness
        elif self.aquifer_type in ["confined", "semi-confined"]:
            if self.specific_storage is None:
                return None
            self.storage_coefficient = self.specific_storage * self.saturated_thickness
        else:
            raise ValueError(
                f"Invalid aquifer type: {self.aquifer_type}. Cannot calculate storage coefficient."
            )
        return self.storage_coefficient

    @property
    def transmissivity(self) -> float:
        transmissivity = self.radial_conductivity * self.saturated_thickness
        return transmissivity

    # apply default valuees for optional properties
    def set_default_values(self) -> None:
        if self.name is None:
            self.name = "Unammed Aquifer"

        if self.anisotropy is None:
            self.anisotropy = 1.0

        if self.ground_surface_elevation is None:
            self.ground_surface_elevation = 0.0

    # check if the aquifer has the required properties
    def validate_required_properties(self) -> bool:
        required_properties = [
            "aquifer_type",
            "ground_surface_elevation",
            "saturated_thickness",
            "water_table_depth",
        ]
        # Check if all required properties are not none
        for prop in required_properties:
            if getattr(self, prop) is None:
                raise ValueError(f"Error: {prop} is not set.")

    def validate_positive_values(self) -> None:
        if self.saturated_thickness <= 0:
            raise ValueError("Error: Saturated thickness must be positive.")
        if self.water_table_depth < 0:
            raise ValueError("Error: Depth to groundwater table must be >= 0.")

        if self.anisotropy < 0:
            raise ValueError("Error: Anisotropy ratio must be >= 0.")
