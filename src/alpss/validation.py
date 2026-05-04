_ALWAYS_REQUIRED = [
    "filepath", "out_files_dir", "header_lines",
    "time_to_skip", "time_to_take", "t_before", "t_after",
    "start_time_user", "start_time_correction",
    "sample_rate", "nperseg", "noverlap", "nfft", "window",
    "freq_min", "freq_max",
    "blur_kernel", "blur_sigx", "blur_sigy",
    "carrier_filter_type", "order", "wid",
    "smoothing_window", "smoothing_wid", "smoothing_amp",
    "smoothing_sigma", "smoothing_mu",
    "lam", "theta",
    "C0", "density", "delta_rho", "delta_C0", "delta_lam", "delta_theta",
    "pb_neighbors", "pb_idx_correction", "rc_neighbors", "rc_idx_correction",
    "spall_calculation",
    "uncert_mult",
    "cmap", "plot_figsize", "plot_dpi",
    "save_data", "display_plots",
    "hel_start_time_ns", "hel_end_time_ns", "hel_angle_threshold_deg",
    "hel_detection_min_points", "minimum_HEL_velocity_expected",
]

# Optional keys — not validated but documented here for discoverability.
# bytestring: raw CSV bytes; alternative to filepath for in-memory data
# C_L: longitudinal wave speed for HEL strain rate; falls back to C0 if absent
# material: label string used in plot titles
_OPTIONAL = ["bytestring", "C_L", "material"]

_REQUIRED_BY_MODE = {
    "start_time_user=otsu": ["carrier_band_time"],
    "start_time_user=iq": ["iq_threshold_factor"],
    "start_time_user=cusum": ["carrier_band_time", "cusum_offset", "cusum_threshold"],
    "carrier_filter_type=sin_fit_subtract": ["t_fit_begin", "t_fit_end"],
}


def validate_inputs(inputs):
    missing = [k for k in _ALWAYS_REQUIRED if k not in inputs]
    if missing:
        raise ValueError(f"Missing required config keys: {missing}")

    if inputs.get("start_time_user") == "otsu":
        missing = [k for k in _REQUIRED_BY_MODE["start_time_user=otsu"] if k not in inputs]
        if missing:
            raise ValueError(f"start_time_user='otsu' requires: {missing}")

    if inputs.get("start_time_user") == "iq":
        missing = [k for k in _REQUIRED_BY_MODE["start_time_user=iq"] if k not in inputs]
        if missing:
            raise ValueError(f"start_time_user='iq' requires: {missing}")

    if inputs.get("start_time_user") == "cusum":
        missing = [k for k in _REQUIRED_BY_MODE["start_time_user=cusum"] if k not in inputs]
        if missing:
            raise ValueError(f"start_time_user='cusum' requires: {missing}")

    if inputs.get("carrier_filter_type") == "sin_fit_subtract":
        missing = [k for k in _REQUIRED_BY_MODE["carrier_filter_type=sin_fit_subtract"] if k not in inputs]
        if missing:
            raise ValueError(f"carrier_filter_type='sin_fit_subtract' requires: {missing}")

    if inputs["t_after"] > inputs["time_to_take"]:
        raise ValueError("'t_after' must be less than 'time_to_take'.")
