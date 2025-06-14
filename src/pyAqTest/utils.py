import os
import shutil
import re

import pandas as pd
import numpy as np
from typing import List, Dict, Any
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from tqdm import tqdm


from pyAqTest import readers


def extract_wet_period(df, window_size=20, debug={"flg": False}):

    valid = False
    for col in df.columns:
        if "Time" in col:
            time = df[col].values
            break

    for col in df.columns:
        if "Depth" in col:
            head = df[col].values
            valid = True
            break
    if not valid:
        return None

    max_change = []
    max_i = []
    signed_max_diff = []

    for i in range(window_size, len(head) - window_size):
        window_before = head[i - window_size : i]
        window_after = head[i : i + window_size]
        mean_before = np.mean(window_before)
        mean_after = np.mean(window_after)
        diff = abs(mean_after - mean_before)

        max_change.append(diff)
        max_i.append(i)
        signed_max_diff.append(mean_after - mean_before)
    df_info = pd.DataFrame(columns=["max_change", "max_i", "signed_max_diff"])
    df_info["max_change"] = max_change
    df_info["max_i"] = max_i
    df_info["signed_max_diff"] = signed_max_diff

    mask = df_info["signed_max_diff"] < 0
    dry_periods = df_info[mask].copy()
    dry_periods.sort_values(by=["max_change"], ascending=False, inplace=True)
    i_min = dry_periods["max_i"].values[0]
    j = np.argmin(head[i_min - window_size : i_min + window_size])
    static_level = np.mean(head[j - window_size : j - 1])
    recovery_start = i_min + j
    recovery_head = head[recovery_start:]
    recovery_time = time[recovery_start:]

    # debug
    if debug["flg"]:
        plot_folder = debug["plot_folder"]
        fn = debug["file_name"]
        fn = os.path.splitext(fn)[0] + ".png"
        if not os.path.exists(plot_folder):
            os.makedirs(plot_folder)

        plt.figure()
        plt.title("Dry/Wet Periods")
        plt.xlabel("Time")
        plt.ylabel("Head")
        plt.plot(time, head)
        plt.plot(time[recovery_start:], recovery_head)
        plt.legend(["All test data", "Recovery Period"])

        plt.savefig(
            os.path.join(
                plot_folder,
                fn,
            )
        )
        plt.close()

    return recovery_head, recovery_time, static_level


def in_situ_tests_to_csv(
    input_folder: str,
    output_folder: str,
    skip_word: str,
    file_extension: str,
    slug_data_folder: str,
) -> None:
    """
    Convert a set of in-situ tests data to CSV format that is suitable for batch processing.
    The following are done by this function:
    1. Read the input folder and get all the files in it. Skip any file that contains the
       skip_word in its name.
    2. For each file, read the data, extract test_data (time, head)
    """

    # 1) Get the files with slug data
    slug_files = os.listdir(input_folder)
    slug_files = [f for f in slug_files if skip_word not in f]
    slug_files = [f for f in slug_files if f.endswith(file_extension)]

    # 2) Read the data from each file
    for slug_file in tqdm(slug_files, desc="Processing files"):

        file_path = os.path.join(input_folder, slug_file)
        df = readers.extract_table_from_insitu_html_file(file_path)

        try:
            recovery_head, recovery_time, static_level = extract_wet_period(
                df,
                window_size=10,
                debug={
                    "flg": True,
                    "plot_folder": os.path.join(output_folder, "recovery_splits"),
                    "file_name": slug_file,
                },
            )

            df_ = pd.DataFrame(
                {
                    "Time": recovery_time,
                    "Head": recovery_head,
                    "Static Level": static_level,
                }
            )

            # Save the data to CSV
            fn = os.path.splitext(slug_file)[0] + ".csv"
            fn = os.path.join(slug_data_folder, fn)
            df_.to_csv(
                fn,
                index=False,
            )
        except:
            print(f"  Error processing file: {slug_file} ")
            continue

def extract_well_name(text):
    if "WET" in text:
        match = re.search(r'Log_(.*?)_WET_', text)
    elif "wet" in text:
        match = re.search(r'Log_(.*?)-wet', text)
    else:
        return None

    return match.group(1) if match else None

def rename_htm_files(input_folder, output_folder,
                     file_extension, skip_word
                     ):
    # 1) Get the files with slug data
    slug_files = os.listdir(input_folder)
    slug_files = [f for f in slug_files if skip_word not in f]
    slug_files = [f for f in slug_files if f.endswith(file_extension)]

    for file in slug_files:
        if "WET" in file or "wet" in file:
            well_name = extract_well_name(file)
            fn1 = os.path.join(input_folder, file)
            fn2 = os.path.join(output_folder, well_name+".htm")
            shutil.copy(fn1, fn2)
        else:
            print(f" Skipped -- {file}")






if __name__ == "__main__":
    # Example usage
    debug1 = False
    skip_word = "DRY"
    input_folder = r"C:\workspace\projects\pump_tests\6173_Slug Test XD Data"
    if debug1:

        output_folder = r"C:\workspace\projects\pump_tests\gw_pump_test"
        output_csv_file = r"C:\workspace\projects\pump_tests\gw_pump_test\slug_test.csv"

        in_situ_tests_to_csv(
            input_folder=input_folder,
            output_folder=output_folder,
            skip_word=skip_word,
            file_extension="htm",
            slug_data_folder=output_folder,
        )

    output_folder = r"C:\workspace\projects\pump_tests\gw_pump_test\insitu_csv"
    rename_htm_files(
        input_folder=input_folder,
        output_folder=output_folder,
        skip_word=skip_word,
        file_extension="htm"
    )
