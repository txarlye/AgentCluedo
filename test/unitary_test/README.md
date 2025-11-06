# Tests Unitarios

Esta carpeta contiene todos los tests unitarios del proyecto AgentCluedo.

## Estructura

- Los archivos de test deben seguir el formato: `test_<nombre_modulo>.py`
- Cada test debe estar en una clase que herede de `unittest.TestCase`
- Usar nombres descriptivos para los métodos de test: `test_<descripcion_funcionalidad>`

## Ejemplo

```python
import unittest
from settings.settings import Settings

class TestSettings(unittest.TestCase):
    def test_settings_singleton(self):
        """Verifica que Settings sea un singleton"""
        settings1 = Settings()
        settings2 = Settings()
        self.assertIs(settings1, settings2)
```

## Ejecutar Tests

```bash
# Ejecutar todos los tests
python -m unittest discover test/unitary_test

# Ejecutar un test específico
python -m unittest test.unitary_test.test_settings
```


