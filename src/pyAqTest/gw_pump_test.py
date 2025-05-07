""" classes for Well, pumping wells, slug wells, and obs wells"""

class Well:
    def __init__(
        self,
        well_id,
        well_type,
        location,
        ground_surface_elevation,
        casing_radius,
        well_radius,
        screen_length,
        screen_top_depth,
    ):
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

    def __str__(self):
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

    def __repr__(self):
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


class PumpingWell(Well):
    def __init__(
        self,
        well_id,
        location,
        ground_surface_elevation,
        casing_radius,
        well_radius,
        screen_length,
        screen_top_depth,
    ):
        super().__init__(
            well_id,
            "pumping",
            location,
            ground_surface_elevation,
            casing_radius,
            well_radius,
            screen_length,
            screen_top_depth,
        )

    def __str__(self):
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

    def __repr__(self):
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
        well_id,
        location,
        ground_surface_elevation,
        casing_radius,
        well_radius,
        screen_length,
        screen_top_depth,
    ):
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

    def __str__(self):
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
        well_id,
        location,
        ground_surface_elevation,
        casing_radius,
        well_radius,
        screen_length,
        screen_top_depth,
    ):
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

    def __str__(self):
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

    def __repr__(self):
        return (
            f"Slug Test Well ID: {self.well_id}, "
            f"Location: {self.location}, "
            f"Ground Surface Elevation: {self.ground_surface_elevation:.2f} m, "
            f"Screen Length: {self.screen_length:.2f} m, "
            f"Casing Radius: {self.casing_radius:.3f} m, "
            f"Well Radius: {self.well_radius:.3f} m, "
            f"Screen Top Depth: {self.screen_top_depth:.2f} m"
        )
