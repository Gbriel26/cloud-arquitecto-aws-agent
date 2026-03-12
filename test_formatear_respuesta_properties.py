"""
Property-based tests para formatear_respuesta usando hypothesis.

Este módulo contiene tests basados en propiedades que verifican el comportamiento
universal de la función formatear_respuesta a través de múltiples inputs generados
aleatoriamente. Los property tests complementan los unit tests al verificar que
las propiedades de correctness se mantienen para cualquier input válido.
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# Definir la constante y función localmente para evitar problemas de importación
SIGNATURE = "\n\n--- *Respuesta generada por CloudArquitecto*"

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
    if not isinstance(output_text, str):
        raise TypeError(
            f"output_text debe ser de tipo str, se recibió {type(output_text).__name__}"
        )
    
    return output_text + SIGNATURE


# Feature: output-hook-formatter, Property 1: Signature Concatenation
@given(st.text())
@settings(max_examples=100)
def test_property_signature_concatenation(input_text):
    """
    **Validates: Requirements 1.2, 1.3, 1.4**
    
    Property 1: Signature Concatenation
    
    For any valid string input, the output of formatear_respuesta must be exactly
    the input string concatenated with the signature.
    
    Esta propiedad verifica que:
    - El texto original se preserva sin modificaciones (Req 1.3)
    - La firma se añade al final (Req 1.2)
    - La firma es exactamente la especificada (Req 1.4)
    """
    result = formatear_respuesta(input_text)
    expected = input_text + SIGNATURE
    
    assert result == expected, (
        f"La concatenación no es correcta.\n"
        f"Input: {repr(input_text)}\n"
        f"Expected: {repr(expected)}\n"
        f"Got: {repr(result)}"
    )


# Feature: output-hook-formatter, Property 2: Type Validation with TypeError
@given(st.one_of(
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False),
    st.lists(st.text()),
    st.none(),
    st.booleans(),
    st.dictionaries(st.text(), st.text())
))
@settings(max_examples=100)
def test_property_type_validation(non_string_input):
    """
    **Validates: Requirements 3.1, 3.3**
    
    Property 2: Type Validation with TypeError
    
    For any input that is not of type str, the function formatear_respuesta
    must raise a TypeError exception with a descriptive message.
    
    Esta propiedad verifica que:
    - La función acepta solo strings (Req 3.1)
    - Inputs no-string lanzan TypeError (Req 3.3)
    - El mensaje de error es descriptivo
    """
    with pytest.raises(TypeError) as exc_info:
        formatear_respuesta(non_string_input)
    
    # Verificar que el mensaje de error es descriptivo
    error_message = str(exc_info.value)
    assert "output_text debe ser de tipo str" in error_message, (
        f"El mensaje de error no es descriptivo.\n"
        f"Input type: {type(non_string_input).__name__}\n"
        f"Error message: {error_message}"
    )
    
    # Verificar que el mensaje incluye el tipo recibido
    assert type(non_string_input).__name__ in error_message, (
        f"El mensaje de error no incluye el tipo recibido.\n"
        f"Input type: {type(non_string_input).__name__}\n"
        f"Error message: {error_message}"
    )
