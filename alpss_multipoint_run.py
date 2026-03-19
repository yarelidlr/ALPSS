import json
from alpss.commands import alpss_multipoint_with_config

with open("docs/files/multipoint_config.json") as f:
    config = json.load(f)

config["out_files_dir"] = "tests/output_data/"
config["sample_rate"] = 128e9
config["carrier_band_time"] = 100e-9
config["start_time_detection"] = "cusum"
config["cusum_offset"] = 2
config["time_to_skip"] = 0e-6
config["time_to_take"] = 3e-6
config["t_after"] = 750e-9
config["carrier_filter_type"] = "gaussian_notch"
config["wid"] = 0.25e9
config["display_plots"] = "yes"
config["plot_dpi"] = 300
config["plot_figsize"] = (30, 10)


alpss_multipoint_with_config(config)