# \\socal-dc\Jobs\6151-7000\6173 (WRD) Regional Brackish Water Reclamation Program – Phase 1\4_Data\6173_Slug Test XD Data
# \\socal-dc\Jobs\6151-7000\6173 (WRD) Regional Brackish Water Reclamation Program – Phase 1\4_Data\AQTESOLV\well info
# \\socal-dc\Jobs\6151-7000\6173 (WRD) Regional Brackish Water Reclamation Program – Phase 1\4_Data\Pneumatic Slug Test Data\PM-07\PM-07-01

import os
import shutil
import pandas as pd
import numpy as np
from pyAqTest import run_batch

# ====================================
# generate synthetic data for testing
# ====================================
number_of_tests = 10
root = r"C:\workspace\projects\pump_tests\pyAqTest\tests\batch_test_data"

# create test data.
fn = r"C:\workspace\projects\pump_tests\pyAqTest\tests\datasets\Butler_1.txt"
df_tr = pd.read_csv(fn, sep="\s+")
del df_tr["NormalizedHead"]

test_data_folder = os.path.join(root, "test_data")
if os.path.exists(test_data_folder):
    shutil.rmtree(test_data_folder)
os.makedirs(test_data_folder)

for i in range(number_of_tests):
    test_id = f"test_{i+1}"
    test_data_file = os.path.join(test_data_folder, f"{test_id}.csv")
    # make the data realistic by adding pre-test static level
    df = df_tr.copy()
    t = np.arange(0, 10, 0.1)
    h = len(t) * [0.0]
    df_static = pd.DataFrame(columns=df.columns)
    df_static["Time"] = t
    df_static["Head"] = h
    df["Time"] = df["Time"] + t[-1]
    df = pd.concat([df_static, df])
    rng = np.random.default_rng(seed=42)
    noise = rng.normal(loc=0.0, scale=0.0, size=len(df))
    df["Head"] = 1.0 + df["Head"] + noise
    df.to_csv(test_data_file, index=False)


# prepare synthetic test data
df_batch = pd.DataFrame(
    columns=[
        "test_id",
        "test_type",
        "aquifer_name",
        "aquifer_type",
        "aquifer_thickness",
        "anisotropy",
        "water_table_depth",
        "well_name",
        "well_radius",
        "casing_radius",
        "screen_length",
        "screen_top_depth",
        "test_data_file",
    ]
)

df_batch["test_id"] = [f"test_{i+1}" for i in range(number_of_tests)]
df_batch["test_type"] = "slug"
df_batch["aquifer_name"] = ["Aquifer_1" for i in range(number_of_tests)]
df_batch["aquifer_type"] = "unconfined"
df_batch["ground_surface_elevation"] = 100.0  # in meters
df_batch["aquifer_thickness"] = 50.6
df_batch["anisotropy"] = 1.0
df_batch["water_table_depth"] = 10.0
df_batch["well_name"] = [f"Well_{i+1}" for i in range(number_of_tests)]
df_batch["well_radius"] = 0.125
df_batch["casing_radius"] = 0.064
df_batch["screen_length"] = 1.52
df_batch["screen_top_depth"] = 28.54
df_batch["test_data_file"] = [
    os.path.join(test_data_folder, f"test_{i+1}.csv") for i in range(number_of_tests)
]
df_batch["slug_volume"] = pd.NA  # default slug volume if not provided

# save the batch data to a csv file
batch_file = os.path.join(root, "batch_data.csv")
df_batch.to_csv(batch_file, index=False)

output_dir = os.path.join(root, "output")
df_results = run_batch(batch_data=batch_file, output_dir=output_dir)
