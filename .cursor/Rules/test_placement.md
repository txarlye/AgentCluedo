# Reglas de Ubicación de Tests

## Ubicación de Archivos de Test

Cuando se creen archivos de test, seguir estas reglas:

### Tests Unitarios
- **Ubicación**: `test/unitary_test/`
- **Formato**: `test_<nombre_del_modulo>.py`
- **Ejemplo**: Para `settings/settings.py` → `test/unitary_test/test_settings.py`

### Tests de Integración
- **Ubicación**: `test/integration_test/` (si existe)
- **Formato**: `test_integration_<nombre>.py`

### Reglas de Documentación/Configuración
- **Ubicación**: `.cursor/Rules/`
- **Formato**: Archivos `.md` o `.txt` con descripción de reglas

## Estructura de Tests Unitarios

Los tests unitarios deben seguir esta estructura:

```python
import unittest
from pathlib import Path
import sys

# Agregar el directorio raíz al path si es necesario
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestModuleName(unittest.TestCase):
    def setUp(self):
        """Configuración inicial para cada test"""
        pass
    
    def test_specific_functionality(self):
        """Descripción del test"""
        # Arrange
        # Act
        # Assert
        pass

if __name__ == '__main__':
    unittest.main()
```

## Notas Importantes

- Siempre crear los tests en `test/unitary_test/` cuando sean tests unitarios
- Mantener la estructura de carpetas organizada
- Usar nombres descriptivos para los archivos de test
- Seguir las convenciones de naming: `test_<modulo_o_funcion>.py`


