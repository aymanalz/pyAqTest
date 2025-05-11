import pandas as pd
import numpy as np
from pyAqTest import Bouwer_Rice_1976, Aquifer, SlugWell

fn = r"C:\workspace\projects\pump_tests\pyAqTest\tests\datasets\Butler_1.txt"
df = pd.read_csv(fn, sep='\s+')
del(df['NormalizedHead'])

# make the data realistic by adding pre-test static level
t = np.arange(0,10,0.1)
h = len(t)*[0.0]
df_static = pd.DataFrame(columns=df.columns)
df_static['Time'] = t
df_static['Head'] = h
df['Time'] =  df['Time']  + t[-1]
df = pd.concat([df_static, df])
#noise = 0.06 * np.random.randn(len(df))
rng = np.random.default_rng(seed=42)
noise = rng.normal(loc=0.0, scale= 0.0, size=len(df))
df['Head'] = 1.0 + df['Head'] + noise


aq = Aquifer(
    name="A1",
    aquifer_type="unconfined",
    ground_surface_elevation=100.0,
    saturated_thickness=50.6,
    water_table_depth=10.0,
    anisotropy=1.0,
)

print(aq)

slug_well = SlugWell(
    name="well_1",
    well_radius=0.125,
    casing_radius=0.064,
    screen_length=1.52,
    screen_top_depth= 28.54,
    head = df['Head'].values,
    time = df['Time'].values,
    slug_volume=0.1
)
print(slug_well)

slug_test = Bouwer_Rice_1976(
    name="slug_test_1",
    aquifer=aq,
    slug_well=slug_well   
)

slug_test.analyze()
slug_test.print_estimated_parameters()






