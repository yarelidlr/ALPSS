import json
import os
import pytest
from alpss.commands import _flatten_config, load_json_config


# --- _flatten_config ---

def test_flatten_merges_sections():
    config = {
        "io": {"filepath": "a.csv", "save_data": "yes"},
        "material": {"density": 8960, "C0": 3950},
    }
    flat = _flatten_config(config)
    assert flat["filepath"] == "a.csv"
    assert flat["density"] == 8960
    assert flat["C0"] == 3950


def test_flatten_raises_on_flat_config():
    with pytest.raises(ValueError, match="nested sections"):
        _flatten_config({"filepath": "a.csv", "density": 8960})


def test_flatten_raises_on_unknown_section():
    with pytest.raises(ValueError, match="Unknown config sections"):
        _flatten_config({"io": {"filepath": "a.csv"}, "typo_section": {"x": 1}})


def test_flatten_raises_on_key_collision():
    with pytest.raises(ValueError, match="collision"):
        _flatten_config({
            "io": {"density": 1.0},      # density doesn't belong here but shouldn't matter
            "material": {"density": 8960},
        })


def test_flatten_single_section():
    flat = _flatten_config({"io": {"filepath": "a.csv"}})
    assert flat == {"filepath": "a.csv"}


def test_flatten_all_valid_sections():
    config = {s: {"key_" + s: 1} for s in [
        "io", "stft", "start_time", "carrier", "velocity",
        "material", "spall", "hel", "uncertainty", "plotting",
    ]}
    flat = _flatten_config(config)
    assert len(flat) == 10
    assert "key_io" in flat
    assert "key_plotting" in flat


# --- load_json_config ---

def test_load_json_config_nested_dict():
    d = {"io": {"filepath": "a.csv"}, "material": {"density": 8960}}
    flat = load_json_config(d)
    assert flat["filepath"] == "a.csv"
    assert flat["density"] == 8960


def test_load_json_config_flat_dict_raises():
    with pytest.raises(ValueError, match="nested sections"):
        load_json_config({"filepath": "a.csv", "density": 8960})


def test_load_json_config_from_file(tmp_path):
    config = {"io": {"filepath": "a.csv"}, "material": {"density": 8960}}
    f = tmp_path / "config.json"
    f.write_text(json.dumps(config))
    flat = load_json_config(str(f))
    assert flat["filepath"] == "a.csv"
    assert flat["density"] == 8960


def test_load_json_config_flat_file_raises(tmp_path):
    config = {"filepath": "a.csv", "density": 8960}
    f = tmp_path / "config.json"
    f.write_text(json.dumps(config))
    with pytest.raises(ValueError, match="nested sections"):
        load_json_config(str(f))


def test_load_json_config_invalid_path_raises():
    with pytest.raises(ValueError, match="Invalid config input"):
        load_json_config("/nonexistent/path/config.json")


def test_load_json_config_unknown_section_raises(tmp_path):
    config = {"io": {"filepath": "a.csv"}, "bad_section": {"x": 1}}
    f = tmp_path / "config.json"
    f.write_text(json.dumps(config))
    with pytest.raises(ValueError, match="Unknown config sections"):
        load_json_config(str(f))
