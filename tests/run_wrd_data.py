import os
import shutil

import pandas as pd
import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import pyAqTest
import re

# This is the folder that has the in-situ html files
slug_test_html_data_folder = r"C:\workspace\projects\pump_tests\6173_Slug Test XD Data"
file_to_include_ext = "htm"
key_word_to_include = "_WET_"

# output_folder
output_dir = r"C:\workspace\projects\pump_tests\pyAqTest\tests\wrd_dataset"
if 0:
    slug_data_dir = os.path.join(output_dir, "slug_test_data")
    if os.path.isdir(slug_data_dir):
        shutil.rmtree(slug_data_dir)
    os.makedirs(slug_data_dir)

    def extract_well_name(text):
        match = re.search(r"Log_(.*?)_WET_", text)
        return match.group(1) if match else None

    html_files = os.listdir(slug_test_html_data_folder)
    for file in html_files:
        if not (file.lower().endswith(".htm")):
            continue

        if not (key_word_to_include in file):
            continue

        well_name = extract_well_name(file)
        fn = os.path.join(slug_test_html_data_folder, file)
        df = pyAqTest.readers.extract_table_from_insitu_html_file(fn)

        time_col = [col for col in df.columns if "Date Time" in col]
        depth_col = [col for col in df.columns if "Depth" in col]
        csv_fn = os.path.join(slug_data_dir, well_name + ".csv")
        df = df[[time_col[0], depth_col[0]]]
        df.rename(columns={time_col[0]: "time", depth_col[0]: "head"}, inplace=True)
        df.to_csv(csv_fn, index=False)
