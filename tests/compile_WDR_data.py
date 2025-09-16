import os
import re
import pandas as pd

ws = r"C:\workspace\projects\pump_tests\WRD_Slug_Data"
input_sheet_file = os.path.join(ws, "Input Sheet.xlsx")
well_par_file = os.path.join(ws, "2025.09.15 - Well Parameter Database.xlsx")
batch_template_file = r"C:\workspace\projects\pump_tests\gw_pump_test\batch_test_infoMax.csv"
data_folder = r"C:\workspace\projects\pump_tests\WRD_Slug_Data"
folders_of_data = [r"2025.06.25_PSTdata", r"2025.07.01_PSTdata",
 r"2025.07.16_PSTdata", r"2025.08.18_PSTdata", "2025.09.11_PSTdata"]

col_names_mapping = {
    "test_id": "Test ID",
    "Test Date": "Test Date",
    "test_type": "Test Type", 
    "solution_method": "Butler", # Bouwer_Rice
    "aquifer_name": "Aquifer",
    "aquifer_type": "Aquifer Type (confined, semiconfined, unconfined)",
    "aquifer_thickness": "Aquifer Saturated Thickness (ft)",
    "water_table_depth": "DTW (ft bgs)",
    "anisotropy": 0.1,
    "well_name": "Well Name_y",
    "well_radius": "Casing Radius (ft)",
    "casing_radius": "Casing Radius (ft)",
    "screen_length": "screen_length",
    "screen_top_depth": "Bottom of Perf",
    "test_data_file": "find it",
    "slug_volume": "Slug Volume",    
    "ground_surface_elevation": "RPE",
    "other_notes": "Other Notes"
}
wellname_col = "Casing ID"
well_df = pd.read_excel(well_par_file)
well_df = well_df[~well_df[wellname_col].isna()]
print("Number of wells: ", len(well_df))

input_df = pd.read_excel(input_sheet_file, sheet_name="PST Data Tracking")

combined_df = input_df.merge(well_df, left_on="Casing ID", right_on=wellname_col, how="left")
combined_df['screen_length'] = combined_df['Bottom of Perf'] - combined_df['Top of Perf'] 
combined_df['test_data_file'] = combined_df['Borehole Diameter (inches)']/12.0

cols = list(col_names_mapping.keys())
solution_method =  "Bouwer_Rice"
aquifer_type = "confined"
for col in cols:
    col_name = col_names_mapping[col]
    if not (col_name in combined_df.columns):
        if col in ["solution_method"]:
            combined_df[col] = solution_method
        elif col in ["test_type"]:
            combined_df[col] = "slug"
        elif col in ["aquifer_type"]:
            combined_df[col] = aquifer_type
        elif col in ["test_data_file", 'other_notes', 'slug_volume']:
            combined_df[col] = None
        elif col in {"anisotropy"}:
            combined_df[col] = 0.1        
        continue
    if col in ["test_data_file", "other_notes"]:
        combined_df[col] = None
        continue
    combined_df[col] = combined_df[col_name]


def extract_info(filename: str):
    if filename in ['VuSitu_Log_2025-06-26_09-20-25_LB2_5_L2_5_T1_Wet.html']:
        cc = 1
    date_match = re.search(r"VuSitu_Log_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})", filename)
    date_time = date_match.group(1) if date_match else None
    if "Wet" in filename:
        well_part = filename.split("_Wet")[0].split(date_time + "_")[-1]
    elif "WET" in filename:
        well_part = filename.split("_WET")[0].split(date_time + "_")[-1]
    nm2, tt = well_part.split("_T")
    len_nm2 = len(nm2)-1
    if len_nm2%2==0:
        hlf = int(len_nm2/2)
        nm_ = nm2[:hlf]
    else:
        print(f"File {filename} has an odd number of characters in the well name")
        return None
    well_name = nm_ + "_T" + str(tt)
    return  well_name

# get data files
test_data_files = {}
capNM = [v.upper() for v in combined_df['test_id'].values]
files_without_test_id = []
for folder in folders_of_data:
    current_folder = os.path.join(data_folder, folder)
    insitu_files = os.listdir(current_folder)
    for file in insitu_files:
        nm = extract_info(file)
        if nm.upper() in capNM:
            test_data_files[nm] = os.path.join(current_folder, file)
            combined_df.loc[combined_df['test_id'] == nm, 'test_data_file'] = os.path.join(current_folder, file)
        else:
            print(f"File {file} does not have a test id")
            files_without_test_id.append([nm, file])
            
combined_df.to_csv(os.path.join(ws, "wrd_batch_data.csv"), index=False)
cols = cols
dff = combined_df[cols]
dff = dff.dropna(subset=['test_data_file', 'well_radius'])
dff = dff.transpose()
dff.index.name = "field"
dff.reset_index(inplace=True)
dff.to_csv(os.path.join(ws, "wrd_batch_data_clean.csv"), index=False)
## data cleaning
for irow, row in combined_df.iterrows():
    test_id = row['Test ID']

            


vv= 1
