# Sistema de Validación de Herramientas @tool

## Propósito

El sistema de validación de herramientas @tool es un mecanismo de análisis estático que inspecciona funciones decoradas con `@tool` en el archivo `tools.py` para verificar el cumplimiento de estándares de calidad de código. El sistema valida:

- **Docstrings**: Verifica que cada función tenga un docstring descriptivo de al menos 10 caracteres
- **Type hints en parámetros**: Verifica que todos los parámetros (excepto `self` y `cls`) tengan anotaciones de tipo
- **Type hint de retorno**: Verifica que cada función tenga una anotación de tipo de retorno

El sistema se ejecuta automáticamente al inicio del agente CloudArquitecto, antes de que comience a aceptar entrada del usuario. Las validaciones se completan en menos de 500ms para archivos con hasta 50 funciones, y los resultados se muestran como advertencias visuales en la consola sin bloquear el inicio del agente.

## Características Principales

- **No invasivo**: La validación no modifica el código ni interfiere con la ejecución normal del agente
- **Rápido**: Análisis completo en < 500ms para 50 funciones
- **Robusto**: Manejo de errores que permite al agente iniciar incluso si la validación falla
- **Informativo**: Mensajes claros que identifican exactamente qué necesita corrección
- **Visual**: Usa colores ANSI y emojis para mejorar la legibilidad (cuando el terminal lo soporta)

## Integración con agent.py

El sistema se integra con `agent.py` mediante una simple llamada al inicio del archivo:

```python
from tool_validator import Validation_Hook

# Ejecutar validación de herramientas @tool al inicio
Validation_Hook.run()
```

Esta llamada debe colocarse después de los imports pero antes de que el agente comience a aceptar entrada del usuario. La validación se ejecuta de forma síncrona y muestra advertencias en la consola si detecta problemas.

### Flujo de Ejecución

1. `agent.py` importa y ejecuta `Validation_Hook.run()` al inicio
2. `Tool_Validator` lee y parsea `tools.py` usando el módulo AST de Python
3. `AST_Inspector` recorre el árbol AST buscando decoradores `@tool`
4. Para cada función decorada, `Validation_Rules` verifica docstrings y type hints
5. Los errores se acumulan en una estructura `Validation_Result`
6. `Console_Formatter` muestra advertencias con formato visual
7. El agente continúa su ejecución normal

## Ejemplos de Salida

### Cuando hay errores de validación

```
⚠️  VALIDACIÓN DE HERRAMIENTAS @tool
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Función: estimar_costo_lambda (línea 15)
  ✗ Missing docstring
  ✗ Parameter 'invocaciones' missing type hint

Función: buscar_servicio (línea 42)
  ✗ Missing return type hint

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ 2 de 5 funciones tienen errores de validación
```

### Cuando no hay errores

```
✅ Validación exitosa: 5 funciones @tool cumplen los estándares
```

### Cuando el archivo tools.py no existe

El sistema simplemente no muestra ningún mensaje y permite que el agente continúe normalmente.

## Arquitectura del Sistema

El sistema sigue una arquitectura de pipeline lineal con los siguientes componentes:

### Componentes Principales

1. **Validation_Hook**: Punto de entrada que se invoca desde `agent.py`
   - Método: `run()` - Ejecuta la validación y captura excepciones

2. **Tool_Validator**: Motor de validación que coordina el análisis AST
   - Método: `validate_tools_file(filepath)` - Valida un archivo Python

3. **AST_Inspector**: Extrae información de funciones decoradas usando AST
   - Método: `find_tool_functions(tree)` - Encuentra funciones con decorador @tool
   - Método: `extract_function_info(func_node)` - Extrae información de una función

4. **Validation_Rules**: Conjunto de reglas que verifican docstrings y type hints
   - Método: `validate_docstring(func_info)` - Valida docstring
   - Método: `validate_parameter_hints(func_info)` - Valida type hints de parámetros
   - Método: `validate_return_hint(func_info)` - Valida type hint de retorno

5. **Console_Formatter**: Formatea y muestra advertencias en la consola
   - Método: `supports_color()` - Detecta soporte de colores ANSI
   - Método: `display_warnings(result)` - Muestra advertencias formateadas

### Modelos de Datos

- **Parameter_Info**: Información de un parámetro (nombre, type hint, es self/cls)
- **Function_Info**: Información de una función (nombre, docstring, parámetros, return hint, línea)
- **Validation_Error**: Error de validación (función, línea, tipo, mensaje)
- **Validation_Result**: Resultado completo (total funciones, funciones con errores, lista de errores)

## Cómo Ejecutar los Tests

### Ejecutar todos los tests

```bash
pytest test_tool_validator.py -v
```

### Ejecutar tests con cobertura

```bash
pytest test_tool_validator.py --cov=tool_validator --cov-report=term-missing
```

### Ejecutar solo property-based tests

```bash
pytest test_tool_validator.py -k "property" -v
```

### Ejecutar solo unit tests

```bash
pytest test_tool_validator.py -k "not property" -v
```

### Ejecutar tests de integración

```bash
pytest test_integration.py -v
```

## Manejo de Errores

El sistema implementa múltiples niveles de manejo de errores para garantizar que nunca bloquee el inicio del agente:

### Errores Manejados

1. **FileNotFoundError**: Si `tools.py` no existe, retorna resultado vacío sin mostrar mensaje
2. **SyntaxError**: Si `tools.py` tiene errores de sintaxis, retorna resultado vacío
3. **ImportError**: Si no se puede importar el módulo tools, retorna resultado vacío
4. **AttributeError**: Si un nodo AST no tiene un atributo esperado, usa valores por defecto
5. **Exception genérica**: Cualquier error inesperado se captura y muestra mensaje de advertencia

### Principios de Manejo de Errores

- **Fail-safe**: Ningún error de validación impide el inicio del agente
- **Informativo**: Todos los errores se registran en consola para debugging
- **Aislamiento**: Errores en una función no afectan validación de otras
- **Graceful degradation**: Si la validación falla completamente, el agente funciona normalmente

## Requisitos del Sistema

- Python 3.10 o superior (usa sintaxis de type hints con `|`)
- Módulos estándar: `ast`, `sys`, `os`, `dataclasses`
- Para tests: `pytest`, `hypothesis` (para property-based testing)

## Rendimiento

El sistema está diseñado para ser extremadamente rápido:

- **Objetivo**: < 500ms para archivos con 50 funciones @tool
- **Método**: Análisis estático usando AST (no ejecuta código)
- **Optimización**: Recorrido único del árbol AST, sin operaciones de I/O adicionales

## Limitaciones Conocidas

1. Solo valida funciones en el archivo `tools.py` (no busca en otros archivos)
2. Solo detecta decoradores con nombre exacto `tool` (no alias)
3. No valida la calidad del contenido de los docstrings (solo longitud mínima)
4. No valida la corrección de los type hints (solo su presencia)

## Extensibilidad

El sistema está diseñado para ser fácilmente extensible:

- **Agregar nuevas reglas**: Crear métodos en `Validation_Rules`
- **Validar otros archivos**: Modificar `Validation_Hook.run()` para llamar a `validate_tools_file()` con diferentes rutas
- **Personalizar formato**: Modificar `Console_Formatter.display_warnings()`
- **Agregar métricas**: Extender `Validation_Result` con nuevos campos

## Contribuir

Para contribuir al sistema de validación:

1. Asegúrate de que todos los tests pasen
2. Mantén cobertura de código >= 90%
3. Sigue el formato PEP 257 para docstrings
4. Agrega property-based tests para nuevas propiedades de corrección
5. Documenta cualquier cambio en este README
