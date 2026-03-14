import ast
import csv
import json
import pathlib
import pprint
from alpss.alpss_main import alpss_main

WORKDIR = pathlib.Path("/Users/elbert/alpss_foo")
INPUTS_CSV = WORKDIR / "JHAMAA00003-02_2025-12-18_18-38-57_shot01_ch1-inputs.csv"
DATA_DIR = WORKDIR / "data"
OUTPUT_DIR = WORKDIR / "output"

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def parse_value(raw):
    raw = raw.strip()

    try:
        return int(raw)
    except ValueError:
        pass

    try:
        return float(raw)
    except ValueError:
        pass

    try:
        return json.loads(raw)
    except Exception:
        pass

    try:
        return ast.literal_eval(raw)
    except Exception:
        pass

    return raw.strip('"')

params = {}
with INPUTS_CSV.open(newline="") as f:
    reader = csv.reader(f)
    for row in reader:
        if not row or len(row) < 2:
            continue
        key = row[0].strip()
        value = row[1].strip()
        params[key] = parse_value(value)

params["filepath"] = str(DATA_DIR / pathlib.Path(str(params["filepath"])).name)
params["out_files_dir"] = str(OUTPUT_DIR)

# normalize a few fields that ALPSS/OpenCV expect
if "blur_kernel" in params and isinstance(params["blur_kernel"], list):
    params["blur_kernel"] = tuple(params["blur_kernel"])

if "plot_figsize" in params and isinstance(params["plot_figsize"], list):
    params["plot_figsize"] = tuple(params["plot_figsize"])

if isinstance(params.get("hel_detection_enabled"), str):
    if params["hel_detection_enabled"].lower() == "true":
        params["hel_detection_enabled"] = True
    elif params["hel_detection_enabled"].lower() == "false":
        params["hel_detection_enabled"] = False

print("Resolved parameters:")
pprint.pprint(params)

result = alpss_main(**params)
print(result)