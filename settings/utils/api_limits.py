"""Gestión de límites de llamadas a APIs de IA"""

from typing import Dict, Any

class APILimitManager:
    """Gestor de límites de llamadas a APIs"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._counters = {
            "openai": {"calls": 0, "tokens": 0},
            "gemini": {"calls": 0, "tokens": 0}
        }
    
    def increment(self, provider: str, tokens: int = 0):
        """Incrementa contador"""
        if provider in self._counters:
            self._counters[provider]["calls"] += 1
            self._counters[provider]["tokens"] += tokens
    
    def check_limit(self, provider: str) -> Dict[str, Any]:
        """Verifica límite"""
        api_limits = self.config.get("api_limits", {})
        if not api_limits.get("enabled", True):
            return {"allowed": True, "message": "Límites deshabilitados"}
        
        provider_config = api_limits.get("providers", {}).get(provider, {})
        if not provider_config:
            return {"allowed": True, "message": "Sin configuración"}
        
        max_calls = provider_config.get("max_calls_per_session", -1)
        
        # Sin límites (ollama)
        if max_calls == -1:
            return {"allowed": True, "message": "Sin límites"}
        
        current_calls = self._counters.get(provider, {}).get("calls", 0)
        
        if current_calls >= max_calls:
            return {"allowed": False, "message": f"Límite alcanzado ({current_calls}/{max_calls})"}
        
        return {"allowed": True, "message": "OK"}
    
    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas de uso"""
        stats = {}
        api_limits = self.config.get("api_limits", {})
        providers = api_limits.get("providers", {})
        
        for provider, counters in self._counters.items():
            config = providers.get(provider, {})
            max_calls = config.get("max_calls_per_session", -1)
            
            stats[provider] = {
                "calls": counters["calls"],
                "max_calls": max_calls,
                "remaining": max_calls - counters["calls"] if max_calls > 0 else "ilimitado"
            }
        
        return stats
