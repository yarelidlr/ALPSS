import numpy as np
from scipy import signal
import traceback
import logging


# function to pull out important points on the spall signal
def spall_analysis(vc_out, iua_out, **inputs):
    # if user wants to pull out the spall points
    if inputs["spall_calculation"] == "yes":
        # unpack dictionary values in to individual variables
        time_f = vc_out["time_f"]
        velocity_f_smooth = vc_out["velocity_f_smooth"]
        pb_neighbors = inputs["pb_neighbors"]
        pb_idx_correction = inputs["pb_idx_correction"]
        rc_neighbors = inputs["pb_neighbors"]
        rc_idx_correction = inputs["pb_idx_correction"]
        C0 = inputs["C0"]
        density = inputs["density"]
        freq_uncert = iua_out["freq_uncert"]
        vel_uncert = iua_out["vel_uncert"]

        # get the global peak velocity
        peak_velocity_idx = np.argmax(velocity_f_smooth)
        peak_velocity = velocity_f_smooth[peak_velocity_idx]

        # get the uncertainities associated with the peak velocity
        peak_velocity_freq_uncert = freq_uncert[peak_velocity_idx]
        peak_velocity_vel_uncert = vel_uncert[peak_velocity_idx]

        # attempt to get the fist local minimum after the peak velocity to get the pullback
        # velocity. 'order' is the number of points on each side to compare to.
        try:
            # --- Pullback (max tension) detection with physical constraints ---
            # The pullback velocity must be:
            #   1. After the peak velocity in time
            #   2. Positive (free surface cannot reverse through zero)
            #   3. Less than the peak velocity (energy conservation)
            # We search within a bounded time window after the peak.
            max_pullback_time = inputs.get("max_pullback_time", 100e-9)  # configurable, default 100 ns
            max_pullback_idx = np.searchsorted(
                time_f, time_f[peak_velocity_idx] + max_pullback_time, side="right"
            )
            max_pullback_idx = min(max_pullback_idx, len(time_f))

            # Search for relative minima only in the post-peak window
            search_slice = velocity_f_smooth[peak_velocity_idx:max_pullback_idx]
            if len(search_slice) < 2 * pb_neighbors + 1:
                raise ValueError(
                    f"Post-peak search window too short ({len(search_slice)} points) "
                    f"for pb_neighbors={pb_neighbors}. Increase max_pullback_time or decrease pb_neighbors."
                )

            rel_min_local = signal.argrelmin(search_slice, order=pb_neighbors)[0]

            # Filter: must be positive and less than peak velocity
            valid_mask = (
                (search_slice[rel_min_local] > 0) &
                (search_slice[rel_min_local] < peak_velocity)
            )
            valid_minima = rel_min_local[valid_mask]

            if len(valid_minima) == 0:
                raise ValueError(
                    "No physically valid pullback minimum found (positive velocity, below peak) "
                    f"within {max_pullback_time/1e-9:.0f} ns after peak compression."
                )

            # Take the first valid minimum (closest to peak), apply user correction
            selected_local_idx = valid_minima[0 + pb_idx_correction]
            max_ten_idx = peak_velocity_idx + selected_local_idx

            # get the uncertainties associated with the max tension velocity
            max_ten_freq_uncert = freq_uncert[max_ten_idx]
            max_ten_vel_uncert = vel_uncert[max_ten_idx]

            # get the velocity at max tension
            max_tension_velocity = velocity_f_smooth[max_ten_idx]

            # calculate the pullback velocity
            pullback_velocity = peak_velocity - max_tension_velocity

            # calculate the estimated strain rate and spall strength
            strain_rate_est = (
                (0.5 / C0)
                * pullback_velocity
                / (time_f[max_ten_idx] - time_f[peak_velocity_idx])
            )
            spall_strength_est = 0.5 * density * C0 * pullback_velocity

            # Plausibility warning (not an error — exotic materials may exceed this)
            max_plausible_spall_gpa = inputs.get("max_plausible_spall_gpa", 20.0)
            if spall_strength_est / 1e9 > max_plausible_spall_gpa:
                logging.warning(
                    "Spall strength %.2f GPa exceeds plausibility threshold %.1f GPa. "
                    "Check signal quality and pullback detection.",
                    spall_strength_est / 1e9, max_plausible_spall_gpa,
                )

            # set final variables for the function return
            t_max_comp = time_f[peak_velocity_idx]
            t_max_ten = time_f[max_ten_idx]
            v_max_comp = peak_velocity
            v_max_ten = max_tension_velocity

        # if the program fails to find the peak and pullback velocities, then input nan's and continue with the program
        except Exception:
            logging.error("Could not locate the peak and/or pullback velocity")
            logging.error(traceback.format_exc())

            t_max_comp = np.nan
            t_max_ten = np.nan
            v_max_comp = np.nan
            v_max_ten = np.nan
            strain_rate_est = np.nan
            spall_strength_est = np.nan
            max_ten_freq_uncert = np.nan
            max_ten_vel_uncert = np.nan

        # try to get the recompression peak that occurs after pullback
        try:
            # Search for recompression peak after the pullback minimum, within the bounded window
            rc_search_slice = velocity_f_smooth[max_ten_idx:max_pullback_idx]
            rel_max_local = signal.argrelmax(rc_search_slice, order=rc_neighbors)[0]

            # Filter: recompression must be positive
            valid_rc = rel_max_local[rc_search_slice[rel_max_local] > 0]

            if len(valid_rc) == 0:
                raise ValueError("No valid recompression peak found after pullback.")

            rc_local_idx = valid_rc[0 + rc_idx_correction]
            rc_idx = max_ten_idx + rc_local_idx
            t_rc = time_f[rc_idx]
            v_rc = velocity_f_smooth[rc_idx]

        # if finding the recompression peak fails then input nan's and continue
        except Exception:
            logging.error("Could not locate the recompression velocity")
            logging.error(traceback.format_exc())
            t_rc = np.nan
            v_rc = np.nan

    # if user does not want to pull out the spall points just set everything to nan
    else:
        t_max_comp = np.nan
        t_max_ten = np.nan
        t_rc = np.nan
        v_max_comp = np.nan
        v_max_ten = np.nan
        v_rc = np.nan
        spall_strength_est = np.nan
        strain_rate_est = np.nan
        peak_velocity_freq_uncert = np.nan
        peak_velocity_vel_uncert = np.nan
        max_ten_freq_uncert = np.nan
        max_ten_vel_uncert = np.nan

    # return a dictionary of the results
    sa_out = {
        "t_max_comp": t_max_comp,
        "t_max_ten": t_max_ten,
        "t_rc": t_rc,
        "v_max_comp": v_max_comp,
        "v_max_ten": v_max_ten,
        "v_rc": v_rc,
        "spall_strength_est": spall_strength_est,
        "strain_rate_est": strain_rate_est,
        "peak_velocity_freq_uncert": peak_velocity_freq_uncert,
        "peak_velocity_vel_uncert": peak_velocity_vel_uncert,
        "max_ten_freq_uncert": max_ten_freq_uncert,
        "max_ten_vel_uncert": max_ten_vel_uncert,
    }

    return sa_out
