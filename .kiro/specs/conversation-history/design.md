# Design Document: Conversation History

## Overview

Este diseño implementa la funcionalidad de persistencia del historial de conversación para el agente CloudArquitecto. El sistema captura automáticamente cada interacción usuario-agente y la almacena en un archivo JSON estructurado, permitiendo mantener un registro completo de las consultas realizadas.

La solución se integra de manera no invasiva en el flujo existente del agente, agregando capacidades de persistencia sin modificar la lógica core de procesamiento. El diseño prioriza la resiliencia: los errores de persistencia no deben interrumpir el funcionamiento del agente.

### Objetivos de Diseño

1. **Integración transparente**: El History_Manager se integra en el bucle existente sin modificar la lógica del agente
2. **Resiliencia**: Los errores de I/O no interrumpen el flujo de conversación
3. **Simplicidad**: Uso de JSON estándar sin dependencias externas
4. **Legibilidad**: Formato JSON indentado para facilitar inspección manual

## Architecture

### Componentes Principales

```
┌─────────────────────────────────────────────────────────┐
│                      agent.py                           │
│                                                         │
│  ┌──────────────┐         ┌─────────────────────┐     │
│  │   Startup    │────────▶│  History_Manager    │     │
│  │              │         │  .load_history()    │     │
│  └──────────────┘         └─────────────────────┘     │
│                                    │                    │
│                                    ▼                    │
│  ┌──────────────┐         ┌─────────────────────┐     │
│  │ Conversation │────────▶│  Display Summary    │     │
│  │     Loop     │         └─────────────────────┘     │
│  │              │                                       │
│  │  user_input  │                                       │
│  │      │       │                                       │
│  │      ▼       │                                       │
│  │   agent()    │                                       │
│  │      │       │                                       │
│  │      ▼       │         ┌─────────────────────┐     │
│  │  respuesta   │────────▶│  History_Manager    │     │
│  │              │         │  .save_entry()      │     │
│  └──────────────┘         └─────────────────────┘     │
│                                    │                    │
└────────────────────────────────────┼────────────────────┘
                                     ▼
                          ┌─────────────────────┐
                          │  historial.json     │
                          │                     │
                          │  [                  │
                          │    {                │
                          │      "timestamp",   │
                          │      "pregunta",    │
                          │      "respuesta"    │
                          │    },               │
                          │    ...              │
                          │  ]                  │
                          └─────────────────────┘
```

### Flujo de Integración

**Al inicio del agente:**
1. Crear instancia de History_Manager
2. Llamar a `load_history()` para cargar historial existente
3. Mostrar resumen al usuario (número de conversaciones, fecha más reciente)

**En cada iteración del bucle:**
1. Usuario ingresa pregunta
2. Agente procesa y genera respuesta
3. Llamar a `save_entry(pregunta, respuesta)` para persistir
4. Continuar con siguiente iteración

**Manejo de errores:**
- Todos los errores de I/O se capturan y registran
- El agente continúa operando normalmente
- Se muestra advertencia al usuario pero no se interrumpe el flujo

## Components and Interfaces

### History_Manager Class

Componente central responsable de todas las operaciones de persistencia del historial.

```python
class History_Manager:
    """
    Gestiona la persistencia del historial de conversación.
    
    Attributes:
        history_file (str): Ruta al archivo JSON de historial
        history (list): Lista de entradas de conversación en memoria
    """
    
    def __init__(self, history_file: str = "historial.json"):
        """
        Inicializa el gestor de historial.
        
        Args:
            history_file: Nombre del archivo JSON (default: "historial.json")
        """
        pass
    
    def load_history(self) -> dict:
        """
        Carga el historial desde el archivo JSON.
        
        Returns:
            dict con:
                - success (bool): True si carga exitosa
                - count (int): Número de conversaciones cargadas
                - last_date (str): Fecha de última conversación (ISO 8601)
                - message (str): Mensaje descriptivo para mostrar al usuario
        
        Side effects:
            - Carga self.history con las entradas del archivo
            - Crea archivo vacío si no existe
            - Muestra mensaje en consola
        """
        pass
    
    def save_entry(self, pregunta: str, respuesta: str) -> bool:
        """
        Guarda una nueva entrada de conversación.
        
        Args:
            pregunta: Texto de la pregunta del usuario
            respuesta: Texto de la respuesta del agente
        
        Returns:
            bool: True si guardado exitoso, False si hubo error
        
        Side effects:
            - Agrega entrada a self.history
            - Escribe archivo JSON actualizado
            - Muestra advertencia en consola si hay error
        """
        pass
    
    def _create_entry(self, pregunta: str, respuesta: str) -> dict:
        """
        Crea un objeto Conversation_Entry.
        
        Args:
            pregunta: Texto de la pregunta
            respuesta: Texto de la respuesta
        
        Returns:
            dict con estructura: {
                "timestamp": str (ISO 8601),
                "pregunta": str,
                "respuesta": str
            }
        """
        pass
    
    def _write_history(self) -> bool:
        """
        Escribe self.history al archivo JSON.
        
        Returns:
            bool: True si escritura exitosa, False si error
        
        Side effects:
            - Escribe archivo con encoding UTF-8
            - Usa indentación de 2 espacios
        """
        pass
```

### Integration Points

**Modificaciones en agent.py:**

```python
# Después de inicializar el agente, antes del bucle
from history_manager import History_Manager

history_mgr = History_Manager()
summary = history_mgr.load_history()
print(summary["message"])

# Dentro del bucle, después de recibir respuesta
try:
    respuesta = agent(user_input)
    print(f"\nCloudArquitecto: {respuesta}\n")
    
    # Guardar en historial
    history_mgr.save_entry(user_input, respuesta)
    
except Exception as e:
    print(f"\nOcurrio un detalle tecnico: {e}")
    print("Revisa la conexion con AWS.\n")
```

## Data Models

### Conversation_Entry

Estructura de datos que representa una interacción individual.

```python
{
    "timestamp": "2024-01-15T14:30:45.123456",  # ISO 8601 format
    "pregunta": "¿Cómo estimar costos de Lambda?",
    "respuesta": "Para estimar costos de Lambda..."
}
```

**Campos:**
- `timestamp` (str, obligatorio): Marca temporal en formato ISO 8601 con microsegundos
- `pregunta` (str, obligatorio): Texto completo de la pregunta del usuario
- `respuesta` (str, obligatorio): Texto completo de la respuesta del agente

### History_File Structure

El archivo `historial.json` contiene un array JSON de objetos Conversation_Entry.

```json
[
  {
    "timestamp": "2024-01-15T14:30:45.123456",
    "pregunta": "¿Qué es Lambda?",
    "respuesta": "AWS Lambda es un servicio de cómputo serverless..."
  },
  {
    "timestamp": "2024-01-15T14:32:10.789012",
    "pregunta": "¿Cómo funciona DynamoDB?",
    "respuesta": "DynamoDB es una base de datos NoSQL..."
  }
]
```

**Características:**
- Encoding: UTF-8
- Indentación: 2 espacios
- Orden: Cronológico (más antiguas primero)
- Tamaño: Sin límite (crece indefinidamente)

### Summary Response

Estructura retornada por `load_history()` para mostrar al usuario.

```python
{
    "success": True,
    "count": 42,
    "last_date": "2024-01-15T14:32:10.789012",
    "message": "📚 Historial cargado: 42 conversaciones. Última: 2024-01-15 14:32"
}
```

**Casos especiales:**

Primera sesión (archivo no existe):
```python
{
    "success": True,
    "count": 0,
    "last_date": None,
    "message": "🆕 Primera sesión. Se creará un nuevo historial."
}
```

Archivo corrupto:
```python
{
    "success": False,
    "count": 0,
    "last_date": None,
    "message": "⚠️  Historial corrupto. Se creará uno nuevo."
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Round-trip Persistence

*For any* pregunta and respuesta strings, if we call `save_entry(pregunta, respuesta)` and then load the history file, the loaded history should contain an entry with exactly the same pregunta and respuesta texts.

**Validates: Requirements 1.2, 1.5, 1.6**

### Property 2: ISO 8601 Timestamp Format

*For any* conversation entry created by the History_Manager, the timestamp field should be a valid ISO 8601 formatted string matching the pattern `YYYY-MM-DDTHH:MM:SS.ffffff`.

**Validates: Requirements 1.4, 3.3**

### Property 3: Entry Structure Completeness

*For any* entry in the history file, it should contain exactly three fields: "timestamp" (string), "pregunta" (string), and "respuesta" (string), with no missing or extra fields.

**Validates: Requirements 3.2, 3.6**

### Property 4: History Preservation on Append

*For any* existing history with N entries, after calling `save_entry()` to add a new entry, the history file should contain N+1 entries, and all original N entries should remain unchanged in content and order.

**Validates: Requirements 1.8**

### Property 5: Summary Accuracy

*For any* history file with N entries, calling `load_history()` should return a summary where:
- `count` equals N
- `last_date` equals the timestamp of the Nth entry (if N > 0)
- `success` is True (if file is valid JSON)

**Validates: Requirements 2.2, 2.3, 2.4**

### Property 6: UTF-8 Character Preservation

*For any* pregunta or respuesta containing UTF-8 characters (including emojis, accents, and special symbols), after saving and loading, the text should be identical to the original with no character corruption or encoding errors.

**Validates: Requirements 3.4**

### Property 7: Error Resilience

*For any* I/O error during `save_entry()` or `load_history()`, the method should:
- Return a failure indicator (False or error status)
- Log an error message to console
- Not raise an unhandled exception that would crash the agent

**Validates: Requirements 4.1, 4.2, 4.3, 4.5**

## Error Handling

### Error Categories

**1. File Not Found (Primera sesión)**
- **Situación**: `historial.json` no existe
- **Comportamiento**: 
  - `load_history()` crea un archivo vacío `[]`
  - Retorna summary con `count=0` y mensaje de primera sesión
  - No se considera error, es flujo normal
- **Código de ejemplo**:
```python
if not os.path.exists(self.history_file):
    self.history = []
    self._write_history()  # Crea archivo vacío
    return {
        "success": True,
        "count": 0,
        "last_date": None,
        "message": "🆕 Primera sesión. Se creará un nuevo historial."
    }
```

**2. JSON Corrupto**
- **Situación**: Archivo existe pero no es JSON válido
- **Comportamiento**:
  - Capturar `json.JSONDecodeError`
  - Mostrar advertencia al usuario
  - Crear nuevo archivo vacío (sobrescribir corrupto)
  - Continuar con historial vacío
- **Código de ejemplo**:
```python
try:
    with open(self.history_file, 'r', encoding='utf-8') as f:
        self.history = json.load(f)
except json.JSONDecodeError:
    print("⚠️  Historial corrupto. Se creará uno nuevo.")
    self.history = []
    self._write_history()
    return {"success": False, "count": 0, "last_date": None, ...}
```

**3. Error de Lectura (Permisos)**
- **Situación**: No se puede leer el archivo por permisos u otro error de I/O
- **Comportamiento**:
  - Capturar `IOError` o `PermissionError`
  - Mostrar advertencia específica
  - Continuar con historial vacío en memoria
  - No intentar crear archivo nuevo
- **Código de ejemplo**:
```python
except (IOError, PermissionError) as e:
    print(f"⚠️  No se pudo leer historial: {e}")
    self.history = []
    return {"success": False, "count": 0, ...}
```

**4. Error de Escritura**
- **Situación**: No se puede escribir al archivo (disco lleno, permisos, etc.)
- **Comportamiento**:
  - Capturar excepción en `save_entry()`
  - Mostrar advertencia al usuario
  - Retornar `False` para indicar fallo
  - Mantener entrada en memoria (self.history)
  - Intentar guardar siguiente entrada normalmente
- **Código de ejemplo**:
```python
def save_entry(self, pregunta: str, respuesta: str) -> bool:
    entry = self._create_entry(pregunta, respuesta)
    self.history.append(entry)
    
    try:
        return self._write_history()
    except (IOError, PermissionError) as e:
        print(f"⚠️  No se pudo guardar en historial: {e}")
        return False
```

### Error Handling Principles

1. **No interrumpir el agente**: Ningún error de persistencia debe detener el bucle de conversación
2. **Fail gracefully**: Mostrar advertencias claras pero continuar operando
3. **Preservar en memoria**: Aunque falle escritura, mantener historial en memoria durante la sesión
4. **Reintentar implícitamente**: Cada `save_entry()` es un nuevo intento independiente
5. **Logging visible**: Todos los errores se muestran en consola para debugging

### Edge Cases

**Archivo vacío vs archivo con array vacío:**
- Archivo vacío (0 bytes): Tratado como JSON corrupto, se recrea
- Archivo con `[]`: Válido, historial vacío legítimo

**Timestamps duplicados:**
- Permitidos (dos conversaciones en el mismo microsegundo son posibles)
- No se valida unicidad de timestamps

**Entradas con campos extra:**
- Al cargar: Se aceptan, no se validan campos extra
- Al guardar: Solo se escriben los tres campos estándar

**Textos muy largos:**
- No hay límite de tamaño para pregunta/respuesta
- JSON puede crecer indefinidamente
- Responsabilidad del usuario gestionar tamaño del archivo

## Testing Strategy

### Dual Testing Approach

La estrategia de testing combina pruebas unitarias para casos específicos y pruebas basadas en propiedades para validación exhaustiva:

**Unit Tests**: Verifican ejemplos concretos, casos edge y condiciones de error
**Property Tests**: Verifican propiedades universales a través de múltiples inputs generados

Ambos tipos de pruebas son complementarios y necesarios para cobertura completa.

### Property-Based Testing

**Framework**: Utilizaremos `hypothesis` para Python, la librería estándar para property-based testing.

**Configuración**:
- Mínimo 100 iteraciones por test (configurado con `@settings(max_examples=100)`)
- Cada test debe referenciar su propiedad del diseño mediante comentario
- Formato de tag: `# Feature: conversation-history, Property {N}: {descripción}`

**Estrategia de generación**:
```python
from hypothesis import given, strategies as st

# Generadores personalizados
@st.composite
def conversation_entry(draw):
    """Genera entradas de conversación válidas."""
    pregunta = draw(st.text(min_size=1, max_size=500))
    respuesta = draw(st.text(min_size=1, max_size=2000))
    return pregunta, respuesta

@st.composite
def history_list(draw):
    """Genera listas de historial con múltiples entradas."""
    n = draw(st.integers(min_value=0, max_value=50))
    entries = [draw(conversation_entry()) for _ in range(n)]
    return entries
```

**Tests de propiedades**:

1. **Property 1: Round-trip Persistence**
```python
# Feature: conversation-history, Property 1: Round-trip Persistence
@given(pregunta=st.text(min_size=1), respuesta=st.text(min_size=1))
@settings(max_examples=100)
def test_roundtrip_persistence(pregunta, respuesta):
    """Guardar y cargar debe preservar pregunta y respuesta exactamente."""
    mgr = History_Manager("test_history.json")
    mgr.save_entry(pregunta, respuesta)
    
    # Cargar desde archivo
    loaded = mgr.load_history()
    last_entry = mgr.history[-1]
    
    assert last_entry["pregunta"] == pregunta
    assert last_entry["respuesta"] == respuesta
```

2. **Property 2: ISO 8601 Timestamp Format**
```python
# Feature: conversation-history, Property 2: ISO 8601 Timestamp Format
@given(pregunta=st.text(), respuesta=st.text())
@settings(max_examples=100)
def test_timestamp_format(pregunta, respuesta):
    """Todos los timestamps deben ser ISO 8601 válidos."""
    mgr = History_Manager()
    entry = mgr._create_entry(pregunta, respuesta)
    
    # Validar formato ISO 8601
    timestamp = entry["timestamp"]
    datetime.fromisoformat(timestamp)  # Debe parsear sin error
    assert re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}', timestamp)
```

3. **Property 4: History Preservation on Append**
```python
# Feature: conversation-history, Property 4: History Preservation on Append
@given(initial_history=history_list(), new_entry=conversation_entry())
@settings(max_examples=100)
def test_history_preservation(initial_history, new_entry):
    """Agregar entrada no debe modificar entradas existentes."""
    mgr = History_Manager("test_history.json")
    
    # Crear historial inicial
    for p, r in initial_history:
        mgr.save_entry(p, r)
    
    initial_count = len(mgr.history)
    initial_entries = mgr.history.copy()
    
    # Agregar nueva entrada
    mgr.save_entry(new_entry[0], new_entry[1])
    
    # Verificar preservación
    assert len(mgr.history) == initial_count + 1
    assert mgr.history[:initial_count] == initial_entries
```

### Unit Testing

**Framework**: `pytest` para estructura de tests y fixtures

**Casos específicos a testear**:

1. **Primera sesión (archivo no existe)**
```python
def test_first_session():
    """Primera sesión debe crear archivo y mostrar mensaje apropiado."""
    if os.path.exists("historial.json"):
        os.remove("historial.json")
    
    mgr = History_Manager()
    summary = mgr.load_history()
    
    assert summary["success"] == True
    assert summary["count"] == 0
    assert summary["last_date"] is None
    assert "Primera sesión" in summary["message"]
    assert os.path.exists("historial.json")
```

2. **Archivo JSON corrupto**
```python
def test_corrupted_json():
    """Archivo corrupto debe manejarse sin crash."""
    with open("historial.json", "w") as f:
        f.write("{invalid json content")
    
    mgr = History_Manager()
    summary = mgr.load_history()
    
    assert summary["success"] == False
    assert summary["count"] == 0
    assert "corrupto" in summary["message"].lower()
```

3. **Indentación de 2 espacios**
```python
def test_json_indentation():
    """Archivo debe usar indentación de 2 espacios."""
    mgr = History_Manager()
    mgr.save_entry("test", "response")
    
    with open("historial.json", "r") as f:
        content = f.read()
    
    # Verificar que hay indentación de 2 espacios
    assert '  {' in content  # 2 espacios antes de {
    assert '    "timestamp"' in content  # 4 espacios para campos
```

4. **Caracteres UTF-8 especiales**
```python
def test_utf8_characters():
    """Caracteres especiales deben preservarse."""
    mgr = History_Manager()
    pregunta = "¿Cómo funciona λ en AWS? 🚀"
    respuesta = "AWS Lambda (λ) es serverless 💻"
    
    mgr.save_entry(pregunta, respuesta)
    mgr.load_history()
    
    last = mgr.history[-1]
    assert last["pregunta"] == pregunta
    assert last["respuesta"] == respuesta
```

5. **Error de escritura (permisos)**
```python
def test_write_permission_error(monkeypatch):
    """Error de escritura no debe crashear el agente."""
    mgr = History_Manager()
    
    # Simular error de permisos
    def mock_write(*args, **kwargs):
        raise PermissionError("No write permission")
    
    monkeypatch.setattr("builtins.open", mock_write)
    
    result = mgr.save_entry("test", "response")
    assert result == False  # Indica fallo pero no crash
```

### Integration Testing

**Test de integración completo**:
```python
def test_full_agent_integration():
    """Test de integración: agente + historial en flujo completo."""
    # Simular sesión completa
    mgr = History_Manager("integration_test.json")
    
    # Primera sesión
    summary = mgr.load_history()
    assert summary["count"] == 0
    
    # Simular 3 conversaciones
    conversations = [
        ("¿Qué es S3?", "S3 es almacenamiento de objetos..."),
        ("¿Cómo funciona Lambda?", "Lambda es serverless..."),
        ("¿Cuánto cuesta?", "Depende del uso...")
    ]
    
    for p, r in conversations:
        mgr.save_entry(p, r)
    
    # Segunda sesión: cargar historial
    mgr2 = History_Manager("integration_test.json")
    summary2 = mgr2.load_history()
    
    assert summary2["count"] == 3
    assert len(mgr2.history) == 3
    assert mgr2.history[0]["pregunta"] == "¿Qué es S3?"
```

### Test Coverage Goals

- **Line coverage**: Mínimo 90%
- **Branch coverage**: Mínimo 85%
- **Property tests**: 7 propiedades × 100 iteraciones = 700 casos generados
- **Unit tests**: ~15 tests para casos específicos y edge cases
- **Integration tests**: 2-3 tests de flujo completo

### Continuous Testing

**Pre-commit hooks**:
```bash
# Ejecutar tests antes de cada commit
pytest tests/ --cov=history_manager --cov-report=term-missing
```

**CI/CD Pipeline**:
```yaml
# GitHub Actions / GitLab CI
test:
  script:
    - pip install pytest hypothesis pytest-cov
    - pytest tests/ --cov=history_manager --cov-report=xml
    - pytest tests/property_tests/ --hypothesis-show-statistics
```
