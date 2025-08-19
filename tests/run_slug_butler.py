import pandas as pd
import numpy as np
from pyAqTest import Aquifer, SlugWell, Butler_2003

fn = r"C:\workspace\projects\pump_tests\pyAqTest\tests\datasets\butler_method.csv"
df = pd.read_csv(fn)


"""
Todo: We assume that the first time is 0 and the first head is H0
"""

t0 = 55932.5
static_level = 0.4463
df["Time"] = df["Time"] - t0
df["Head"] = df["Head"] - static_level
H0 = -0.0539
first_row = {"Time": 0, "Head": H0}
df = pd.concat([pd.DataFrame([first_row]), df], ignore_index=True)


aq = Aquifer(
    name="GEMS",
    aquifer_type="unconfined",
    ground_surface_elevation=100.0,
    saturated_thickness=10.67,
    water_table_depth=19.8 - 5 - 0.229,
    anisotropy=1.0,
    length_unit="m",
    time_unit="s",
)

print(aq)

slug_well = SlugWell(
    name="well_1",
    well_radius=0.01667,
    casing_radius=0.01883,
    screen_length=0.2286,
    screen_top_depth=19.8 - 0.229,
    head=df["Head"].values,
    time=df["Time"].values,
    is_recovery_data=True,
    length_unit="m",
    time_unit="s",
)
print(slug_well)

slug_test = Butler_2003(name="slug_test_1", aquifer=aq, slug_well=slug_well)

slug_test.analyze()
slug_test.print_estimated_parameters()

cc = 1