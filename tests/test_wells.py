import pytest
from pyAqTest.wells import Well
from pyAqTest.wells import PumpingWell
import pandas as pd

def test_well_initialization():
    well = Well(
        name="W1",
        well_type="pumping",
        location=(10.0, 20.0),
        ground_surface_elevation=100.0,
        casing_radius=0.1,
        well_radius=0.15,
        screen_length=10.0,
        screen_top_depth=5.0,
    )
    assert well.well_id == "W1"
    assert well.well_type == "pumping"
    assert well.location == (10.0, 20.0)
    assert well.ground_surface_elevation == 100.0
    assert well.casing_radius == 0.1
    assert well.well_radius == 0.15
    assert well.screen_length == 10.0
    assert well.screen_top_depth == 5.0

def test_validate_positive_values():
    well = Well(
        name="W2",
        well_type="observation",
        location=(15.0, 25.0),
        ground_surface_elevation=120.0,
        casing_radius=0.1,
        well_radius=0.15,
        screen_length=10.0,
        screen_top_depth=5.0,
    )
    assert well.validate_positive_values() is None

    well.casing_radius = -0.1
    assert well.validate_positive_values() == "Error: Casing radius must be positive."

def test_validate_casing_radius():
    well = Well(
        name="W3",
        well_type="slug",
        location=(5.0, 10.0),
        ground_surface_elevation=80.0,
        casing_radius=0.1,
        well_radius=0.15,
        screen_length=10.0,
        screen_top_depth=5.0,
    )
    assert well.validate_casing_radius() is None

    well.casing_radius = 0.2
    assert well.validate_casing_radius() == (
        "Error: Casing radius (0.200 m) must be less than well radius (0.150 m)."
    )

def test_validate_well_type():
    well = Well(
        name="W4",
        well_type="pumping",
        location=(0.0, 0.0),
        ground_surface_elevation=50.0,
        casing_radius=0.1,
        well_radius=0.15,
        screen_length=10.0,
        screen_top_depth=5.0,
    )
    assert well.validate_well_type() is None

    well.well_type = "invalid_type"
    assert well.validate_well_type() == (
        "Error: Invalid well type 'invalid_type'. Valid types are: pumping, slug, observation."
    )

def test_set_default_values():
    well = Well(
        name="W5",
        well_type="observation",
        location=None,
        ground_surface_elevation=None,
        casing_radius=None,
        well_radius=None,
        screen_length=None,
        screen_top_depth=None,
    )
    well.set_default_values()
    assert well.location == (0.0, 0.0)
    assert well.ground_surface_elevation == 0.0
    assert well.casing_radius == 0.1
    assert well.well_radius == 0.15
    assert well.screen_length == 10.0
    assert well.screen_top_depth == 5.0
    
def test_pumping_well_initialization_with_float_rate():
    well = PumpingWell(
        well_id="PW1",
        well_type="pumping",
        location=(10.0, 20.0),
        ground_surface_elevation=100.0,
        casing_radius=0.1,
        well_radius=0.15,
        screen_length=10.0,
        screen_top_depth=5.0,
        pumping_rate=5.0,
        pumping_period=10.0,
    )
    assert well.well_id == "PW1"
    assert well.well_type == "pumping"
    assert well.location == (10.0, 20.0)
    assert well.ground_surface_elevation == 100.0
    assert well.casing_radius == 0.1
    assert well.well_radius == 0.15
    assert well.screen_length == 10.0
    assert well.screen_top_depth == 5.0
    assert isinstance(well.pumping_rate, pd.DataFrame)
    assert list(well.pumping_rate.columns) == ["time", "rate"]
    assert well.pumping_rate.iloc[0]["rate"] == 5.0

def test_pumping_well_initialization_with_dataframe_rate():
    pumping_rate_df = pd.DataFrame({"time": [0, 10], "rate": [5.0, 5.0]})
    well = PumpingWell(
        well_id="PW2",
        well_type="pumping",
        location=(15.0, 25.0),
        ground_surface_elevation=120.0,
        casing_radius=0.1,
        well_radius=0.15,
        screen_length=10.0,
        screen_top_depth=5.0,
        pumping_rate=pumping_rate_df,
        pumping_period=None,
    )
    assert well.well_id == "PW2"
    assert well.well_type == "pumping"
    assert well.location == (15.0, 25.0)
    assert well.ground_surface_elevation == 120.0
    assert well.casing_radius == 0.1
    assert well.well_radius == 0.15
    assert well.screen_length == 10.0
    assert well.screen_top_depth == 5.0
    assert well.pumping_rate.equals(pumping_rate_df)

def test_pumping_well_invalid_pumping_rate_type():
    with pytest.raises(ValueError, match="Pumping rate must be a float or a pandas DataFrame."):
        PumpingWell(
            well_id="PW3",
            well_type="pumping",
            location=(20.0, 30.0),
            ground_surface_elevation=150.0,
            casing_radius=0.1,
            well_radius=0.15,
            screen_length=10.0,
            screen_top_depth=5.0,
            pumping_rate="invalid_rate",
            pumping_period=None,
        )

def test_pumping_well_missing_pumping_period_with_float_rate():
    with pytest.raises(ValueError, match="Error: Pumping period must be provided if pumping rate is a float."):
        PumpingWell(
            well_id="PW4",
            well_type="pumping",
            location=(25.0, 35.0),
            ground_surface_elevation=200.0,
            casing_radius=0.1,
            well_radius=0.15,
            screen_length=10.0,
            screen_top_depth=5.0,
            pumping_rate=5.0,
            pumping_period=None,
        )

def test_pumping_well_invalid_dataframe_columns():
    invalid_df = pd.DataFrame({"invalid_col": [0, 10], "rate": [5.0, 5.0]})
    with pytest.raises(ValueError, match="Error: Pumping rate DataFrame must contain a 'time' column."):
        PumpingWell(
            well_id="PW5",
            well_type="pumping",
            location=(30.0, 40.0),
            ground_surface_elevation=250.0,
            casing_radius=0.1,
            well_radius=0.15,
            screen_length=10.0,
            screen_top_depth=5.0,
            pumping_rate=invalid_df,
            pumping_period=None,
        )

def test_pumping_well_invalid_dataframe_rate_column():
    invalid_df = pd.DataFrame({"time": [0, 10], "invalid_col": [5.0, 5.0]})
    with pytest.raises(ValueError, match="Error: Pumping rate DataFrame must contain a 'rate' column."):
        PumpingWell(
            well_id="PW6",
            well_type="pumping",
            location=(35.0, 45.0),
            ground_surface_elevation=300.0,
            casing_radius=0.1,
            well_radius=0.15,
            screen_length=10.0,
            screen_top_depth=5.0,
            pumping_rate=invalid_df,
            pumping_period=None,
        )
