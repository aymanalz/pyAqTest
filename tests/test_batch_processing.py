import configparser
import pytest
from pyAqTest import Batch_Processing


@pytest.fixture
def minimal_config_dict(tmp_path):
    # Create a minimal config dict with required sections and keys
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()
    return {
        "Input Info": {
            "raw_data_folder": str(input_folder),
            "file_type": "csv",
            "length_unit": "m",
            "time_unit": "s",
            "batch_data_file": "batch.csv",
        },
        "Output Info": {"output_folder": str(output_folder)},
    }


def test_init_with_dict(minimal_config_dict):
    bp = Batch_Processing(config_obj=minimal_config_dict)
    assert bp.raw_data_folder == minimal_config_dict["Input Info"]["raw_data_folder"]
    assert bp.file_type == "csv"
    assert bp.length_unit == "m"
    assert bp.time_unit == "s"
    assert bp.output_folder == minimal_config_dict["Output Info"]["output_folder"]
    assert bp.batch_data_file == "batch.csv"


def test_init_with_configparser(minimal_config_dict):
    config = configparser.ConfigParser()
    config.read_dict(minimal_config_dict)
    bp = Batch_Processing(config_obj=config)
    assert bp.raw_data_folder == minimal_config_dict["Input Info"]["raw_data_folder"]


def test_init_with_missing_file(tmp_path):
    missing_file = tmp_path / "missing.ini"
    with pytest.raises(FileNotFoundError):
        Batch_Processing(config_obj=str(missing_file))


def test_init_with_invalid_type():
    with pytest.raises(ValueError):
        Batch_Processing(config_obj=123)


def test_from_dict_sets_config(minimal_config_dict):
    bp = Batch_Processing(config_obj=minimal_config_dict)
    assert isinstance(bp.config, configparser.ConfigParser)
