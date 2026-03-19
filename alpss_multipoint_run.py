import json
from alpss.commands import alpss_multipoint_with_config

with open("docs/files/multipoint_config.json") as f:
    config = json.load(f)

config["filepath"] = "tests/input_data/Multi_PDV_test--20260311--00028_{channel}.csv"
config["out_files_dir"] = "tests/output_data/"
# config["channels"] = {
#     "ch1": [
#         {"tar_lam": 1550.000, "ref_lam": 1550.016, "probe_number": 10}
#     ],
#     "ch2": [
#         {"tar_lam": 1531.116, "ref_lam": 1531.140, "probe_number": 6},
#         {"tar_lam": 1537.397, "ref_lam": 1537.453, "probe_number": 9},
#     ],
#     "ch3": [
#         {"tar_lam": 1531.236, "ref_lam": 1531.316, "probe_number": 3},
#         {"tar_lam": 1537.549, "ref_lam": 1537.605, "probe_number": 8},
#         {"tar_lam": 1543.906, "ref_lam": 1543.930, "probe_number": 19},
#         {"tar_lam": 1550.116, "ref_lam": 1550.260, "probe_number": 15}
#     ]
# }

config["freq_refine_lower"] = 0.25e9
config["freq_refine_upper"] = 1e9

config["start_time_user"] = "cusum"
config["cusum_offset"] = 2.5
config["cusum_threshold"] = 1000

config["t_after"] = 750e-9
config["smoothing_window"] = 1501

config["carrier_filter_type"] = "sin_fit_subtract"
config["t_fit_begin"] = 100e-9
config["t_fit_end"] = 200e-9
config["wid"] = 0.3e9

config["display_plots"] = "yes"
config["spall_calculation"] = "no"
config["plot_dpi"] = 300
config["plot_figsize"] = (30, 10)


alpss_multipoint_with_config(config)