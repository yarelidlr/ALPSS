def shock_analysis(vc_out, **inputs):
    """Compute shock-related metrics from velocity data and material properties."""
    shock_out = {}

    if "density" in inputs and "C0" in inputs:
        shock_out["peak_shock_stress"] = (
            0.5 * inputs["density"] * inputs["C0"] * vc_out["v_max_comp"]
        )
    else:
        shock_out["peak_shock_stress"] = float("nan")

    return shock_out
