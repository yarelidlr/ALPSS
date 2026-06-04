import logging
import traceback
from datetime import datetime
import os

from alpss.io.reading import extract_data
from alpss.io.saving import save
from alpss.detection.spall_doi_finder import spall_doi_finder
from alpss.carrier.frequency import carrier_frequency
from alpss.carrier.filter import carrier_filter
from alpss.velocity.calculation import velocity_calculation
from alpss.analysis.instantaneous_uncertainty import instantaneous_uncertainty_analysis
from alpss.analysis.velocity_uncertainty import velocity_uncertainty_analysis
from alpss.analysis.spall import spall_analysis
from alpss.analysis.full_uncertainty import full_uncertainty_analysis
from alpss.analysis.shock import shock_analysis
from alpss.analysis.hel import hel_detection
from alpss.plotting.plots import plot_results
from alpss.plotting.hel import plot_hel_detection
from alpss.utils.defaults import (
    default_spall_output,
    default_uncertainty_output,
    default_shock_output,
    default_hel_output,
)

logger = logging.getLogger("alpss")


def run_velocity_phase(**inputs) -> tuple:
    """Run Phase 1 (velocity processing). Returns (vel_out, velocity_ok, error_msg)."""
    start_time = datetime.now()
    velocity_ok = False
    error_msg = None
    vel_out = {}

    try:
        data = extract_data(inputs)
        logger.info("Extracted %d samples", len(data))

        sdf_out = spall_doi_finder(data, **inputs)
        logger.info(
            "Spall DOI found: start=%.3e s, end=%.3e s",
            sdf_out["t_doi_start"],
            sdf_out["t_doi_end"],
        )

        cen = carrier_frequency(sdf_out, **inputs)
        logger.info("Carrier frequency: %.6e Hz", cen)

        cf_out = carrier_filter(sdf_out, cen, **inputs)
        logger.info("Carrier filter applied")

        vc_out = velocity_calculation(sdf_out, cen, cf_out, **inputs)
        logger.info("Velocity calculated (%d points)", len(vc_out["time_f"]))

        iua_out = instantaneous_uncertainty_analysis(sdf_out, vc_out, cen, **inputs)
        logger.info("Instantaneous uncertainty computed")

        vu_out = velocity_uncertainty_analysis(vc_out, iua_out)
        vc_out.update(vu_out)
        logger.info("Velocity uncertainties computed")

        end_time = datetime.now()
        logger.info("Velocity processing complete in %s", end_time - start_time)

        vel_out = {
            "sdf_out": sdf_out,
            "cen": cen,
            "cf_out": cf_out,
            "vc_out": vc_out,
            "iua_out": iua_out,
            "start_time": start_time,
            "end_time": end_time,
        }
        velocity_ok = True

    except Exception as e:
        error_msg = f"velocity: {e}"
        logger.error("Error in velocity processing: %s", str(e))
        logger.error("Traceback: %s", traceback.format_exc())
        try:
            from alpss.plotting.plots import plot_voltage

            plot_voltage(extract_data(inputs), **inputs)
        except Exception:
            logger.error("Fallback voltage plot also failed.")

    return vel_out, velocity_ok, error_msg


def run_spall_phase(vc_out, iua_out, **inputs) -> tuple:
    """Phase 2a: Spall analysis (optional). Returns (sa_out, spall_ok, error_msg)."""
    sa_out = default_spall_output()
    spall_ok = False
    error_msg = None

    if inputs["spall_enabled"]:
        try:
            logger.info("Running spall analysis...")
            sa_out = spall_analysis(vc_out, iua_out, **inputs)
            spall_ok = True
            logger.info(
                "Spall analysis complete: spall strength=%.4f, strain rate=%.4e",
                sa_out["spall_strength_est"],
                sa_out["strain_rate_est"],
            )
        except Exception as e:
            error_msg = f"spall: {e}"
            logger.error("Error in spall analysis: %s", str(e))
            logger.error("Traceback: %s", traceback.format_exc())
            logger.info("Continuing without spall analysis.")

    return sa_out, spall_ok, error_msg


def run_uncertainty_phase(cen, vc_out, sa_out, iua_out, spall_ok, **inputs) -> tuple:
    """Phase 2b: Uncertainty analysis. Returns (fua_out, uncertainty_ok, error_msg)."""
    fua_out = default_uncertainty_output()
    uncertainty_ok = False
    error_msg = None

    try:
        logger.info("Running full uncertainty analysis...")
        fua_out = full_uncertainty_analysis(cen, vc_out, sa_out, iua_out, spall_ok, **inputs)
        uncertainty_ok = True
        logger.info(
            "Uncertainty analysis complete."
        )
    except Exception as e:
        error_msg = f"uncertainty: {e}"
        logger.error("Error in full uncertainty analysis: %s", str(e))
        logger.error("Traceback: %s", traceback.format_exc())
        logger.info("Continuing without full uncertainty analysis.")

    return fua_out, uncertainty_ok, error_msg


def run_hel_phase(vc_out, iua_out, **inputs) -> tuple:
    """Phase 2c: HEL detection (optional). Returns (hel_out, error_msg)."""
    hel_out = default_hel_output()
    error_msg = None

    if inputs["hel_enabled"]:
        try:
            logger.info("Running HEL detection...")
            # Convert velocity time from seconds to nanoseconds for HEL
            time_ns = vc_out["time_f"] / 1e-9
            hel_out = hel_detection(
                time_ns,
                vc_out["velocity_f_smooth"],
                iua_out["vel_uncert"],
                hel_start_ns=inputs.get("hel_start_time_ns"),
                hel_end_ns=inputs.get("hel_end_time_ns"),
                angle_threshold_deg=inputs.get("hel_angle_threshold_deg"),
                min_points=inputs.get("hel_detection_min_points"),
                min_velocity=inputs.get("minimum_HEL_velocity_expected"),
                density=inputs.get("density"),
                C_L=inputs.get("C_L"),
            )
            if hel_out.ok:
                logger.info(
                    "HEL detected: strength=%.4f GPa, FSV=%.2f m/s, time=%.2f ns",
                    hel_out.strength_gpa,
                    hel_out.free_surface_velocity,
                    hel_out.time_detection_ns,
                )
            else:
                if hel_out.error_message:
                    error_msg = f"hel: {hel_out.error_message}"
                logger.info("HEL detection complete: no HEL found")
        except Exception as e:
            error_msg = f"hel: {e}"
            logger.error("Error in HEL detection: %s", str(e))
            logger.error("Traceback: %s", traceback.format_exc())
            logger.info("Continuing without HEL results.")

    return hel_out, error_msg


def run_shock_phase(vc_out, **inputs) -> tuple:
    """Phase 2d: Shock analysis. Returns (shock_out, error_msg)."""
    shock_out = default_shock_output()
    error_msg = None

    try:
        logger.info("Running shock analysis...")
        shock_out = shock_analysis(vc_out, **inputs)
        logger.info("Shock analysis complete: peak shock stress=%.4f Pa", shock_out["peak_shock_stress"])
    except Exception as e:
        error_msg = f"shock: {e}"
        logger.error("Error in shock analysis: %s", str(e))
        logger.error("Traceback: %s", traceback.format_exc())
        logger.info("Continuing without shock analysis.")

    return shock_out, error_msg


def run_output_phase(
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
    velocity_ok,
    spall_ok,
    uncertainty_ok,
    errors,
    **inputs,
) -> tuple:
    """Phase 3: Output (plotting + saving). Returns (fig, hel_fig, items)."""
    # Generate plots
    logger.info("Generating plots...")
    fig = plot_results(
        sdf_out,
        cen,
        cf_out,
        vc_out,
        sa_out,
        iua_out,
        fua_out,
        shock_out,
        start_time,
        end_time,
        **inputs,
    )

    # Generate HEL diagnostic plot
    hel_fig = None
    if hel_out.ok:
        try:
            time_ns = vc_out["time_f"] / 1e-9
            hel_fig = plot_hel_detection(
                time_ns,
                vc_out["velocity_f_smooth"],
                hel_out,
                hel_start_ns=inputs["hel_start_time_ns"],
                hel_end_ns=inputs["hel_end_time_ns"],
                angle_threshold_deg=inputs["hel_angle_threshold_deg"],
                sample_name=os.path.basename(inputs.get("filepath", "")),
            )
            if not inputs["display_plots"]:
                import matplotlib.pyplot as _plt

                _plt.close(hel_fig)
        except Exception as e:
            logger.error("Error generating HEL plot: %s", str(e))

    logger.info("Plots generated")

    # Save outputs
    logger.info("Saving outputs...")
    items = save(
        sdf_out,
        cen,
        vc_out,
        sa_out,
        iua_out,
        fua_out,
        shock_out,
        start_time,
        end_time,
        fig,
        velocity_ok,
        spall_ok,
        uncertainty_ok,
        iq_fig=sdf_out.get("iq_fig"),
        hel_fig=hel_fig,
        hel_out=hel_out,
        error_msg="; ".join(errors) if errors else "",
        **inputs,
    )

    logger.info("Outputs saved")

    return fig, hel_fig, items
