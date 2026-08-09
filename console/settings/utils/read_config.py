import json
from pathlib import Path

def load_config(path="config.json", objective=None): 
    path_obj = Path(path) if not isinstance(path, Path) else path
    if not path_obj.exists():
        print("⚠️ No se encontró config.json, usando valores por defecto.")
        return {}
    with open(path_obj, "r", encoding="utf-8") as f:
        config = json.load(f)
        return config.get(objective, {}) if objective else config
