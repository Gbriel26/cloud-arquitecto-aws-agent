# Design Document: Output Hook Formatter

## Overview

El sistema Output Hook Formatter proporciona una funcionalidad de formateo automático para las respuestas del agente CloudArquitecto. La solución implementa un mecanismo de hook de salida que intercepta todas las respuestas generadas por el agente y añade una firma consistente al final de cada una.

### Objetivos del Diseño

- Implementar una función de formateo simple y eficiente que añada una firma a las respuestas
- Integrar el formateo de manera transparente en el flujo de respuestas del agente
- Garantizar robustez mediante validación de tipos y manejo de casos edge
- Mantener la simplicidad y facilidad de mantenimiento del código

### Alcance

Este diseño cubre:
- La función `formatear_respuesta` que realiza el formateo de texto
- La integración con el sistema de output_hooks del agente Strands
- El manejo de tipos y validación de entrada
- La organización del código en el archivo agent.py

Este diseño NO cubre:
- Modificación del contenido de las respuestas más allá de añadir la firma
- Formateo condicional basado en el tipo de respuesta
- Configuración dinámica de la firma
- Múltiples hooks de salida

## Architecture

### Arquitectura General

El sistema sigue un patrón de interceptor (Interceptor Pattern) donde la función de formateo actúa como un middleware que procesa las respuestas antes de su entrega final.

```
┌─────────────┐
│   Agent     │
│   (Strands) │
└──────┬──────┘
       │
       │ Genera respuesta
       ▼
┌─────────────────────┐
│  output_hooks       │
│  [formatear_        │
│   respuesta]        │
└──────┬──────────────┘
       │
       │ Aplica formateo
       ▼
┌─────────────────────┐
│  formatear_         │
│  respuesta()        │
│                     │
│  input: str         │
│  output: str +      │
│          signature  │
└──────┬──────────────┘
       │
       │ Retorna texto formateado
       ▼
┌─────────────────────┐
│  Usuario            │
└─────────────────────┘
```

### Flujo de Datos

1. El agente genera una respuesta (Response_Text)
2. El sistema de hooks de Strands invoca automáticamente `formatear_respuesta`
3. La función valida el tipo de entrada
4. La función concatena el Response_Text con la Signature
5. La función retorna el Formatted_Response
6. El agente entrega el Formatted_Response al usuario

### Decisiones de Arquitectura

**Decisión 1: Usar output_hooks en lugar de modificar el agente directamente**
- Razón: Mantiene la separación de responsabilidades y permite añadir/remover el formateo sin modificar la lógica del agente
- Alternativa considerada: Modificar el método de respuesta del agente
- Trade-off: Dependencia del sistema de hooks de Strands, pero mayor flexibilidad

**Decisión 2: Validación de tipos en runtime**
- Razón: Python es dinámicamente tipado; la validación explícita previene errores sutiles
- Alternativa considerada: Confiar solo en type hints
- Trade-off: Pequeño overhead de performance, pero mayor robustez

## Components and Interfaces

### Component 1: formatear_respuesta Function

**Responsabilidad:** Transformar el texto de respuesta añadiendo la firma del agente.

**Interface:**
```python
def formatear_respuesta(output_text: str) -> str:
    """
    Formatea el texto de salida del agente añadiendo una firma al final.
    
    Args:
        output_text: El texto de respuesta generado por el agente
        
    Returns:
        El texto de respuesta con la firma añadida
        
    Raises:
        TypeError: Si output_text no es de tipo str
    """
```

**Comportamiento:**
- Valida que `output_text` sea de tipo `str`
- Si no es string, lanza `TypeError` con mensaje descriptivo
- Concatena `output_text` con la constante SIGNATURE
- Retorna el texto formateado

**Constantes:**
```python
SIGNATURE = "\n\n--- *Respuesta generada por CloudArquitecto*"
```

### Component 2: Agent Configuration

**Responsabilidad:** Configurar el agente para usar el output hook.

**Interface:**
```python
agent = Agent(
    # ... otros parámetros ...
    output_hooks=[formatear_respuesta]
)
```

**Comportamiento:**
- El agente recibe la lista de output_hooks en su inicialización
- Aplica cada hook en orden a las respuestas generadas
- Mantiene toda la funcionalidad existente del agente

### Interacciones entre Componentes

1. **Agent → formatear_respuesta**
   - El agente invoca la función automáticamente después de generar cada respuesta
   - Pasa el texto de respuesta como argumento
   - Recibe el texto formateado como resultado

2. **formatear_respuesta → Agent**
   - La función no tiene dependencias del agente
   - Es una función pura que solo transforma strings
   - Puede ser testeada independientemente

## Data Models

### Input Data Model

**Response_Text (str)**
- Tipo: `str`
- Descripción: Texto de respuesta generado por el agente antes del formateo
- Restricciones: Debe ser de tipo string (validado en runtime)
- Ejemplos válidos:
  - `"Hola, ¿cómo puedo ayudarte?"`
  - `""`
  - `"Línea 1\nLínea 2\nLínea 3"`
- Ejemplos inválidos:
  - `None` (TypeError)
  - `123` (TypeError)
  - `["texto"]` (TypeError)

### Output Data Model

**Formatted_Response (str)**
- Tipo: `str`
- Descripción: Texto de respuesta con la firma añadida
- Formato: `{Response_Text}{SIGNATURE}`
- Ejemplos:
  - Input: `"Hola"` → Output: `"Hola\n\n--- *Respuesta generada por CloudArquitecto*"`
  - Input: `""` → Output: `"\n\n--- *Respuesta generada por CloudArquitecto*"`

### Constants

**SIGNATURE (str)**
- Valor: `"\n\n--- *Respuesta generada por CloudArquitecto*"`
- Descripción: Firma que se añade al final de cada respuesta
- Inmutable: Definida como constante en el módulo

### Error Model

**TypeError**
- Condición: Cuando `output_text` no es de tipo `str`
- Mensaje: `"output_text debe ser de tipo str, se recibió {type(output_text).__name__}"`
- Manejo: La excepción se propaga al caller (el agente)


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Signature Concatenation

*For any* valid string input, the output of `formatear_respuesta` must be exactly the input string concatenated with the signature `"\n\n--- *Respuesta generada por CloudArquitecto*"`.

**Validates: Requirements 1.2, 1.3, 1.4**

**Rationale:** Esta propiedad verifica el comportamiento core de la función: que añade correctamente la firma sin modificar el texto original. Al verificar la concatenación exacta, automáticamente verificamos que:
- El texto original se preserva (1.3)
- La firma se añade al final (1.2)
- La firma es exactamente la especificada (1.4)

### Property 2: Type Validation with TypeError

*For any* input that is not of type `str`, the function `formatear_respuesta` must raise a `TypeError` exception.

**Validates: Requirements 3.1, 3.3**

**Rationale:** Esta propiedad garantiza la robustez de la función mediante validación de tipos en runtime. Verifica que la función rechaza inputs inválidos de manera predecible y consistente, lanzando el tipo de excepción apropiado.

### Property 3: Agent Integration Hook Application

*For any* response generated by the agent, the output hook must be automatically applied, resulting in the response containing the signature.

**Validates: Requirements 2.2**

**Rationale:** Esta propiedad verifica la integración end-to-end del sistema. Asegura que el mecanismo de hooks funciona correctamente y que todas las respuestas del agente pasan por el formateo, independientemente de su contenido o longitud.

### Edge Cases

**Edge Case 1: Empty String Input**
- Input: `""`
- Expected Output: `"\n\n--- *Respuesta generada por CloudArquitecto*"`
- Validates: Requirements 1.5, 3.4
- Rationale: El string vacío es un caso límite importante que debe manejarse correctamente sin lanzar excepciones.

**Edge Case 2: Multi-line Strings**
- Input: `"Línea 1\nLínea 2\nLínea 3"`
- Expected Output: `"Línea 1\nLínea 2\nLínea 3\n\n--- *Respuesta generada por CloudArquitecto*"`
- Validates: Requirements 3.5
- Rationale: Los saltos de línea deben preservarse correctamente en el texto original.

## Error Handling

### Error Scenarios

**Scenario 1: Non-String Input**
- Trigger: Llamar `formatear_respuesta` con un argumento que no es string
- Error Type: `TypeError`
- Error Message: `"output_text debe ser de tipo str, se recibió {type(output_text).__name__}"`
- Recovery: No hay recovery automático; el caller debe manejar la excepción
- Prevention: Usar type hints y validación en el caller

**Scenario 2: Agent Hook Failure**
- Trigger: Excepción dentro de `formatear_respuesta` durante ejecución del agente
- Error Type: Propagación de la excepción original
- Impact: La respuesta del agente puede fallar
- Recovery: El agente debe manejar excepciones de hooks según su implementación
- Prevention: Asegurar que `formatear_respuesta` solo recibe strings válidos

### Error Handling Strategy

1. **Fail Fast:** La función valida tipos inmediatamente y lanza excepciones descriptivas
2. **No Silent Failures:** Todos los errores se propagan; no hay valores de retorno por defecto
3. **Descriptive Messages:** Los mensajes de error incluyen el tipo recibido para facilitar debugging
4. **No Side Effects:** La función no tiene efectos secundarios; los errores no dejan el sistema en estado inconsistente

### Logging and Monitoring

- No se implementa logging dentro de `formatear_respuesta` para mantener la simplicidad
- El agente puede implementar logging de hooks si es necesario
- Los errores de tipo se capturarán en los logs del agente si este los implementa

## Testing Strategy

### Dual Testing Approach

Este sistema requiere tanto unit testing como property-based testing para garantizar correctness completa:

- **Unit Tests:** Verifican ejemplos específicos, casos edge, y condiciones de error
- **Property Tests:** Verifican propiedades universales a través de múltiples inputs generados aleatoriamente

Ambos enfoques son complementarios y necesarios:
- Los unit tests capturan bugs concretos y documentan comportamiento esperado
- Los property tests verifican correctness general y descubren casos edge inesperados

### Property-Based Testing

**Framework:** `hypothesis` (biblioteca estándar para property-based testing en Python)

**Configuration:**
- Mínimo 100 iteraciones por test de propiedad
- Cada test debe referenciar la propiedad del documento de diseño mediante un comentario

**Property Test 1: Signature Concatenation**
```python
# Feature: output-hook-formatter, Property 1: Signature Concatenation
@given(st.text())
@settings(max_examples=100)
def test_property_signature_concatenation(input_text):
    """
    For any valid string input, the output must be exactly 
    the input concatenated with the signature.
    """
    expected_signature = "\n\n--- *Respuesta generada por CloudArquitecto*"
    result = formatear_respuesta(input_text)
    assert result == input_text + expected_signature
```

**Property Test 2: Type Validation with TypeError**
```python
# Feature: output-hook-formatter, Property 2: Type Validation with TypeError
@given(st.one_of(st.integers(), st.floats(), st.lists(st.text()), 
                 st.none(), st.booleans(), st.dictionaries(st.text(), st.text())))
@settings(max_examples=100)
def test_property_type_validation(non_string_input):
    """
    For any input that is not of type str, the function must raise TypeError.
    """
    with pytest.raises(TypeError) as exc_info:
        formatear_respuesta(non_string_input)
    assert "output_text debe ser de tipo str" in str(exc_info.value)
```

**Property Test 3: Agent Integration Hook Application**
```python
# Feature: output-hook-formatter, Property 3: Agent Integration Hook Application
@given(st.text(min_size=1))
@settings(max_examples=100)
def test_property_agent_integration(prompt):
    """
    For any response generated by the agent, the output hook must be 
    automatically applied, resulting in the response containing the signature.
    """
    # Este test requiere un agente mock o de prueba
    agent = create_test_agent_with_hook()
    response = agent.generate_response(prompt)
    assert "\n\n--- *Respuesta generada por CloudArquitecto*" in response
```

### Unit Testing

**Unit Test Coverage:**

1. **Ejemplo básico:** Input simple, output esperado
2. **String vacío:** Edge case del string vacío
3. **Multi-línea:** Preservación de saltos de línea
4. **TypeError con None:** Validación de tipo con None
5. **TypeError con int:** Validación de tipo con entero
6. **TypeError con list:** Validación de tipo con lista
7. **Integración básica:** Verificar que el agente aplica el hook

**Example Unit Tests:**
```python
def test_formatear_respuesta_basic():
    """Verifica el comportamiento básico con un string simple."""
    result = formatear_respuesta("Hola mundo")
    assert result == "Hola mundo\n\n--- *Respuesta generada por CloudArquitecto*"

def test_formatear_respuesta_empty_string():
    """Verifica el manejo del string vacío."""
    result = formatear_respuesta("")
    assert result == "\n\n--- *Respuesta generada por CloudArquitecto*"

def test_formatear_respuesta_multiline():
    """Verifica la preservación de saltos de línea."""
    input_text = "Línea 1\nLínea 2\nLínea 3"
    result = formatear_respuesta(input_text)
    assert result == "Línea 1\nLínea 2\nLínea 3\n\n--- *Respuesta generada por CloudArquitecto*"

def test_formatear_respuesta_type_error_none():
    """Verifica que None lanza TypeError."""
    with pytest.raises(TypeError) as exc_info:
        formatear_respuesta(None)
    assert "output_text debe ser de tipo str" in str(exc_info.value)

def test_formatear_respuesta_type_error_int():
    """Verifica que un entero lanza TypeError."""
    with pytest.raises(TypeError) as exc_info:
        formatear_respuesta(123)
    assert "output_text debe ser de tipo str" in str(exc_info.value)
```

### Test Organization

```
tests/
├── unit/
│   └── test_formatear_respuesta.py      # Unit tests
├── property/
│   └── test_formatear_respuesta_properties.py  # Property-based tests
└── integration/
    └── test_agent_integration.py        # Integration tests
```

### Testing Guidelines

1. **Property tests primero:** Escribir property tests para verificar propiedades universales
2. **Unit tests para casos específicos:** Usar unit tests para documentar ejemplos y edge cases
3. **No sobre-testear:** Evitar unit tests redundantes que ya están cubiertos por property tests
4. **Mínimo 100 iteraciones:** Configurar hypothesis con `max_examples=100` o más
5. **Tags claros:** Cada property test debe tener un comentario referenciando la propiedad del diseño
