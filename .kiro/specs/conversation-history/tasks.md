# Plan de Implementación: Historial de Conversación

## Descripción General

Este plan implementa la funcionalidad de persistencia del historial de conversación para el agente CloudArquitecto. Se creará un componente History_Manager que captura automáticamente cada interacción usuario-agente y la almacena en un archivo JSON estructurado, integrándose de manera no invasiva en el flujo existente del agente.

## Tareas

- [x] 1. Crear módulo History_Manager con estructura básica
  - Crear archivo `history_manager.py` en el directorio raíz
  - Implementar clase `History_Manager` con método `__init__`
  - Inicializar atributos `history_file` y `history` (lista vacía)
  - _Requisitos: 1.3, 3.1_

- [ ] 2. Implementar método para crear entradas de conversación
  - [x] 2.1 Implementar método `_create_entry(pregunta, respuesta)`
    - Generar timestamp en formato ISO 8601 con microsegundos usando `datetime.now().isoformat()`
    - Retornar diccionario con estructura: `{"timestamp": str, "pregunta": str, "respuesta": str}`
    - _Requisitos: 1.1, 1.4, 1.5, 1.6, 3.2, 3.3_
  
  - [ ]* 2.2 Escribir property test para formato de timestamp
    - **Property 2: ISO 8601 Timestamp Format**
    - **Valida: Requisitos 1.4, 3.3**
  
  - [ ]* 2.3 Escribir property test para estructura de entrada
    - **Property 3: Entry Structure Completeness**
    - **Valida: Requisitos 3.2, 3.6**

- [ ] 3. Implementar persistencia de escritura
  - [x] 3.1 Implementar método `_write_history()`
    - Escribir `self.history` al archivo JSON con encoding UTF-8
    - Usar `json.dump()` con `indent=2` para legibilidad
    - Capturar excepciones de I/O y retornar `False` en caso de error
    - Retornar `True` si escritura exitosa
    - _Requisitos: 1.2, 3.4, 3.5, 4.1, 4.3_
  
  - [x] 3.2 Implementar método `save_entry(pregunta, respuesta)`
    - Llamar a `_create_entry()` para crear objeto de entrada
    - Agregar entrada a `self.history`
    - Llamar a `_write_history()` para persistir
    - Capturar excepciones y mostrar advertencia sin interrumpir
    - Retornar `True/False` según éxito de operación
    - _Requisitos: 1.1, 1.2, 1.8, 4.1, 4.5_
  
  - [ ]* 3.3 Escribir property test para round-trip persistence
    - **Property 1: Round-trip Persistence**
    - **Valida: Requisitos 1.2, 1.5, 1.6**
  
  - [ ]* 3.4 Escribir property test para preservación de historial
    - **Property 4: History Preservation on Append**
    - **Valida: Requisitos 1.8**
  
  - [ ]* 3.5 Escribir unit tests para escritura
    - Test de indentación de 2 espacios en JSON
    - Test de error de permisos de escritura
    - _Requisitos: 3.5, 4.1_

- [x] 4. Checkpoint - Verificar persistencia básica
  - Asegurar que todos los tests pasen, preguntar al usuario si surgen dudas.

- [ ] 5. Implementar carga de historial
  - [x] 5.1 Implementar método `load_history()`
    - Verificar si archivo existe; si no, crear archivo vacío con `[]`
    - Leer archivo JSON y cargar en `self.history`
    - Capturar `json.JSONDecodeError` para archivos corruptos
    - Capturar `IOError/PermissionError` para errores de lectura
    - Calcular número de conversaciones y fecha de última conversación
    - Retornar diccionario con `success`, `count`, `last_date`, `message`
    - Mostrar mensaje apropiado en consola según el caso
    - _Requisitos: 1.7, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 4.2, 4.3_
  
  - [ ]* 5.2 Escribir property test para precisión del resumen
    - **Property 5: Summary Accuracy**
    - **Valida: Requisitos 2.2, 2.3, 2.4**
  
  - [ ]* 5.3 Escribir unit tests para carga de historial
    - Test de primera sesión (archivo no existe)
    - Test de archivo JSON corrupto
    - Test de error de permisos de lectura
    - _Requisitos: 2.5, 2.6, 4.2_

- [ ] 6. Implementar manejo de caracteres UTF-8
  - [ ]* 6.1 Escribir property test para preservación UTF-8
    - **Property 6: UTF-8 Character Preservation**
    - **Valida: Requisitos 3.4**
  
  - [ ]* 6.2 Escribir unit test para caracteres especiales
    - Test con emojis, acentos y símbolos especiales
    - _Requisitos: 3.4_

- [ ] 7. Implementar resiliencia ante errores
  - [ ]* 7.1 Escribir property test para resiliencia de errores
    - **Property 7: Error Resilience**
    - **Valida: Requisitos 4.1, 4.2, 4.3, 4.5**
  
  - [ ]* 7.2 Escribir unit test de integración completa
    - Test de flujo completo: primera sesión, múltiples conversaciones, segunda sesión
    - _Requisitos: 1.1, 1.2, 2.1, 2.2_

- [x] 8. Integrar History_Manager en agent.py
  - [x] 8.1 Importar History_Manager en agent.py
    - Agregar `from history_manager import History_Manager` después de imports existentes
    - _Requisitos: 1.1_
  
  - [x] 8.2 Inicializar History_Manager al inicio
    - Crear instancia de `History_Manager()` después de inicializar el agente
    - Llamar a `load_history()` y mostrar resumen antes del bucle
    - _Requisitos: 2.1, 2.2, 2.3, 2.4_
  
  - [x] 8.3 Guardar conversaciones en el bucle
    - Después de recibir respuesta del agente, llamar a `save_entry(user_input, respuesta)`
    - Asegurar que errores de persistencia no interrumpan el bucle
    - _Requisitos: 1.1, 1.2, 4.4_

- [x] 9. Checkpoint final - Verificar integración completa
  - Asegurar que todos los tests pasen, preguntar al usuario si surgen dudas.

## Notas

- Las tareas marcadas con `*` son opcionales y pueden omitirse para un MVP más rápido
- Cada tarea referencia requisitos específicos para trazabilidad
- Los checkpoints aseguran validación incremental
- Los property tests validan propiedades de correctitud universales
- Los unit tests validan casos específicos y condiciones de error
- La integración en agent.py es no invasiva y no modifica la lógica core del agente
