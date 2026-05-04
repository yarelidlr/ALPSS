import copy
import logging
import pytest
from alpss.utils.config import flatten_config
from alpss.validation import validate_inputs


@pytest.fixture
def flat_inputs(valid_inputs):
    return flatten_config(valid_inputs)


# --- _ALWAYS_REQUIRED ---


def test_valid_inputs_passes(flat_inputs):
    validate_inputs(flat_inputs)


def test_missing_always_required_raises(flat_inputs):
    inputs = copy.deepcopy(flat_inputs)
    del inputs["filepath"]
    with pytest.raises(ValueError, match="Missing required config keys"):
        validate_inputs(inputs)


@pytest.mark.parametrize(
    "key",
    [
        "out_files_dir",
        "sample_rate",
        "lam",
        "density",
        "uncert_mult",
        "hel_start_time_ns",
        "minimum_HEL_velocity_expected",
    ],
)
def test_missing_required_key_raises(flat_inputs, key):
    inputs = copy.deepcopy(flat_inputs)
    del inputs[key]
    with pytest.raises(ValueError, match="Missing required config keys"):
        validate_inputs(inputs)


# --- _REQUIRED_BY_MODE: start_time_user ---


@pytest.mark.parametrize("missing_key", ["carrier_band_time"])
def test_otsu_requires_key(flat_inputs, missing_key):
    inputs = copy.deepcopy(flat_inputs)
    inputs["start_time_user"] = "otsu"
    del inputs[missing_key]
    with pytest.raises(ValueError, match="start_time_user='otsu'"):
        validate_inputs(inputs)


@pytest.mark.parametrize("missing_key", ["iq_threshold_factor"])
def test_iq_requires_key(flat_inputs, missing_key):
    inputs = copy.deepcopy(flat_inputs)
    inputs["start_time_user"] = "iq"
    del inputs[missing_key]
    with pytest.raises(ValueError, match="start_time_user='iq'"):
        validate_inputs(inputs)


@pytest.mark.parametrize(
    "missing_key", ["carrier_band_time", "cusum_offset", "cusum_threshold"]
)
def test_cusum_requires_key(flat_inputs, missing_key):
    inputs = copy.deepcopy(flat_inputs)
    inputs["start_time_user"] = "cusum"
    del inputs[missing_key]
    with pytest.raises(ValueError, match="start_time_user='cusum'"):
        validate_inputs(inputs)


def test_float_start_time_does_not_require_mode_params(flat_inputs):
    inputs = copy.deepcopy(flat_inputs)
    inputs["start_time_user"] = 7.5e-7
    inputs.pop("carrier_band_time", None)
    inputs.pop("iq_threshold_factor", None)
    validate_inputs(inputs)


# --- _REQUIRED_BY_MODE: carrier_filter_type ---


@pytest.mark.parametrize("missing_key", ["order", "wid"])
def test_gaussian_notch_requires_key(flat_inputs, missing_key):
    inputs = copy.deepcopy(flat_inputs)
    inputs["carrier_filter_type"] = "gaussian_notch"
    del inputs[missing_key]
    with pytest.raises(ValueError, match="carrier_filter_type='gaussian_notch'"):
        validate_inputs(inputs)


@pytest.mark.parametrize("missing_key", ["wid", "t_fit_begin", "t_fit_end"])
def test_sin_fit_subtract_requires_key(flat_inputs, missing_key):
    inputs = copy.deepcopy(flat_inputs)
    inputs["carrier_filter_type"] = "sin_fit_subtract"
    del inputs[missing_key]
    with pytest.raises(ValueError, match="carrier_filter_type='sin_fit_subtract'"):
        validate_inputs(inputs)


def test_none_filter_does_not_require_order_wid(flat_inputs):
    inputs = copy.deepcopy(flat_inputs)
    inputs["carrier_filter_type"] = "none"
    inputs.pop("order", None)
    inputs.pop("wid", None)
    validate_inputs(inputs)


# --- t_after constraint ---


def test_t_after_exceeds_time_to_take_raises(flat_inputs):
    inputs = copy.deepcopy(flat_inputs)
    inputs["t_after"] = inputs["time_to_take"] + 1e-9
    with pytest.raises(ValueError, match="t_after"):
        validate_inputs(inputs)


# --- optional param warning ---


def test_missing_optional_C_L_warns(flat_inputs, caplog):
    inputs = copy.deepcopy(flat_inputs)
    inputs.pop("C_L", None)
    with caplog.at_level(logging.WARNING, logger="alpss"):
        validate_inputs(inputs)
    assert "C_L" in caplog.text


def test_present_optional_C_L_no_warning(flat_inputs, caplog):
    inputs = copy.deepcopy(flat_inputs)
    inputs["C_L"] = 5000.0
    with caplog.at_level(logging.WARNING, logger="alpss"):
        validate_inputs(inputs)
    assert "C_L" not in caplog.text
