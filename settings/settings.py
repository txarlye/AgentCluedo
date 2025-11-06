from pathlib import Path
from dotenv import load_dotenv
from typing import Any
import json, os

from .utils.read_config import load_config
from .utils.write_config import save_config
from .utils.api_limits import APILimitManager


class Settings:
    """Singleton para gestión de configuración"""
    _instance = None
    _initialized = False
    
    def __new__(cls, config_path=None):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config_path=None):
        if self._initialized:
            return 
        if config_path:
            self.config_path = Path(config_path)
        else:
            base_dir = Path(__file__).parent
            self.config_path = base_dir / "config.json" 
        self.config = load_config(self.config_path) 
        self._load_config_sections(config_path) 
        env_path = self.config_path.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path) 
        self._load_env_vars() 
        self.api_limits = APILimitManager(self.config) 
        self._initialized = True
    
    def _load_config_sections(self, path): 
        def load_config_internal(config_path, objective=None):
            if Path(config_path).exists() is not True: 
                print("⚠️No se encontró config.json, usando valores por defecto.")
                return {}
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f).get(objective, {})
        
        # Carga de config de Json:
        config_main     = load_config(self.config_path, "main")
        config_agentes  = load_config_internal(self.config_path, "Agentes")
        
        ########################################## ##################################
        
        
        self.main_name      = config_main.get("name")
        self.agentes        = config_agentes.get("ia_agente_texto")
        self.ollama_model   = config_agentes.get("ia_ollama_model")
        self.prompt_path    = config_agentes.get("prompt_path")
        
        
        
        
        
    def _load_env_vars(self):
        """Carga variables de entorno como atributos"""
        env_vars = [
            "HUGGINGFACE_TOKEN",
            "OPEN_AI_API",
            "API_HOST",
            "API_PORT"
        ]
        
        for var_name in env_vars:
            value = os.getenv(var_name)
            if value:
                setattr(self, var_name, value) 
    
    def save(self):
        """Guarda la configuración usando save_config"""
        save_config(self.config, self.config_path)


# Instancia global singleton
settings = Settings()