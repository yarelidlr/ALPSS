import numpy as np


def compute_velocity_peaks(velocity_f_smooth, time_f):
    """Compute velocity peak metrics from the smoothed velocity signal.

    Returns a dict with:
    - peak_velocity_idx: index of maximum velocity
    - v_max_comp: maximum velocity value
    - t_max_comp: time at maximum velocity
    """
    peak_velocity_idx = int(np.argmax(velocity_f_smooth))
    return {
        "peak_velocity_idx": peak_velocity_idx,
        "v_max_comp": velocity_f_smooth[peak_velocity_idx],
        "t_max_comp": time_f[peak_velocity_idx],
    }
