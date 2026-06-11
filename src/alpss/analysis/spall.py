import numpy as np


# function to pull out important points on the spall signal
def spall_analysis(vc_out, iua_out, **inputs):
    C0 = inputs["C0"]
    density = inputs["density"]
    freq_uncert = iua_out["freq_uncert"]
    vel_uncert = iua_out["vel_uncert"]

    max_ten_idx = vc_out["max_ten_idx"]
    t_max_ten = vc_out["t_max_ten"]
    v_max_ten = vc_out["v_max_ten"]
    t_rc = vc_out["t_rc"]
    v_rc = vc_out["v_rc"]

    max_ten_freq_uncert = freq_uncert[max_ten_idx]
    max_ten_vel_uncert = vel_uncert[max_ten_idx]

    pullback_velocity = vc_out["v_max_comp"] - v_max_ten

    strain_rate_est = (
        (0.5 / C0)
        * pullback_velocity
        / (t_max_ten - vc_out["t_max_comp"])
    )
    spall_strength_est = 0.5 * density * C0 * pullback_velocity

    return {
        "t_max_ten": t_max_ten,
        "t_rc": t_rc,
        "v_max_ten": v_max_ten,
        "v_rc": v_rc,
        "spall_strength_est": spall_strength_est,
        "strain_rate_est": strain_rate_est,
        "max_ten_freq_uncert": max_ten_freq_uncert,
        "max_ten_vel_uncert": max_ten_vel_uncert,
    }
