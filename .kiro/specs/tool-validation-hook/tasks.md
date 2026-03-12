# Plan de Implementación: Sistema de Validación de Herramientas @tool

## Overview

Este plan implementa un sistema de validación automática que inspecciona funciones decoradas con @tool usando análisis AST de Python. El sistema se ejecuta al inicio del agente, valida docstrings y type hints, y muestra advertencias visuales en consola sin bloquear la ejecución.

La implementación sigue una arquitectura de pipeline lineal: Validation_Hook → Tool_Validator → AST_Inspector → Validation_Rules → Console_Formatter. Todos los componentes se crearán en un nuevo archivo `tool_validator.py`, y se integrará con `agent.py` mediante una llamada al inicio.

## Tasks

- [x] 1. Crear estructura base y modelos de datos
  - Crear archivo `tool_validator.py` en el directorio raíz del proyecto
  - Implementar dataclasses: `Parameter_Info`, `Function_Info`, `Validation_Error`, `Validation_Result`
  - Implementar método `Validation_Result.has_errors()` que retorna True si hay errores
  - Implementar método `Validation_Result.group_by_function()` que agrupa errores por nombre de función
  - _Requirements: 1.3, 2.2, 5.2_

- [ ]* 1.1 Escribir unit tests para modelos de datos
  - Crear archivo `test_tool_validator.py`
  - Test: `Validation_Result.has_errors()` retorna True cuando hay errores y False cuando está vacío
  - Test: `Validation_Result.group_by_function()` agrupa correctamente errores por función
  - Test: Crear instancias de cada dataclass con valores válidos
  - _Requirements: 1.3, 2.2, 5.2_

- [x] 2. Implementar AST_Inspector para análisis de código
  - [x] 2.1 Implementar método `AST_Inspector.find_tool_functions()`
    - Recorrer árbol AST usando `ast.walk()`
    - Identificar nodos `ast.FunctionDef` con decorador @tool
    - Manejar decoradores simples (`@tool`) y con módulo (`@strands.tool`)
    - Retornar lista de nodos `ast.FunctionDef` que tienen el decorador
    - _Requirements: 4.2_

  - [ ]* 2.2 Escribir property test para identificación completa de funciones @tool
    - **Property 4: Identificación completa de funciones @tool**
    - **Validates: Requirements 4.2**
    - Generar módulos Python con cantidad variable de funciones @tool y funciones normales
    - Verificar que el inspector identifica todas las funciones @tool sin omisiones ni falsos positivos
    - _Requirements: 4.2_

  - [ ]* 2.3 Escribir unit tests para detección de decoradores
    - Test: Identificar función con decorador `@tool` simple
    - Test: Identificar función con decorador `@strands.tool` (con módulo)
    - Test: Ignorar funciones sin decorador @tool
    - Test: Ignorar funciones con otros decoradores (e.g., `@staticmethod`)
    - _Requirements: 4.2_

  - [x] 2.4 Implementar método `AST_Inspector.extract_function_info()`
    - Extraer nombre de función desde `node.name`
    - Extraer docstring usando `ast.get_docstring(node)`
    - Extraer parámetros iterando sobre `node.args.args`
    - Para cada parámetro, extraer nombre y type hint desde `arg.annotation`
    - Identificar parámetros 'self' y 'cls' y marcarlos con flag `is_self_or_cls=True`
    - Extraer return type hint desde `node.returns`
    - Extraer número de línea desde `node.lineno`
    - Retornar instancia de `Function_Info`
    - Manejar `AttributeError` con valores por defecto seguros
    - _Requirements: 1.3, 2.1, 2.3, 2.4, 3.1_

  - [ ]* 2.5 Escribir unit tests para extracción de información
    - Test: Extraer nombre de función correctamente
    - Test: Extraer docstring cuando existe
    - Test: Retornar None cuando docstring no existe
    - Test: Extraer type hints de parámetros cuando existen
    - Test: Retornar None para parámetros sin type hint
    - Test: Identificar correctamente parámetros 'self' y 'cls'
    - Test: Extraer return type hint cuando existe
    - Test: Extraer número de línea correctamente
    - _Requirements: 1.3, 2.1, 2.3, 2.4, 3.1_

- [x] 3. Implementar Validation_Rules para verificación de estándares
  - [x] 3.1 Implementar método `Validation_Rules.validate_docstring()`
    - Verificar que `func_info.docstring` no es None
    - Verificar que longitud del docstring >= 10 caracteres
    - Si falta docstring, retornar mensaje "Missing docstring"
    - Si docstring < 10 caracteres, retornar mensaje "Docstring too short (minimum 10 characters)"
    - Si válido, retornar lista vacía
    - _Requirements: 1.1, 1.2, 1.4, 5.3_

  - [ ]* 3.2 Escribir property test para detección de docstrings
    - **Property 1: Detección de docstrings faltantes o insuficientes**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4**
    - Generar funciones con/sin docstrings de longitudes variadas (0-50 caracteres)
    - Verificar que funciones sin docstring o con docstring < 10 chars generan error con nombre de función
    - Verificar que funciones con docstring >= 10 chars no generan error
    - _Requirements: 1.1, 1.2, 1.4_

  - [ ]* 3.3 Escribir unit tests para validación de docstrings
    - Test: Función sin docstring genera error "Missing docstring"
    - Test: Docstring con 9 caracteres genera error "Docstring too short"
    - Test: Docstring con 10 caracteres es válido (lista vacía)
    - Test: Docstring con 50 caracteres es válido
    - _Requirements: 1.1, 1.2, 1.4_

  - [x] 3.4 Implementar método `Validation_Rules.validate_parameter_hints()`
    - Iterar sobre `func_info.parameters`
    - Para cada parámetro, verificar si `is_self_or_cls` es True, si es así, omitir validación
    - Para parámetros normales, verificar que `type_hint` no es None
    - Si falta type hint, agregar mensaje "Parameter '{name}' missing type hint"
    - Retornar lista de mensajes de error
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 5.4_

  - [ ]* 3.5 Escribir property test para detección de type hints en parámetros
    - **Property 2: Detección de type hints faltantes en parámetros**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
    - Generar funciones con 0-10 parámetros, con probabilidad variable de tener type hints
    - Incluir casos con 'self' y 'cls' que no deben generar errores
    - Verificar que parámetros sin type hint (excepto self/cls) generan error con nombres de función y parámetro
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [ ]* 3.6 Escribir unit tests para validación de type hints de parámetros
    - Test: Parámetro normal sin type hint genera error con nombre del parámetro
    - Test: Parámetro 'self' sin type hint no genera error
    - Test: Parámetro 'cls' sin type hint no genera error
    - Test: Función con todos los parámetros con type hints no genera errores
    - Test: Función con múltiples parámetros sin type hints genera múltiples errores
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 3.7 Implementar método `Validation_Rules.validate_return_hint()`
    - Verificar que `func_info.return_hint` no es None
    - Si falta return type hint, retornar mensaje "Missing return type hint"
    - Si return type hint es "None" (string), considerar válido
    - Si válido, retornar lista vacía
    - _Requirements: 3.1, 3.2, 3.3, 5.5_

  - [ ]* 3.8 Escribir property test para detección de return type hint
    - **Property 3: Detección de return type hint faltante**
    - **Validates: Requirements 3.1, 3.2, 3.3**
    - Generar funciones con/sin return type hint, incluyendo casos con return type "None"
    - Verificar que funciones sin return type hint generan error con nombre de función
    - Verificar que funciones con return type "None" son válidas
    - _Requirements: 3.1, 3.2, 3.3_

  - [ ]* 3.9 Escribir unit tests para validación de return type hint
    - Test: Función sin return type hint genera error "Missing return type hint"
    - Test: Función con return type hint "None" es válida
    - Test: Función con return type hint "str" es válida
    - Test: Función con return type hint complejo (e.g., "list[dict[str, int]]") es válida
    - _Requirements: 3.1, 3.2, 3.3_

- [x] 4. Implementar Tool_Validator para coordinación de validación
  - [x] 4.1 Implementar constructor `Tool_Validator.__init__()`
    - Inicializar instancias de `AST_Inspector` y `Validation_Rules` si es necesario
    - Preparar estructuras de datos internas
    - _Requirements: 4.1_

  - [x] 4.2 Implementar método `Tool_Validator.validate_tools_file()`
    - Intentar leer archivo usando `open(filepath, 'r').read()`
    - Manejar `FileNotFoundError`: retornar `Validation_Result` vacío con mensaje informativo
    - Parsear código usando `ast.parse(source_code)`
    - Manejar `SyntaxError`: retornar `Validation_Result` vacío con mensaje de error
    - Llamar `AST_Inspector.find_tool_functions(tree)` para obtener lista de funciones
    - Para cada función, llamar `AST_Inspector.extract_function_info(func_node)`
    - Para cada `Function_Info`, aplicar las tres reglas de validación
    - Acumular errores en lista de `Validation_Error`
    - Crear y retornar `Validation_Result` con estadísticas y errores
    - _Requirements: 4.1, 4.3, 4.4, 8.1, 8.2, 8.3_

  - [ ]* 4.3 Escribir unit tests para Tool_Validator
    - Test: Validar archivo con funciones @tool válidas retorna resultado sin errores
    - Test: Validar archivo con funciones @tool inválidas retorna errores específicos
    - Test: Archivo inexistente retorna resultado vacío sin lanzar excepción
    - Test: Archivo con errores de sintaxis retorna resultado vacío sin lanzar excepción
    - Test: Archivo vacío retorna resultado con 0 funciones
    - _Requirements: 4.1, 4.3, 4.4, 8.1, 8.2_

- [x] 5. Implementar Console_Formatter para salida visual
  - [x] 5.1 Implementar método `Console_Formatter.supports_color()`
    - Verificar si stdout es un terminal usando `sys.stdout.isatty()`
    - Verificar variable de entorno `TERM` no es "dumb"
    - Retornar True si ambas condiciones se cumplen
    - _Requirements: 7.4_

  - [x] 5.2 Implementar método `Console_Formatter.display_warnings()`
    - Si `result.has_errors()` es False, mostrar mensaje de éxito con ✅
    - Si hay errores, mostrar encabezado con ⚠️ y separador visual
    - Llamar `result.group_by_function()` para agrupar errores
    - Para cada función con errores, mostrar nombre de función y número de línea
    - Listar cada error con símbolo ✗ y mensaje específico
    - Mostrar separador visual al final
    - Mostrar resumen con formato "❌ X de Y funciones tienen errores de validación"
    - Si `supports_color()` es True, aplicar códigos ANSI: amarillo para encabezado, rojo para errores, verde para éxito
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 7.1, 7.2, 7.3, 7.4_

  - [ ]* 5.3 Escribir property test para formato de mensajes de error
    - **Property 5: Formato de mensajes de error**
    - **Validates: Requirements 5.2, 5.3, 5.4, 5.5**
    - Generar listas de errores de validación con diferentes tipos
    - Verificar que cada mensaje formateado contiene: nombre de función, tipo de error específico, y número de línea
    - _Requirements: 5.2, 5.3, 5.4, 5.5_

  - [ ]* 5.4 Escribir property test para agrupación de errores
    - **Property 6: Agrupación de errores por función**
    - **Validates: Requirements 7.2**
    - Generar listas de errores con múltiples funciones
    - Verificar que en la salida formateada, todos los errores de la misma función aparecen agrupados
    - _Requirements: 7.2_

  - [ ]* 5.5 Escribir property test para presencia de resumen
    - **Property 7: Presencia de resumen en salida**
    - **Validates: Requirements 7.3**
    - Generar resultados de validación con errores
    - Verificar que la salida formateada incluye línea de resumen con conteos
    - _Requirements: 7.3_

  - [ ]* 5.6 Escribir property test para separador visual
    - **Property 8: Separador visual en advertencias**
    - **Validates: Requirements 7.1**
    - Generar resultados de validación con errores
    - Verificar que la salida contiene separador visual distintivo (⚠️ o "WARNING:")
    - _Requirements: 7.1_

  - [ ]* 5.7 Escribir unit tests para formato de salida
    - Test: Resultado sin errores muestra mensaje "✅ Validación exitosa: X funciones @tool cumplen los estándares"
    - Test: Resultado con errores muestra encabezado "⚠️  VALIDACIÓN DE HERRAMIENTAS @tool"
    - Test: Errores de la misma función aparecen agrupados bajo el nombre de la función
    - Test: Resumen incluye formato "❌ X de Y funciones tienen errores de validación"
    - Test: Salida incluye separadores visuales (líneas de ━)
    - Test: Cuando terminal soporta colores, salida incluye códigos ANSI
    - _Requirements: 5.6, 7.1, 7.2, 7.3, 7.4_

- [x] 6. Implementar Validation_Hook como punto de entrada
  - [x] 6.1 Implementar método estático `Validation_Hook.run()`
    - Crear instancia de `Tool_Validator`
    - Llamar `validator.validate_tools_file("tools.py")` dentro de bloque try-except
    - Capturar cualquier excepción genérica y mostrar mensaje "⚠️  Error inesperado en validación: {tipo}: {mensaje}"
    - Si validación exitosa, llamar `Console_Formatter.display_warnings(result)`
    - Garantizar que el método nunca propaga excepciones
    - _Requirements: 6.1, 6.3, 8.1, 8.2, 8.4_

  - [ ]* 6.2 Escribir unit tests para Validation_Hook
    - Test: Llamar `run()` con archivo válido no lanza excepciones
    - Test: Llamar `run()` con archivo inexistente no lanza excepciones
    - Test: Llamar `run()` cuando ocurre `ImportError` no lanza excepciones
    - Test: Llamar `run()` cuando ocurre `AttributeError` no lanza excepciones
    - Test: Verificar que excepciones inesperadas se capturan y se muestra mensaje de error
    - _Requirements: 6.3, 8.1, 8.2, 8.3, 8.4_

- [x] 7. Checkpoint - Verificar implementación completa
  - Ejecutar todos los unit tests: `pytest test_tool_validator.py -v`
  - Ejecutar todos los property-based tests con hypothesis
  - Verificar cobertura de código: `pytest --cov=tool_validator --cov-report=term-missing`
  - Confirmar cobertura >= 90% líneas y >= 85% ramas
  - Asegurar que todos los tests pasan
  - Preguntar al usuario si hay dudas o ajustes necesarios

- [x] 8. Integrar validación con agent.py
  - [x] 8.1 Modificar agent.py para invocar validación al inicio
    - Agregar import: `from tool_validator import Validation_Hook`
    - Localizar el punto de inicio de ejecución del agente (después de imports, antes de aceptar input)
    - Insertar llamada: `Validation_Hook.run()`
    - Agregar comentario explicativo sobre el propósito de la validación
    - _Requirements: 6.1, 6.2_

  - [ ]* 8.2 Escribir test de integración end-to-end
    - Crear archivo temporal `tools.py` con funciones @tool válidas e inválidas
    - Ejecutar `Validation_Hook.run()` y capturar salida de consola
    - Verificar que la salida contiene advertencias esperadas
    - Verificar que la ejecución completa en < 500ms para 50 funciones
    - Limpiar archivo temporal
    - _Requirements: 6.2, 6.3_

- [-] 9. Documentación y verificación final
  - [x] 9.1 Agregar docstrings a todas las clases y métodos
    - Verificar que cada clase tiene docstring descriptivo
    - Verificar que cada método público tiene docstring con Args, Returns, Raises
    - Seguir formato PEP 257 para docstrings
    - _Requirements: 1.1_

  - [x] 9.2 Crear archivo README para el módulo de validación
    - Documentar propósito del sistema de validación
    - Explicar cómo funciona la integración con agent.py
    - Incluir ejemplos de salida de consola
    - Documentar cómo ejecutar los tests
    - _Requirements: 5.1, 6.1_

  - [x] 9.3 Verificación final de requisitos
    - Revisar que todos los 8 requisitos están implementados
    - Verificar que todas las 8 propiedades tienen property-based tests
    - Confirmar que el sistema cumple con el objetivo de < 500ms para 50 funciones
    - Ejecutar suite completa de tests una última vez
    - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 7.1, 8.1_

- [x] 10. Checkpoint final - Validación completa del sistema
  - Ejecutar el agente con `python agent.py` y verificar que la validación se ejecuta al inicio
  - Confirmar que las advertencias se muestran correctamente en consola
  - Verificar que el agente continúa funcionando normalmente después de la validación
  - Probar con diferentes escenarios: tools.py válido, con errores, inexistente
  - Asegurar que todos los tests pasan y la cobertura cumple los objetivos
  - Preguntar al usuario si el sistema cumple con sus expectativas

## Notes

- Las tareas marcadas con `*` son opcionales y pueden omitirse para un MVP más rápido
- Cada tarea referencia requisitos específicos para trazabilidad
- Los checkpoints aseguran validación incremental del progreso
- Los property-based tests validan propiedades universales de corrección
- Los unit tests validan ejemplos específicos y casos edge
- La implementación completa debe estar en `tool_validator.py` como módulo independiente
- La integración con `agent.py` es mínima: solo un import y una llamada a `Validation_Hook.run()`
