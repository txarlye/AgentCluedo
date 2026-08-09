from pathlib import Path
from settings.settings import settings

def load_prompt(file_name: str) -> str:
    prompt_path = Path(settings.prompt_path) / file_name
    if not prompt_path.exists():
        raise FileExistsError(f"No se encontró el prompt {prompt_path}")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read() 