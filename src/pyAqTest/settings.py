import configparser


class Batch_Settings:
    def __init__(self):
        self.raw_data_folder = "."
        self.batch_data_file = r".\batch_info.csv"
        self.file_type = "csv"
        self.length_unit = "m"
        self.time_unit = "s"
        self.time_col = "Time"
        self.head_col = "Head"
        extract_recovery = True

        self.log_file = "logging.log"
        self.output_folder = r"output"
        # self.processed_data_folder = "processed_data"

        self.test_id_col = "test_id"
        self.test_type_col = "test_type"
        self.test_id_col = "test_id"
        self.test_type_col = "test_type"
        self.aquifer_name_col = "aquifer_name"
        self.aquifer_type_col = "aquifer_type"
        self.aquifer_thickness_col = "aquifer_thickness"
        self.water_table_depth_col = "water_table_depth"
        self.anisotropy_col = "anisotropy"
        self.well_name_col = "well_name"
        self.well_radius_col = "well_radius"
        self.casing_radius_col = "casing_radius"
        self.screen_length_col = "screen_length"
        self.screen_top_depth_col = "screen_top_depth"
        self.data_file_col = "test_data_file"
        self.slug_volume_col = "slug_volume"
        self.solution_method_col = "solution_method"

    def get_default(self, key):
        if not hasattr(self, key):
            raise KeyError(f"Config key '{key}' is not a valid setting.")
        default_value = getattr(self, key)
        if default_value.strip().lower() in ["true"]:
            return True
        elif default_value.strip().lower() in ["false"]:
            return False
        else:
            return default_value

    def generate_default_config_file(self, filename="default_config.ini"):
        """Generate a default configuration file.

        Parameters
        ----------
        filename : str

           Name of the configuration file to be generated.
           Default is 'default_config.ini'.

        Returns
           None"""
        # todo: this function should be tested.
        config = configparser.ConfigParser()

        config["Input Info"] = {
            "raw_data_folder": self.input_folder,
            "file_type": self.file_type,
            "length_unit": self.length_unit,
            "time_unit": self.time_unit,
            "batch_data_file": self.batch_data_file,
            "time_col": self.time_col,
            "head_col": self.head_col,
        }

        config["Output Info"] = {
            "log_file": self.log_file,
            "output_folder": self.output_folder,
            "processed_data_folder": self.processed_data_folder,
        }

        config["Batch File Schema"] = {
            "test_id": self.test_id_col,
            "test_type": self.test_type_col,
            "aquifer_name": self.aquifer_name_col,
            "aquifer_type": self.aquifer_type_col,
            "aquifer_thickness": self.aquifer_thickness_col,
            "water_table_depth": self.water_table_depth_col,
            "anisotropy": self.anisotropy_col,
            "well_name": self.well_name_col,
            "well_radius": self.well_radius_col,
            "casing_radius": self.casing_radius_col,
            "screen_length": self.screen_length_col,
            "screen_top_depth": self.screen_top_depth_col,
            "test_data_file": self.data_file_col,
            "slug_volume": self.slug_volume_col,
            "solution_method": self.solution_method_col,
        }

        with open(filename, "w") as configfile:
            config.write(configfile)
        print(f"Default configuration file '{filename}' generated.")
