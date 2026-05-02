import argparse

from alpss.alpss_watcher import Watcher
from alpss.alpss_main import alpss_main
import os
import json
import logging
import sys

def start_watcher():
    w = Watcher()
    w.run()

_SECTIONS = {
    "io", "stft", "start_time", "carrier", "velocity",
    "material", "spall", "hel", "uncertainty", "plotting",
}


def _flatten_config(config: dict) -> dict:
    """Flatten a nested section-based config into a single flat dict.

    Raises ValueError if the JSON config is flat (no recognised section keys).
    """
    has_sections = any(k in _SECTIONS for k in config)
    if not has_sections:
        raise ValueError(
            f"Config file must use nested sections. "
            f"Expected top-level keys from: {sorted(_SECTIONS)}. "
            f"Got: {sorted(config.keys())}"
        )
    flat = {}
    for section, value in config.items():
        if section in _SECTIONS and isinstance(value, dict):
            clashes = [k for k in value if k in flat]
            if clashes:
                raise ValueError(
                    f"Config key collision in section '{section}': "
                    f"{clashes} already defined in a previous section."
                )
            flat.update(value)
        else:
            flat[section] = value
    return flat


def load_json_config(config):
    """Load configuration from a JSON file.

    Accepts a file path (str) or a pre-built flat dict (programmatic use).
    JSON files must use the nested section format; flat dicts are passed through.
    """
    if isinstance(config, dict):
        return config  # programmatic use — trust the caller

    if isinstance(config, str) and os.path.exists(config):
        with open(config, "r") as file:
            return _flatten_config(json.load(file))

    raise ValueError(
        "Invalid config input: Provide a dictionary or a valid JSON file path."
    )

def alpss_main_with_config(config=None):
    """
    Run ALPSS with a given JSON configuration.

    Args:
        config (str or dict, optional): JSON config file, either given as parsable argument through CLI or directly as a string, or a dictionary containing config parameters.
    """

    if config is None: 
        # If called from CLI, parse arguments
        parser = argparse.ArgumentParser(
            description="Run ALPSS using a JSON config file"
        )
        parser.add_argument(
            "config_path", type=str, help="Path to the JSON configuration file"
        )
        args = parser.parse_args()
        config = load_json_config(args.config_path)

    # Load the dictionary or YAML config
    else:
        config = load_json_config(config)

    # Run ALPSS with the loaded config
    return alpss_main(**config)

def alpss_cli():
    """
    Entry point for console_scripts.
    Always uses sys.argv so `alpss /path/to/config.json` works.
    """
    try:
        sys.exit(alpss_main_with_config())
    except Exception as e:
        print(f"[ALPSS ERROR] {e}", file=sys.stderr)
        sys.exit(1)