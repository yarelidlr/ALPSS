import json
from alpss.commands import alpss_multipoint_with_config, alpss_main_with_config

with open("tests/input_data/multipoint/multipoint_config.json") as f:
    config = json.load(f)

config["display_plots"] = "yes"
config["spall_calculation"] = "no"

alpss_multipoint_with_config(config)