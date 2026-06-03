from alpss.plotting.plots import plot_voltage
from alpss.utils.validation import validate_inputs
from alpss.utils.config import flatten_config
from alpss.utils.phases import (
    run_velocity_phase,
    run_spall_phase,
    run_uncertainty_phase,
    run_shock_phase,
    run_hel_phase,
    run_output_phase,
)
from alpss.utils.logging import setup_alpss_logger
from datetime import datetime


logger = setup_alpss_logger()


# main function to link together all the sub-functions
def alpss_main(**inputs):
    inputs = flatten_config(inputs)
    validate_inputs(inputs)

    # --- Phase 1: Velocity Processing ---
    try:
        vel = run_velocity_phase(**inputs)
    except Exception as e:
        logger.error("Error in velocity processing: %s", str(e))
        try:
            from alpss.io.reading import extract_data

            plot_voltage(extract_data(inputs), **inputs)
        except Exception:
            logger.error("Fallback voltage plot also failed.")
        raise

    sdf_out = vel["sdf_out"]
    cen = vel["cen"]
    cf_out = vel["cf_out"]
    vc_out = vel["vc_out"]
    iua_out = vel["iua_out"]
    start_time = vel["start_time"]
    end_time = vel["end_time"]

    # --- Phase 2a: Spall analysis (optional) ---
    errors = []
    sa_out, spall_ok, spall_error = run_spall_phase(vc_out, iua_out, **inputs)
    if spall_error:
        errors.append(spall_error)

    # --- Phase 2b: Full uncertainty analysis ---
    fua_out, uncertainty_ok, uncertainty_error = run_uncertainty_phase(
        cen, vc_out, sa_out, iua_out, spall_ok, **inputs
    )
    if uncertainty_error:
        errors.append(uncertainty_error)

    # --- Phase 2c: HEL detection (optional) ---
    hel_out, hel_error = run_hel_phase(vc_out, iua_out, **inputs)
    if hel_error:
        errors.append(hel_error)

    # --- Phase 2d: Shock analysis ---
    shock_out, shock_error = run_shock_phase(vc_out, **inputs)
    if shock_error:
        errors.append(shock_error)

    # --- Phase 3: Output (plotting + saving) ---
    end_time_final = datetime.now()
    logger.info(f"\nFull runtime: {end_time_final - start_time}\n")

    fig, hel_fig, items = run_output_phase(
        sdf_out,
        cen,
        cf_out,
        vc_out,
        sa_out,
        iua_out,
        fua_out,
        shock_out,
        hel_out,
        start_time,
        end_time,
        spall_ok,
        uncertainty_ok,
        errors,
        **inputs,
    )

    return (fig, items)
