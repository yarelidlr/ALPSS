import logging
from alpss.alpss_main import alpss_main

logger = logging.getLogger("alpss")

_C = 3e8  # speed of light (m/s)


def alpss_multipoint(channels, filepath, freq_lower=1e9, freq_upper=1e9, **kwargs):
    """Run alpss_main over every probe in a multi-point PDV channel configuration.

    Parameters
    ----------
    channels : dict[str, pd.DataFrame]
        Keys are channel names (e.g. ``"ch1"``); values are DataFrames with
        columns ``tar_lam`` (nm), ``ref_lam`` (nm), and ``probe_number``.
    filepath : str
        Path to the input file with ``{channel}`` as a placeholder for the
        channel name, e.g.
        ``r"C:/data/shot_00006_{channel}.csv"``.
    freq_lower : float
        How far below the beat frequency to set ``freq_min`` (Hz). Default is 1 GHz.
    freq_upper : float
        How far above the beat frequency to set ``freq_max`` (Hz). Default is 1 GHz.
    **kwargs
        All other keyword arguments are forwarded to :func:`alpss_main`.
        ``filepath``, ``multipoint_probe``, ``lam``, ``freq_min``, and
        ``freq_max`` are set automatically and should **not** be passed here.

    Returns
    -------
    list[tuple]
        One ``(fig, items)`` tuple per probe, in channel-then-probe order.
    """
    reserved = {"filepath", "multipoint_probe", "lam", "freq_min", "freq_max"}
    conflicts = reserved & kwargs.keys()
    if conflicts:
        raise ValueError(
            f"The following kwargs are set automatically by alpss_multipoint "
            f"and must not be passed manually: {conflicts}"
        )

    results = []
    for channel_name, channel_df in channels.items():
        channel_filepath = filepath.format(channel=channel_name)
        for _, row in channel_df.iterrows():
            tar_lam_nm = row["tar_lam"]
            ref_lam_nm = row["ref_lam"]
            probe_number = int(row["probe_number"])

            # Beat frequency between target and reference wavelengths
            upshift = _C / (tar_lam_nm * 1e-9) - _C / (ref_lam_nm * 1e-9)

            logger.info(
                "Channel %s | probe %s | upshift=%.4f GHz",
                channel_name,
                probe_number,
                upshift / 1e9,
            )

            try:
                result = alpss_main(
                    filepath=channel_filepath,
                    multipoint_probe=probe_number,
                    lam=ref_lam_nm * 1e-9,
                    freq_min=upshift - freq_lower,
                    freq_max=upshift + freq_upper,
                    **kwargs,
                )
                results.append(result)
            except Exception as e:
                logger.error(
                    "Channel %s | probe %s failed: %s — skipping.",
                    channel_name,
                    probe_number,
                    e,
                )
                results.append(None)

    return results