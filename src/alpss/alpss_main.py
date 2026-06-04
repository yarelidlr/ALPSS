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
from alpss.utils.defaults import (
    default_spall_output,
    default_uncertainty_output,
    default_hel_output,
    default_shock_output,
)
from datetime import datetime


logger = setup_alpss_logger()


# main function to link together all the sub-functions
def alpss_main(**inputs):
    inputs = flatten_config(inputs)
    validate_inputs(inputs)

    # --- Phase 1: Velocity Processing ---
    vel, velocity_ok, velocity_error = run_velocity_phase(**inputs)

    sdf_out = vel.get("sdf_out") if velocity_ok else {}
    cen = vel.get("cen") if velocity_ok else None
    cf_out = vel.get("cf_out") if velocity_ok else {}
    vc_out = vel.get("vc_out") if velocity_ok else {}
    iua_out = vel.get("iua_out") if velocity_ok else {}
    start_time = vel.get("start_time") if velocity_ok else datetime.now()
    end_time = vel.get("end_time") if velocity_ok else datetime.now()

    errors = []
    if velocity_error:
        errors.append(velocity_error)

    # --- Phase 2a: Spall analysis (optional) ---
    sa_out, spall_ok, spall_error = run_spall_phase(vc_out, iua_out, **inputs) if velocity_ok else (default_spall_output(), False, "spall: skipped due to velocity_ok=false")
    if spall_error:
        errors.append(spall_error)

    # --- Phase 2b: Full uncertainty analysis ---
    fua_out, uncertainty_ok, uncertainty_error = run_uncertainty_phase(
        cen, vc_out, sa_out, iua_out, spall_ok, **inputs
    ) if velocity_ok else (default_uncertainty_output(), False, "uncertainty: skipped due to velocity_ok=false")
    if uncertainty_error:
        errors.append(uncertainty_error)

    # --- Phase 2c: HEL detection (optional) ---
    hel_out, hel_error = run_hel_phase(vc_out, iua_out, **inputs) if velocity_ok else (default_hel_output(), "hel: skipped due to velocity_ok=false")
    if hel_error:
        errors.append(hel_error)

    # --- Phase 2d: Shock analysis ---
    shock_out, shock_error = run_shock_phase(vc_out, **inputs) if velocity_ok else (default_shock_output(), "shock: skipped due to velocity_ok=false")
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
        end_time_final,
        velocity_ok,
        spall_ok,
        uncertainty_ok,
        errors,
        **inputs,
    )

    return (fig, items)
