# Documento de Diseño: Sistema de Validación de Herramientas @tool

## Overview

El sistema de validación de herramientas @tool es un mecanismo de análisis estático que inspecciona funciones decoradas con `@tool` en el archivo `tools.py` para verificar el cumplimiento de estándares de calidad de código. El sistema utiliza el módulo AST (Abstract Syntax Tree) de Python para analizar el código fuente sin ejecutarlo, validando la presencia y calidad de docstrings y type hints.

El sistema se ejecuta automáticamente al inicio del agente CloudArquitecto, antes de que comience a aceptar entrada del usuario. Las validaciones se completan en menos de 500ms para archivos con hasta 50 funciones, y los resultados se muestran como advertencias visuales en la consola sin bloquear el inicio del agente.

### Objetivos del Diseño

1. **No invasivo**: La validación no modifica el código ni interfiere con la ejecución normal del agente
2. **Rápido**: Análisis completo en < 500ms para 50 funciones
3. **Robusto**: Manejo de errores que permite al agente iniciar incluso si la validación falla
4. **Informativo**: Mensajes claros que identifican exactamente qué necesita corrección

## Architecture

El sistema sigue una arquitectura de pipeline lineal con tres etapas principales:

```
agent.py (inicio)
    ↓
Validation_Hook.run()
    ↓
Tool_Validator.validate_tools_file()
    ↓
AST Parser → Function Inspector → Validation Rules
    ↓
Validation_Result (lista de errores)
    ↓
Console_Formatter.display_warnings()
    ↓
agent.py (continúa ejecución normal)
```

### Componentes Principales

1. **Validation_Hook**: Punto de entrada que se invoca desde `agent.py`
2. **Tool_Validator**: Motor de validación que coordina el análisis AST
3. **AST_Inspector**: Extrae información de funciones decoradas usando AST
4. **Validation_Rules**: Conjunto de reglas que verifican docstrings y type hints
5. **Console_Formatter**: Formatea y muestra advertencias en la consola

### Flujo de Ejecución

1. `agent.py` importa y ejecuta `Validation_Hook.run()` al inicio
2. `Tool_Validator` lee y parsea `tools.py` usando `ast.parse()`
3. `AST_Inspector` recorre el árbol AST buscando decoradores `@tool`
4. Para cada función decorada, `Validation_Rules` verifica:
   - Existencia y longitud de docstring
   - Type hints en todos los parámetros (excepto self/cls)
   - Type hint de retorno
5. Los errores se acumulan en una estructura `Validation_Result`
6. `Console_Formatter` muestra advertencias con formato visual
7. El agente continúa su ejecución normal

## Components and Interfaces

### 1. Validation_Hook

**Responsabilidad**: Punto de entrada público para ejecutar la validación.

**Interface**:
```python
class Validation_Hook:
    @staticmethod
    def run() -> None:
        """
        Ejecuta la validación de herramientas @tool.
        
        Side effects:
            - Muestra advertencias en consola si hay errores
            - Captura y maneja cualquier excepción sin propagarla
        """
```

**Comportamiento**:
- Crea una instancia de `Tool_Validator`
- Invoca `validate_tools_file("tools.py")`
- Captura cualquier excepción y la registra sin propagarla
- Garantiza que el agente pueda iniciar incluso si la validación falla

### 2. Tool_Validator

**Responsabilidad**: Coordinar el análisis AST y la aplicación de reglas de validación.

**Interface**:
```python
class Tool_Validator:
    def __init__(self):
        """Inicializa el validador."""
        
    def validate_tools_file(self, filepath: str) -> Validation_Result:
        """
        Valida todas las funciones @tool en un archivo.
        
        Args:
            filepath: Ruta al archivo Python a validar
            
        Returns:
            Validation_Result con lista de errores encontrados
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            SyntaxError: Si el archivo contiene errores de sintaxis
        """
```

**Comportamiento**:
- Lee el contenido del archivo
- Parsea el código usando `ast.parse()`
- Identifica funciones decoradas con `@tool`
- Aplica reglas de validación a cada función
- Retorna resultado agregado

### 3. AST_Inspector

**Responsabilidad**: Extraer información de funciones usando el árbol AST.

**Interface**:
```python
class AST_Inspector:
    @staticmethod
    def find_tool_functions(tree: ast.Module) -> list[ast.FunctionDef]:
        """
        Encuentra todas las funciones decoradas con @tool.
        
        Args:
            tree: Árbol AST del módulo
            
        Returns:
            Lista de nodos FunctionDef decorados con @tool
        """
    
    @staticmethod
    def extract_function_info(func_node: ast.FunctionDef) -> Function_Info:
        """
        Extrae información relevante de un nodo de función.
        
        Args:
            func_node: Nodo AST de la función
            
        Returns:
            Function_Info con nombre, docstring, parámetros y type hints
        """
```

**Comportamiento**:
- Recorre el AST usando `ast.NodeVisitor` o `ast.walk()`
- Identifica decoradores comparando nombres
- Extrae docstrings desde `ast.get_docstring()`
- Extrae type hints desde `func_node.args` y `func_node.returns`

### 4. Validation_Rules

**Responsabilidad**: Aplicar reglas de validación específicas.

**Interface**:
```python
class Validation_Rules:
    @staticmethod
    def validate_docstring(func_info: Function_Info) -> list[str]:
        """
        Valida la presencia y calidad del docstring.
        
        Args:
            func_info: Información de la función
            
        Returns:
            Lista de mensajes de error (vacía si válido)
        """
    
    @staticmethod
    def validate_parameter_hints(func_info: Function_Info) -> list[str]:
        """
        Valida type hints en parámetros.
        
        Args:
            func_info: Información de la función
            
        Returns:
            Lista de mensajes de error (vacía si válido)
        """
    
    @staticmethod
    def validate_return_hint(func_info: Function_Info) -> list[str]:
        """
        Valida type hint de retorno.
        
        Args:
            func_info: Información de la función
            
        Returns:
            Lista de mensajes de error (vacía si válido)
        """
```

**Comportamiento**:
- Cada método retorna lista de strings con errores específicos
- Docstring: verifica existencia y longitud >= 10 caracteres
- Parámetros: verifica type hints, excluyendo 'self' y 'cls'
- Retorno: verifica presencia de type hint (None es válido)

### 5. Console_Formatter

**Responsabilidad**: Formatear y mostrar advertencias en la consola.

**Interface**:
```python
class Console_Formatter:
    @staticmethod
    def display_warnings(result: Validation_Result) -> None:
        """
        Muestra advertencias de validación en la consola.
        
        Args:
            result: Resultado de validación con errores
            
        Side effects:
            - Imprime en stdout con formato visual
            - Usa colores ANSI si el terminal los soporta
        """
    
    @staticmethod
    def supports_color() -> bool:
        """
        Detecta si el terminal soporta colores ANSI.
        
        Returns:
            True si soporta colores, False en caso contrario
        """
```

**Comportamiento**:
- Agrupa errores por función
- Usa emoji ⚠️ o texto "WARNING:" como prefijo
- Aplica colores amarillo/rojo si el terminal lo soporta
- Muestra resumen con total de funciones con errores
- Si no hay errores, muestra mensaje de éxito con ✅

## Data Models

### Function_Info

Estructura que encapsula información extraída de una función.

```python
@dataclass
class Function_Info:
    """Información extraída de una función @tool."""
    name: str
    docstring: str | None
    parameters: list[Parameter_Info]
    return_hint: str | None
    line_number: int
```

### Parameter_Info

Estructura que representa un parámetro de función.

```python
@dataclass
class Parameter_Info:
    """Información de un parámetro de función."""
    name: str
    type_hint: str | None
    is_self_or_cls: bool
```

### Validation_Error

Estructura que representa un error de validación.

```python
@dataclass
class Validation_Error:
    """Error de validación encontrado en una función."""
    function_name: str
    line_number: int
    error_type: str  # "docstring", "parameter_hint", "return_hint"
    message: str
```

### Validation_Result

Estructura que agrupa todos los resultados de validación.

```python
@dataclass
class Validation_Result:
    """Resultado completo de la validación."""
    total_functions: int
    functions_with_errors: int
    errors: list[Validation_Error]
    
    def has_errors(self) -> bool:
        """Retorna True si hay errores."""
        return len(self.errors) > 0
    
    def group_by_function(self) -> dict[str, list[Validation_Error]]:
        """Agrupa errores por nombre de función."""
        grouped = {}
        for error in self.errors:
            if error.function_name not in grouped:
                grouped[error.function_name] = []
            grouped[error.function_name].append(error)
        return grouped
```


### AST Inspection Algorithm

El algoritmo de inspección AST sigue estos pasos:

1. **Parse del archivo**: `ast.parse(source_code)` genera el árbol AST
2. **Búsqueda de funciones decoradas**:
   ```python
   for node in ast.walk(tree):
       if isinstance(node, ast.FunctionDef):
           for decorator in node.decorator_list:
               if is_tool_decorator(decorator):
                   # Procesar función
   ```
3. **Extracción de información**:
   - Nombre: `node.name`
   - Docstring: `ast.get_docstring(node)`
   - Parámetros: iterar sobre `node.args.args`
   - Type hints de parámetros: `arg.annotation`
   - Return type hint: `node.returns`
4. **Identificación de decorador @tool**:
   - Caso simple: `decorator.id == "tool"`
   - Caso con atributo: `decorator.attr == "tool"` (para `module.tool`)

### Error Handling Strategy

El sistema implementa múltiples niveles de manejo de errores:

**Nivel 1: Validation_Hook (más externo)**
- Captura todas las excepciones con `try-except` genérico
- Registra error en consola con formato: "⚠️ Error en validación: {mensaje}"
- Nunca propaga excepciones hacia `agent.py`

**Nivel 2: Tool_Validator**
- Maneja `FileNotFoundError`: muestra mensaje informativo, retorna resultado vacío
- Maneja `SyntaxError`: muestra error de parsing, retorna resultado vacío
- Maneja `ImportError`: muestra advertencia de importación, retorna resultado vacío

**Nivel 3: AST_Inspector**
- Maneja `AttributeError`: cuando un nodo AST no tiene atributo esperado
- Usa valores por defecto seguros (None, listas vacías)

**Nivel 4: Validation_Rules**
- No lanza excepciones, siempre retorna lista de errores (vacía si válido)
- Usa verificaciones defensivas con `getattr(obj, attr, default)`

### Console Output Format

**Formato cuando hay errores:**
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

**Formato cuando no hay errores:**
```
✅ Validación exitosa: 5 funciones @tool cumplen los estándares
```

**Colores ANSI (si el terminal los soporta):**
- Encabezado: Amarillo (`\033[93m`)
- Errores: Rojo (`\033[91m`)
- Éxito: Verde (`\033[92m`)
- Reset: `\033[0m`

## Correctness Properties

*Una propiedad (property) es una característica o comportamiento que debe cumplirse en todas las ejecuciones válidas de un sistema - esencialmente, una declaración formal sobre lo que el sistema debe hacer. Las propiedades sirven como puente entre especificaciones legibles por humanos y garantías de corrección verificables por máquinas.*

### Property 1: Detección de docstrings faltantes o insuficientes

*Para cualquier* función decorada con @tool, si la función carece de docstring o tiene un docstring con menos de 10 caracteres, entonces el validador debe registrar un error de validación que incluya el nombre de la función.

**Validates: Requirements 1.1, 1.2, 1.3, 1.4**

### Property 2: Detección de type hints faltantes en parámetros

*Para cualquier* función decorada con @tool y cualquier parámetro de esa función (excluyendo 'self' y 'cls'), si el parámetro carece de type hint, entonces el validador debe registrar un error de validación que incluya el nombre de la función y el nombre del parámetro.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

### Property 3: Detección de return type hint faltante

*Para cualquier* función decorada con @tool, si la función carece de type hint de retorno, entonces el validador debe registrar un error de validación que incluya el nombre de la función. Funciones con return type hint de `None` son consideradas válidas.

**Validates: Requirements 3.1, 3.2, 3.3**

### Property 4: Identificación completa de funciones @tool

*Para cualquier* archivo Python válido que contenga funciones decoradas con @tool, el validador debe identificar todas las funciones decoradas, sin omitir ninguna ni incluir funciones no decoradas.

**Validates: Requirements 4.2**

### Property 5: Formato de mensajes de error

*Para cualquier* error de validación, el mensaje de error formateado debe contener: (1) el nombre de la función, (2) el tipo específico de error ("Missing docstring", "Parameter 'X' missing type hint", o "Missing return type hint"), y (3) el número de línea donde se encuentra la función.

**Validates: Requirements 5.2, 5.3, 5.4, 5.5**

### Property 6: Agrupación de errores por función

*Para cualquier* conjunto de errores de validación, cuando se formatean para mostrar en consola, todos los errores pertenecientes a la misma función deben aparecer agrupados bajo el nombre de esa función.

**Validates: Requirements 7.2**

### Property 7: Presencia de resumen en salida

*Para cualquier* resultado de validación que contenga errores, la salida formateada debe incluir una línea de resumen que indique el número total de funciones con errores y el número total de funciones analizadas.

**Validates: Requirements 7.3**

### Property 8: Separador visual en advertencias

*Para cualquier* salida de advertencias de validación, el texto formateado debe contener un separador visual distintivo (emoji ⚠️ o texto "WARNING:") al inicio.

**Validates: Requirements 7.1**

## Error Handling

### Categorías de Errores

**1. Errores de Archivo**
- **FileNotFoundError**: `tools.py` no existe
  - Acción: Mostrar mensaje informativo, retornar resultado vacío
  - Mensaje: "ℹ️  Archivo tools.py no encontrado. Omitiendo validación."
  - No bloquea inicio del agente

**2. Errores de Sintaxis**
- **SyntaxError**: `tools.py` contiene código Python inválido
  - Acción: Mostrar error de parsing, retornar resultado vacío
  - Mensaje: "⚠️  Error de sintaxis en tools.py: {detalle}"
  - No bloquea inicio del agente

**3. Errores de Importación**
- **ImportError**: No se puede importar el módulo tools
  - Acción: Mostrar advertencia, retornar resultado vacío
  - Mensaje: "⚠️  No se pudo importar tools: {detalle}"
  - No bloquea inicio del agente

**4. Errores de Atributos**
- **AttributeError**: Nodo AST no tiene atributo esperado
  - Acción: Usar valor por defecto, continuar validación
  - Logging interno, no visible al usuario
  - No afecta otras funciones

**5. Errores Inesperados**
- **Exception**: Cualquier otro error no anticipado
  - Acción: Capturar en Validation_Hook, mostrar mensaje genérico
  - Mensaje: "⚠️  Error inesperado en validación: {tipo}: {mensaje}"
  - No bloquea inicio del agente

### Principios de Manejo de Errores

1. **Fail-safe**: Ningún error de validación debe impedir el inicio del agente
2. **Informativo**: Todos los errores se registran en consola para debugging
3. **Aislamiento**: Errores en una función no afectan validación de otras
4. **Graceful degradation**: Si la validación falla completamente, el agente funciona normalmente

## Testing Strategy

### Enfoque Dual de Testing

El sistema requiere dos tipos complementarios de pruebas:

**Unit Tests**: Verifican ejemplos específicos, casos edge y condiciones de error
- Ejemplos concretos de funciones válidas e inválidas
- Casos edge: funciones sin parámetros, solo con self/cls, etc.
- Manejo de errores: archivos inexistentes, sintaxis inválida

**Property-Based Tests**: Verifican propiedades universales a través de múltiples inputs generados
- Generación aleatoria de definiciones de funciones
- Cobertura exhaustiva de combinaciones de parámetros
- Validación de invariantes del sistema

### Configuración de Property-Based Testing

**Librería**: `hypothesis` (Python)

**Configuración**:
- Mínimo 100 iteraciones por test de propiedad
- Cada test debe referenciar su propiedad en el documento de diseño
- Formato de tag: `# Feature: tool-validation-hook, Property {N}: {texto}`

**Estrategias de Generación**:
- Funciones con/sin docstrings de longitudes variadas
- Parámetros con/sin type hints
- Combinaciones de self/cls con otros parámetros
- Return type hints presentes/ausentes/None

### Unit Tests Específicos

**Test Suite 1: AST Parsing**
- Test: Parsear archivo válido con funciones @tool
- Test: Manejar archivo inexistente
- Test: Manejar archivo con errores de sintaxis

**Test Suite 2: Detección de Decoradores**
- Test: Identificar @tool simple
- Test: Identificar @tool con módulo (e.g., `strands.tool`)
- Test: Ignorar funciones sin decorador
- Test: Ignorar funciones con otros decoradores

**Test Suite 3: Validación de Docstrings**
- Test: Función sin docstring genera error
- Test: Docstring < 10 caracteres genera error
- Test: Docstring >= 10 caracteres es válido
- Test: Docstring None genera error

**Test Suite 4: Validación de Type Hints**
- Test: Parámetro sin type hint genera error
- Test: Parámetro 'self' sin type hint no genera error
- Test: Parámetro 'cls' sin type hint no genera error
- Test: Función sin return type hint genera error
- Test: Función con return type hint None es válida

**Test Suite 5: Formato de Salida**
- Test: Salida sin errores muestra mensaje de éxito
- Test: Salida con errores muestra separador visual
- Test: Errores agrupados por función
- Test: Resumen incluye conteo de funciones con errores

**Test Suite 6: Manejo de Errores**
- Test: ImportError no propaga excepción
- Test: AttributeError no propaga excepción
- Test: Validation_Hook captura todas las excepciones

### Property-Based Tests

**Property Test 1**: Detección de docstrings
```python
# Feature: tool-validation-hook, Property 1: Para cualquier función @tool sin docstring o con docstring < 10 chars, el validador registra error con nombre de función
@given(function_definition=st.builds(generate_function, has_docstring=st.booleans(), docstring_length=st.integers(0, 20)))
@settings(max_examples=100)
def test_docstring_detection_property(function_definition):
    # Test implementation
```

**Property Test 2**: Detección de type hints en parámetros
```python
# Feature: tool-validation-hook, Property 2: Para cualquier parámetro (excepto self/cls) sin type hint, el validador registra error con nombres de función y parámetro
@given(function_definition=st.builds(generate_function_with_params, param_count=st.integers(0, 10), hint_probability=st.floats(0, 1)))
@settings(max_examples=100)
def test_parameter_hints_property(function_definition):
    # Test implementation
```

**Property Test 3**: Detección de return type hint
```python
# Feature: tool-validation-hook, Property 3: Para cualquier función @tool sin return type hint, el validador registra error (None es válido)
@given(function_definition=st.builds(generate_function, has_return_hint=st.booleans(), return_hint_is_none=st.booleans()))
@settings(max_examples=100)
def test_return_hint_property(function_definition):
    # Test implementation
```

**Property Test 4**: Identificación completa de funciones @tool
```python
# Feature: tool-validation-hook, Property 4: Para cualquier archivo Python válido, el validador identifica todas las funciones @tool sin omisiones ni falsos positivos
@given(module_code=st.builds(generate_module, tool_function_count=st.integers(0, 20), other_function_count=st.integers(0, 20)))
@settings(max_examples=100)
def test_complete_identification_property(module_code):
    # Test implementation
```

**Property Test 5**: Formato de mensajes de error
```python
# Feature: tool-validation-hook, Property 5: Para cualquier error, el mensaje contiene nombre de función, tipo de error específico, y número de línea
@given(validation_errors=st.lists(st.builds(generate_validation_error)))
@settings(max_examples=100)
def test_error_message_format_property(validation_errors):
    # Test implementation
```

**Property Test 6**: Agrupación de errores
```python
# Feature: tool-validation-hook, Property 6: Para cualquier conjunto de errores, los errores de la misma función aparecen agrupados
@given(validation_errors=st.lists(st.builds(generate_validation_error), min_size=1))
@settings(max_examples=100)
def test_error_grouping_property(validation_errors):
    # Test implementation
```

**Property Test 7**: Presencia de resumen
```python
# Feature: tool-validation-hook, Property 7: Para cualquier resultado con errores, la salida incluye resumen con conteos
@given(validation_result=st.builds(generate_validation_result, has_errors=st.just(True)))
@settings(max_examples=100)
def test_summary_presence_property(validation_result):
    # Test implementation
```

**Property Test 8**: Separador visual
```python
# Feature: tool-validation-hook, Property 8: Para cualquier salida de advertencias, el texto contiene separador visual distintivo
@given(validation_result=st.builds(generate_validation_result, has_errors=st.just(True)))
@settings(max_examples=100)
def test_visual_separator_property(validation_result):
    # Test implementation
```

### Métricas de Cobertura

**Objetivos**:
- Cobertura de líneas: >= 90%
- Cobertura de ramas: >= 85%
- Todas las propiedades implementadas con property-based tests
- Todos los casos edge cubiertos con unit tests

### Integración con CI/CD

- Tests ejecutados automáticamente en cada commit
- Property-based tests con seed fijo para reproducibilidad
- Timeout de 30 segundos para suite completa de tests
- Fallos en tests bloquean merge a rama principal
