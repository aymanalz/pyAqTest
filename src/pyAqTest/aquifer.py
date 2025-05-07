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
        aquifer_id: str,
        aquifer_type: str,
        ground_surface_elevation: float,
        saturated_thickness: float,
        depth_to_confining_layer: float,
        radial_conductivity: float,
        vertical_conductivity: float,
        specific_yield: float,
        specific_storage: float,
        hydraulic_conductivity_anisotropy_ratio: float,
    ) -> None:
        """
        Initialize an Aquifer object.

        Parameters:
        aquifer_id (str): Unique identifier for the aquifer.
        aquifer_type (str): Type of the aquifer (e.g., "unconfined", "confined", "semi-confined").
        ground_surface_elevation (float): Elevation of the ground surface .
        saturated_thickness (float): Saturated thickness of the aquifer.
        depth_to_confining_layer (float): Depth to the confining layer.
        radial_conductivity (float): Radial hydraulic conductivity of the aquifer.
        vertical_conductivity (float): Vertical hydraulic conductivity of the aquifer.
        specific_yield (float): Specific yield (Sy) of the aquifer.
        specific_storage (float): Specific storage (Ss) of the aquifer.
        hydraulic_conductivity_anisotropy_ratio (float): Ratio of horizontal to vertical hydraulic conductivity.


        """
        self.aquifer_id = aquifer_id
        self.aquifer_type = aquifer_type
        self.ground_surface_elevation = ground_surface_elevation
        self.saturated_thickness = saturated_thickness
        self.depth_to_confining_layer = depth_to_confining_layer
        self.validate_required_properties()

        self.radial_conductivity = radial_conductivity
        self.vertical_conductivity = vertical_conductivity
        self.specific_yield = specific_yield
        self.specific_storage = specific_storage
        self.hydraulic_conductivity_anisotropy_ratio = (
            hydraulic_conductivity_anisotropy_ratio
        )

    def __str__(self) -> str:
        return (
            f"Aquifer ID: {self.aquifer_id}\n"
            f"Aquifer Type: {self.aquifer_type}\n"
            f"Ground Surface Elevation: {self.ground_surface_elevation:.2f} m\n"
            f"Saturated Thickness: {self.saturated_thickness:.2f} m\n"
            f"Depth to Confining Layer: {self.depth_to_confining_layer:.2f} m\n"
            f"Radial Conductivity: {self.radial_conductivity:.3f} m/s\n"
            f"Vertical Conductivity: {self.vertical_conductivity:.3f} m/s\n"
            f"Storage Coefficient: {self.storage_coefficient:.3f}\n"
            f"Specific Yield: {self.specific_yield:.3f}\n"
            f"Specific Storage: {self.specific_storage:.3f} 1/m\n"
            f"Hydraulic Conductivity Anisotropy Ratio: {self.hydraulic_conductivity_anisotropy_ratio:.3f}\n"
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
            self.storage_coefficient = self.specific_yield * self.saturated_thickness
        elif self.aquifer_type in ["confined", "semi-confined"]:
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

    # check if the aquifer has the required properties
    def validate_required_properties(self) -> bool:
        required_properties = [
            "aquifer_type",
            "ground_surface_elevation",
            "saturated_thickness",
            "depth_to_confining_layer",
        ]
        # Check if all required properties are not none
        for prop in required_properties:
            if getattr(self, prop) is None:
                raise ValueError(f"Error: {prop} is not set.")

                # check if thickness, depths are positive

    def validate_positive_values(self) -> None:
        if self.saturated_thickness <= 0:
            raise ValueError("Error: Saturated thickness must be positive.")
        if self.depth_to_confining_layer <= 0:
            raise ValueError("Error: Depth to confining layer must be positive.")
