import os
import shutil
import configparser

import pandas as pd
from pyAqTest import Aquifer, SlugWell, Bouwer_Rice_1976, Butler_2003

from .settings import Batch_Settings
from .utils import insitu_to_csv
from .report import gererate_report, make_schematic_plot
from datetime import date

# from .report import generate_html_report

"""
To process a large number of pumping tests in batch mode, we need first to standardize the input data fromat.
Since slug and pumping tests can come in many different formats, we need to create a standard format for the
input data.

The standard format is csv file that should include the following columns:
- Test ID (optional)
- Test Type (optional)
- Aquifer name (optional)
- Aquifer type
- Aquifer properties
- Well name (optional)
- Well properties
- file name with test data.
- Test data (time, head, drawdown, etc.)

"""


class Batch_Processing:
    def __init__(self, config_obj=None):

        self.config_file = None
        if isinstance(config_obj, str):
            config_file = config_obj
            if not (os.path.exists(config_file)):
                raise FileNotFoundError(f"The file {config_file} does not exist.")
            try:
                self.config_file = config_file
                config = configparser.ConfigParser()
                config.read(config_file)
                self.config = config
            except:
                raise ValueError(f"Error reading {config_file} file")
        elif isinstance(config_obj, dict):
            self._from_dict(config_obj)
        elif isinstance(config_obj, configparser.ConfigParser):
            self.config = config_obj
        else:
            raise ValueError(
                "config_obj must be a file name, dictionary, or ConfigParser object."
            )

        self._populate_attributes()

    def _from_dict(self, config_dict):
        self.config = configparser.ConfigParser()
        self.config.read_dict(config_dict)

    def _populate_attributes(self):

        # loop through the config and set attributes
        defaults = Batch_Settings()
        default_attrs = [a for a in dir(defaults) if not a.startswith("__")]
        all_keys = []
        for section in self.config.sections():
            items = self.config[section].keys()
            all_keys = all_keys + list(items)

        for key in default_attrs:
            setattr(self, key, getattr(defaults, key))

        self._settings_keys = all_keys

        for section in self.config.sections():
            for key, value in self.config.items(section):
                value = value.strip()
                if not (value.lower() == "na"):
                    setattr(self, key, value)

    def run_batch(self):

        if not (os.path.exists(self.batch_data_file)):
            raise FileNotFoundError(
                f"The batch data file {self.batch_data_file} does not exist."
            )
        
        self.df_batch = pd.read_csv(self.batch_data_file)
        self.df_batch = self.df_batch.set_index("field").transpose()

        if os.path.exists(self.output_folder):
            shutil.rmtree(self.output_folder)
        os.makedirs(self.output_folder)
        procced_data_folder = os.path.join(self.output_folder, "processed_data")
        os.makedirs(procced_data_folder)
        df_results = []
        for irow, row in self.df_batch.iterrows():
            test_id = row.get("test_id")
            test_type = row.get("test_type")
            aquifer_name = row.get("aquifer_name")
            aquifer_type = row.get("aquifer_type")
            aquifer_thickness = float(row.get("aquifer_thickness"))
            water_table_depth = float(row.get("water_table_depth"))
            anisotropy = float(row.get("anisotropy"))
            well_name = row.get("well_name")
            well_radius = float(row.get("well_radius"))
            casing_radius = float(row.get("casing_radius"))
            screen_length = float(row.get("screen_length"))
            screen_top_depth = float(row.get("screen_top_depth"))
            test_data_file = row.get("test_data_file")
            slug_volume = float(row.get("slug_volume", pd.NA))
            test_method = row.get("solution_method")

            test_data_file = os.path.join(self.raw_data_folder, test_data_file)
            if not (os.path.exists(test_data_file)):
                raise FileNotFoundError(
                    f"The test data file {test_data_file} does not exist."
                )

            csv_file = os.path.splitext(os.path.basename(test_data_file))[0] + ".csv"
            csv_file = os.path.join(procced_data_folder, csv_file)
            insitu_to_csv(
                insitu_file=test_data_file,
                output_csv_file=csv_file,
                fig_folder=os.path.join(self.output_folder, "recovery_splits"),
                extract_recovery=True,
            )

            test_data = pd.read_csv(csv_file)
            time_col = self.time_col
            head_col = self.head_col
            if time_col not in test_data.columns or head_col not in test_data.columns:
                raise ValueError(
                    f"The test data file {test_data_file} does not contain '{time_col}' and '{head_col}' columns."
                )

            print(f"Processing {test_id}: {aquifer_name}, {well_name}, {test_type}")
            # todo: if pumping is implemented, we need to change this
            aq = Aquifer(
                name=aquifer_name,
                aquifer_type=aquifer_type,
                ground_surface_elevation=100.0,  # todo: do we need this?
                saturated_thickness=aquifer_thickness,
                water_table_depth=water_table_depth,
                anisotropy=anisotropy,
                time_unit=self.time_unit,
                length_unit=self.length_unit,
            )
            test_data[time_col] = pd.to_datetime(test_data[time_col])
            test_data[time_col] = (
                test_data[time_col] - test_data[time_col].values[0]
            ).dt.total_seconds()

            slug_well = SlugWell(
                name=well_name,
                well_radius=well_radius,
                casing_radius=casing_radius,
                screen_length=screen_length,
                screen_top_depth=screen_top_depth,
                head=test_data[head_col].values,
                time=test_data[time_col].values,
                slug_volume=slug_volume,
                is_recovery_data=True,  # rod
                length_unit=self.length_unit,
                time_unit=self.time_unit,
            )

            if test_method == "Bouwer_Rice":
                slug_test = Bouwer_Rice_1976(
                    name=test_id, aquifer=aq, slug_well=slug_well
                )
            elif test_method == "Butler":
                slug_test = Butler_2003(name=test_id, aquifer=aq, slug_well=slug_well)

            slug_test.analyze()
            plots_dir = os.path.join(self.output_folder, "fit_plots")
            if not (os.path.isdir(plots_dir)):
                os.makedirs(plots_dir)
            fig_file = os.path.join(plots_dir, test_id + ".png")
            slug_test.viz_fig.savefig(fig_file, format="png")

            df_res = pd.concat(
                [
                    pd.Series(slug_test.fitting_statistics),
                    pd.Series(slug_test.estimated_parameters),
                ]
            )
            df_res["test_name"] = slug_test.name
            df_results.append(df_res)          



        df_results = pd.concat(df_results, axis=1)
        df_results = df_results.transpose()
        df_results = df_results[
            ["test_name"] + [col for col in df_results.columns if col != "test_name"]
        ]
        self.df_results = df_results
    
    def get_well_info(self, test_name, attr = None):
        
        info = self.df_batch[self.df_batch["test_id"] == test_name][
                    attr
                ].values[0]
        return info
    
    def get_results(self, test_name = None , attr = None):
        
        if attr in self.df_results.columns:
            info = self.df_results[self.df_results["test_name"] == test_name][
                        attr
                    ].values[0]
        else:
            info = "N/A"
        return info
    def pretty_list(self, items):
        u_items = []
        for item in items:
            # find ":" and split the string
            if ":" in item:
                parts = item.split(":")
                # format parts[0] such that it is 20 characters long
                part0 = parts[0].ljust(20)
                part1 = parts[1].strip()
                u_items.append(f"{part0} : {part1}") 
        return u_items         


    def generate_html_report(self):

        test_names = self.df_batch["test_id"].unique()
        for test_name in test_names:
            components = []

            # General Info
            # -----------------
            test_date = "Date of Analysis: " + str(date.today())
            well_name = self.df_batch[self.df_batch["test_id"] == test_name]['well_name'].values[0]
            well_name = "Well Name: " + str(well_name)
            aquifer_name = "Aquifer Name: " + str(self.get_well_info(test_name, "aquifer_name")) 
            aquifer_type = "Aquifer Type: " + str(self.get_well_info(test_name, "aquifer_type"))               
            solution_method = "Solution Method: " + str(self.get_well_info(test_name, "solution_method")) 
            estimated_k = "Estimated K: " + str(self.get_results(test_name, "hydraulic_conductivity")) + " " + str(self.length_unit) + "/" + str(self.time_unit)
            estimated_s = "Estimated S: " + str(self.get_results(test_name, "S_estimated"))
            raw_list = [test_date, well_name, 
                        aquifer_name, aquifer_type,
                        solution_method, estimated_k, 
                        estimated_s]
            plist = self.pretty_list(raw_list)
            c1_gen_info = (
                "list",
                plist
                ,
                "Test Summary",
            )
            
            row1 = [c1_gen_info ]            
            components.append(row1)

            # Well info
            # -----------------
            cols = ['well_radius', 'casing_radius', 'screen_length', 'screen_top_depth', 'test_data_file', 'slug_volume']
            df_well = self.df_batch[self.df_batch["test_id"] == test_name]
            df_well = df_well[cols]           
            df_well = df_well.transpose()            
            df_well.reset_index(inplace=True)
            df_well.columns = ["Parameter", "Value"]
            # in table df_well, column Parameter, replace "_" with " " and capitalize each word
            df_well["Parameter"] = df_well["Parameter"].str.replace("_", " ").str.title()
            table1 = ("table", df_well, "Well Info")

            img_fn = self.get_well_info(test_name, "test_data_file")
            # remove extension if it exists
            if "." in img_fn:
                img_fn = img_fn.split(".")[0]
            
            img1 = os.path.join(self.output_folder, "recovery_splits", img_fn + ".png")
            row2 = [table1, ("image", img1, "Recovery Data Splits")]
            components.append(row2)

            # aquifer info
            # -----------------
            cols = ['aquifer_thickness', 'anisotropy', 'water_table_depth','ground_surface_elevation']
            df_aq = self.df_batch[self.df_batch["test_id"] == test_name]
            df_aq = df_aq[cols]
            df_aq = df_aq.transpose()
            df_aq.reset_index(inplace=True)
            df_aq.columns = ["Parameter", "Value"]
            df_aq["Parameter"] = df_aq["Parameter"].str.replace("_", " ").str.title()
            table2 = ("table", df_aq, "Aquifer Info")
            cross_sec_fig = make_schematic_plot()
            row3 = [table2, ('figure', cross_sec_fig)] 
            components.append(row3) 

            # Fitting results
            # -----------------
            df_fit = self.df_results[self.df_results["test_name"] == test_name]
            df_fit = df_fit.transpose()
            df_fit.reset_index(inplace=True)
            df_fit.columns = ["Parameter", "Value"]
            df_fit["Parameter"] = df_fit["Parameter"].str.replace("_", " ").str.title()
            table3 = ("table", df_fit, "Fitting Results")
            fit_fig = os.path.join(self.output_folder, "fit_plots", test_name + ".png")
            row4 = [table3, ('image', fit_fig, "Fit Plot")]
            components.append(row4)
            # Write report
            well_name = self.df_batch[self.df_batch["test_id"] == test_name]['well_name'].values[0]
            fn = os.path.join(self.output_folder, "{}_{}_report.html".format(well_name, test_name))
            gererate_report(components, fn)
            


def run_batch(
    batch_data=None, output_dir=None, time_unit=None, length_unit=None, config_obj=None
):
    """"""
    if config_obj is not None:

        batch_data = config_obj.get("Input Info", "batch data file")
        output_dir = config_obj.get("Output Info", "output folder")
        time_unit = config_obj.get("Input Info", "time_unit")
        length_unit = config_obj.get("Input Info", "length_unit")

    # check if df_fn is a dataframe or a file name
    if isinstance(batch_data, pd.DataFrame):
        df = batch_data  # assume it is a dataframe
    elif isinstance(batch_data, str):
        # check if the file exists and read it
        if not os.path.exists(batch_data):
            raise FileNotFoundError(f"The file {batch_data} does not exist.")
        df = pd.read_csv(batch_data)
        df = df.set_index("field").transpose()
    else:
        raise ValueError("Input must be a DataFrame or a file name.")

    # check if the output directory exists, if not create it
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # process each row in the dataframe
    df_results = []
    for index, row in df.iterrows():
        # extract the test parameters
        test_id = row.get("test_id")
        test_type = row.get("test_type")
        aquifer_name = row.get("aquifer_name")
        aquifer_type = row.get("aquifer_type")
        aquifer_thickness = float(row.get("aquifer_thickness"))
        water_table_depth = float(row.get("water_table_depth"))
        anisotropy = float(row.get("anisotropy"))
        well_name = row.get("well_name")
        well_radius = float(row.get("well_radius"))
        casing_radius = float(row.get("casing_radius"))
        screen_length = float(row.get("screen_length"))
        screen_top_depth = float(row.get("screen_top_depth"))
        test_data_file = row.get("test_data_file")
        slug_volume = float(
            row.get("slug_volume", pd.NA)
        )  # default slug volume if not provided
        test_method = row.get("method")

        # load the test data
        procced_data_folder = config_obj.get("Output Info", "processed data folder")
        if not os.path.exists(procced_data_folder):
            pass

        if not os.path.exists(test_data_file):
            raise FileNotFoundError(
                f"The test data file {test_data_file} does not exist."
            )

        test_data = pd.read_csv(test_data_file)
        # check if the required columns are present
        if "Time" not in test_data.columns or "Head" not in test_data.columns:
            raise ValueError(
                f"The test data file {test_data_file} must contain 'Time' and 'Head' columns."
            )

        print(f"Processing {test_id}: {aquifer_name}, {well_name}, {test_type}")

        # todo:
        # here you would call the appropriate analysis function based on the test type
        # e.g., if test_type == 'slug': analyze_slug_test(...)

        aq = Aquifer(
            name=aquifer_name,
            aquifer_type=aquifer_type,
            ground_surface_elevation=100.0,  # todo: do we need this?
            saturated_thickness=aquifer_thickness,
            water_table_depth=water_table_depth,
            anisotropy=anisotropy,
            time_unit=time_unit,
            length_unit=length_unit,
        )

        test_data["Time"] = pd.to_datetime(test_data["Time"])
        test_data["Time"] = (
            test_data["Time"] - test_data["Time"].values[0]
        ).dt.total_seconds()

        slug_well = SlugWell(
            name=well_name,
            well_radius=well_radius,
            casing_radius=casing_radius,
            screen_length=screen_length,
            screen_top_depth=screen_top_depth,
            head=test_data["Head"].values,
            time=test_data["Time"].values,
            slug_volume=slug_volume,
            is_recovery_data=True,  # rod
            length_unit=length_unit,
            time_unit=time_unit,
        )

        if test_method == "Bouwer_Rice":
            slug_test = Bouwer_Rice_1976(name=test_id, aquifer=aq, slug_well=slug_well)
        elif test_method == "Butler":
            slug_test = Butler_2003(name=test_id, aquifer=aq, slug_well=slug_well)

        slug_test.analyze()
        plots_dir = os.path.join(output_dir, "fit_plots")
        if not (os.path.isdir(plots_dir)):
            os.makedirs(plots_dir)
        fig_file = os.path.join(plots_dir, test_id + ".png")
        slug_test.viz_fig.savefig(fig_file, format="png")

        df_res = pd.concat(
            [
                pd.Series(slug_test.fitting_statistics),
                pd.Series(slug_test.estimated_parameters),
            ]
        )
        df_res["test_name"] = slug_test.name
        df_results.append(df_res)

    df_results = pd.concat(df_results, axis=1)
    df_results = df_results.transpose()
    df_results = df_results[
        ["test_name"] + [col for col in df_results.columns if col != "test_name"]
    ]
    return df_results


def run_batch_init(config_file=None):
    # check if file exist
    if not (os.path.exists(config_file)):
        raise FileNotFoundError(f"The file {config_file} does not exist.")

    try:
        config_obj = setting.read_config(config_file)
    except:
        raise ValueError(f"Error reading {config_file} file")

    run_batch(config_file=config_file)
