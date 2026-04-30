import logging
from datetime import datetime

from alpss.utils.helpers import extract_data
from alpss.detection.spall_doi_finder import spall_doi_finder
from alpss.carrier.frequency import carrier_frequency
from alpss.carrier.filter import carrier_filter
from alpss.velocity.calculation import velocity_calculation
from alpss.analysis.instantaneous_uncertainty import instantaneous_uncertainty_analysis

logger = logging.getLogger("alpss")


def run_velocity_phase(**inputs) -> dict:
    """Run Phase 1 (velocity processing). Returns sdf_out, cen, cf_out, vc_out, iua_out, start_time, end_time."""
    start_time = datetime.now()

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

    end_time = datetime.now()
    logger.info("Velocity processing complete in %s", end_time - start_time)

    return {
        "sdf_out": sdf_out,
        "cen": cen,
        "cf_out": cf_out,
        "vc_out": vc_out,
        "iua_out": iua_out,
        "start_time": start_time,
        "end_time": end_time,
    }
