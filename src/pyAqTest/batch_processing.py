import os
import pandas as pd
from pyAqTest import Aquifer, SlugWell, Bouwer_Rice_1976
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

def run_batch(batch_data, output_dir):
    # check if df_fn is a dataframe or a file name
    if isinstance(batch_data, pd.DataFrame):
        df = batch_data  # assume it is a dataframe
    elif isinstance(batch_data, str):
        # check if the file exists and read it
        if not os.path.exists(batch_data):
            raise FileNotFoundError(f"The file {batch_data} does not exist.")
        df = pd.read_csv(batch_data)
    else:
        raise ValueError("Input must be a DataFrame or a file name.")

    # check if the output directory exists, if not create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # process each row in the dataframe
    df_results = []
    for index, row in df.iterrows():
        # extract the test parameters
        test_id = row.get('test_id')
        test_type = row.get('test_type')
        aquifer_name = row.get('aquifer_name')
        aquifer_type = row.get('aquifer_type')
        aquifer_thickness = float(row.get('aquifer_thickness'))
        water_table_depth = float(row.get('water_table_depth'))
        anisotropy = float(row.get('anisotropy'))
        well_name = row.get('well_name')
        well_radius = float(row.get('well_radius'))
        casing_radius = float(row.get('casing_radius'))
        screen_length = float(row.get('screen_length'))
        screen_top_depth = float(row.get('screen_top_depth'))
        test_data_file = row.get('test_data_file')
        slug_volume = float(row.get('slug_volume', pd.NA))  # default slug volume if not provided

        # load the test data
        if not os.path.exists(test_data_file):
            raise FileNotFoundError(f"The test data file {test_data_file} does not exist.")

        test_data = pd.read_csv(test_data_file)
        # check if the required columns are present
        if 'Time' not in test_data.columns or 'Head' not in test_data.columns:
            raise ValueError(f"The test data file {test_data_file} must contain 'Time' and 'Head' columns.")


        print(f"Processing {test_id}: {aquifer_name}, {well_name}, {test_type}")

        # todo:
        # here you would call the appropriate analysis function based on the test type
        # e.g., if test_type == 'slug': analyze_slug_test(...)



        aq = Aquifer(
            name= aquifer_name,
            aquifer_type= aquifer_type,
            ground_surface_elevation=100.0, # todo: do we need this?
            saturated_thickness=aquifer_thickness,
            water_table_depth=water_table_depth,
            anisotropy= anisotropy,
        )

        test_data['Time'] = pd.to_datetime(test_data['Time'])
        test_data['Time'] = (test_data['Time'] - test_data['Time'].values[0]).dt.total_seconds()

        slug_well = SlugWell(
            name=well_name,
            well_radius=well_radius,
            casing_radius=casing_radius,
            screen_length=screen_length,
            screen_top_depth= screen_top_depth,
            head = test_data['Head'].values,
            time = test_data['Time'].values,
            slug_volume= slug_volume,
            is_recovery_data=True, # rod
        )

        slug_test = Bouwer_Rice_1976(
            name=test_id,
            aquifer=aq,
            slug_well=slug_well
        )

        slug_test.analyze()
        plots_dir = os.path.join(output_dir, 'fit_plots')
        if not(os.path.isdir(plots_dir)):
            os.makedirs(plots_dir)
        fig_file = os.path.join(plots_dir, test_id+".png")
        slug_test.viz_fig.savefig(fig_file, format="png")

        df_res = pd.concat([pd.Series(slug_test.fitting_statistics),
                              pd.Series(slug_test.estimated_parameters)]
                             )
        df_res['test_name'] = slug_test.name
        df_results.append(df_res)

    df_results = pd.concat(df_results, axis=1)
    df_results = df_results.transpose()
    df_results = df_results[['test_name'] + [col for col in df_results.columns if col != 'test_name']]
    return df_results

