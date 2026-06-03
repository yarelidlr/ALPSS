import pytest
import numpy as np
from alpss.analysis.shock import shock_analysis


def test_shock_analysis_computes_peak_shock_stress(valid_inputs):
    """Test that shock_analysis computes peak shock stress correctly."""
    # Create minimal vc_out with required fields
    vc_out = {
        "v_max_comp": 828.0849443007512,
    }

    # Extract material properties from valid_inputs
    inputs = {
        "density": valid_inputs["material"]["density"],
        "C0": valid_inputs["material"]["C0"],
    }

    # Run shock analysis
    result = shock_analysis(vc_out, **inputs)

    # Expected value: 0.5 * density * C0 * v_max_comp
    expected = 0.5 * inputs["density"] * inputs["C0"] * vc_out["v_max_comp"]

    assert "peak_shock_stress" in result
    assert result["peak_shock_stress"] == pytest.approx(expected, rel=1e-9)


def test_shock_analysis_missing_material_properties():
    """Test that shock_analysis returns NaN when material properties are missing."""
    vc_out = {
        "v_max_comp": 828.0849443007512,
    }

    # Empty inputs (no density or C0)
    result = shock_analysis(vc_out)

    assert "peak_shock_stress" in result
    assert np.isnan(result["peak_shock_stress"])


def test_shock_analysis_missing_only_density():
    """Test that shock_analysis returns NaN when density is missing."""
    vc_out = {
        "v_max_comp": 828.0849443007512,
    }

    inputs = {
        "C0": 6000.0,
    }

    result = shock_analysis(vc_out, **inputs)

    assert "peak_shock_stress" in result
    assert np.isnan(result["peak_shock_stress"])


def test_shock_analysis_missing_only_c0():
    """Test that shock_analysis returns NaN when C0 is missing."""
    vc_out = {
        "v_max_comp": 828.0849443007512,
    }

    inputs = {
        "density": 2700.0,
    }

    result = shock_analysis(vc_out, **inputs)

    assert "peak_shock_stress" in result
    assert np.isnan(result["peak_shock_stress"])
