import json
from pathlib import Path

def save_config(config_data, path="config.json"):
    path_obj = Path(path) if not isinstance(path, Path) else path
    with open(path_obj, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=2)