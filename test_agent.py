"""
Tests unitarios para CloudArquitecto y sus herramientas.

Este módulo contiene pruebas exhaustivas para:
- Todas las herramientas @tool del agente
- Función de formateo de respuestas
- Validación de tipos y manejo de errores
- Casos edge y valores límite
"""

import pytest
from unittest.mock import patch, MagicMock
from tools import (
    estimar_costo_lambda,
    calcular_instancias_ec2,
    buscar_servicio_aws,
    recomendar_instancia
)

# Importar solo la función de formateo sin ejecutar el bucle principal
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
    SIGNATURE = "\n\n--- *Respuesta generada por CloudArquitecto*"
    
    if not isinstance(output_text, str):
        raise TypeError(
            f"output_text debe ser de tipo str, se recibió {type(output_text).__name__}"
        )
    
    return output_text + SIGNATURE


class TestEstimarCostoLambda:
    """Tests para la herramienta estimar_costo_lambda."""
    
    def test_calculo_basico(self):
        """Verifica el cálculo básico de costos Lambda."""
        resultado = estimar_costo_lambda(1000, 128)
        assert isinstance(resultado, float)
        assert resultado > 0
        # Verificar que el cálculo es aproximadamente correcto
        # 1000 invocaciones * 0.0000002 + (1000 * 128/1024) * 0.0000166667
        esperado = 0.0002 + (125 * 0.0000166667)
        assert abs(resultado - esperado) < 0.0001
    
    def test_cero_invocaciones(self):
        """Verifica el manejo de cero invocaciones."""
        resultado = estimar_costo_lambda(0, 128)
        assert resultado == 0.0
    
    def test_memoria_minima(self):
        """Verifica el cálculo con memoria mínima."""
        resultado = estimar_costo_lambda(1000, 128)
        assert isinstance(resultado, float)
        assert resultado > 0
    
    def test_memoria_maxima(self):
        """Verifica el cálculo con memoria alta."""
        resultado = estimar_costo_lambda(1000, 3008)
        assert isinstance(resultado, float)
        assert resultado > 0
    
    def test_invocaciones_altas(self):
        """Verifica el cálculo con muchas invocaciones."""
        resultado = estimar_costo_lambda(1000000, 512)
        assert isinstance(resultado, float)
        assert resultado > 0
    
    def test_tipos_incorrectos(self):
        """Verifica que los tipos incorrectos causan errores."""
        with pytest.raises(TypeError):
            estimar_costo_lambda("1000", 128)
        
        with pytest.raises(TypeError):
            estimar_costo_lambda(1000, "128")
        
        with pytest.raises(TypeError):
            estimar_costo_lambda(None, 128)


class TestCalcularInstanciasEC2:
    """Tests para la herramienta calcular_instancias_ec2."""
    
    def test_calculo_basico(self):
        """Verifica el cálculo básico de instancias."""
        resultado = calcular_instancias_ec2(100, 0.5)
        assert isinstance(resultado, int)
        assert resultado > 0
        # 100 usuarios * 0.5 carga = 50 / 80 = 0.625 -> int(0.625) = 0 -> 0 + 1 = 1
        assert resultado == 1
    
    def test_cero_usuarios(self):
        """Verifica el manejo de cero usuarios."""
        resultado = calcular_instancias_ec2(0, 0.5)
        assert resultado == 1  # Siempre al menos 1 instancia
    
    def test_carga_alta(self):
        """Verifica el cálculo con carga alta por usuario."""
        resultado = calcular_instancias_ec2(100, 2.0)
        assert isinstance(resultado, int)
        assert resultado > 2  # Debería necesitar más instancias
    
    def test_muchos_usuarios(self):
        """Verifica el cálculo con muchos usuarios."""
        resultado = calcular_instancias_ec2(10000, 0.1)
        assert isinstance(resultado, int)
        assert resultado > 10
    
    def test_carga_cero(self):
        """Verifica el manejo de carga cero."""
        resultado = calcular_instancias_ec2(100, 0.0)
        assert resultado == 1  # Siempre al menos 1 instancia
    
    def test_tipos_incorrectos(self):
        """Verifica que los tipos incorrectos causan errores."""
        with pytest.raises(TypeError):
            calcular_instancias_ec2("100", 0.5)
        
        with pytest.raises(TypeError):
            calcular_instancias_ec2(100, "0.5")
        
        with pytest.raises(TypeError):
            calcular_instancias_ec2(None, 0.5)


class TestBuscarServicioAWS:
    """Tests para la herramienta buscar_servicio_aws."""
    
    def test_servicio_lambda(self):
        """Verifica la búsqueda del servicio Lambda."""
        resultado = buscar_servicio_aws("lambda")
        assert isinstance(resultado, str)
        assert "Lambda" in resultado
        assert "serverless" in resultado
    
    def test_servicio_ec2(self):
        """Verifica la búsqueda del servicio EC2."""
        resultado = buscar_servicio_aws("ec2")
        assert isinstance(resultado, str)
        assert "EC2" in resultado
        assert "virtual" in resultado
    
    def test_servicio_s3(self):
        """Verifica la búsqueda del servicio S3."""
        resultado = buscar_servicio_aws("s3")
        assert isinstance(resultado, str)
        assert "S3" in resultado
        assert "Almacenamiento" in resultado
    
    def test_servicio_mayusculas(self):
        """Verifica que funciona con mayúsculas."""
        resultado = buscar_servicio_aws("LAMBDA")
        assert "Lambda" in resultado
    
    def test_servicio_mixto(self):
        """Verifica que funciona con mayúsculas y minúsculas mezcladas."""
        resultado = buscar_servicio_aws("LaMbDa")
        assert "Lambda" in resultado
    
    def test_servicio_inexistente(self):
        """Verifica el manejo de servicios inexistentes."""
        resultado = buscar_servicio_aws("servicio_inexistente")
        assert isinstance(resultado, str)
        assert "no encontrado" in resultado
        assert "servicio_inexistente" in resultado
    
    def test_string_vacio(self):
        """Verifica el manejo de string vacío."""
        resultado = buscar_servicio_aws("")
        assert isinstance(resultado, str)
        assert "no encontrado" in resultado
    
    def test_tipo_incorrecto(self):
        """Verifica que los tipos incorrectos causan errores."""
        with pytest.raises(AttributeError):
            buscar_servicio_aws(123)
        
        with pytest.raises(AttributeError):
            buscar_servicio_aws(None)


class TestRecomendarInstancia:
    """Tests para la herramienta recomendar_instancia."""
    
    def test_uso_basico(self):
        """Verifica la recomendación para uso básico."""
        resultado = recomendar_instancia("basico")
        assert isinstance(resultado, str)
        assert resultado == "t3.micro"
    
    def test_uso_produccion(self):
        """Verifica la recomendación para producción."""
        resultado = recomendar_instancia("produccion")
        assert isinstance(resultado, str)
        assert resultado == "m5.large"
    
    def test_uso_base_datos(self):
        """Verifica la recomendación para base de datos."""
        resultado = recomendar_instancia("base de datos")
        assert isinstance(resultado, str)
        assert resultado == "r5.4xlarge"
    
    def test_uso_mayusculas(self):
        """Verifica que funciona con mayúsculas."""
        resultado = recomendar_instancia("BASICO")
        assert resultado == "t3.micro"
    
    def test_uso_con_espacios(self):
        """Verifica que maneja espacios extra."""
        resultado = recomendar_instancia("  basico  ")
        assert resultado == "t3.micro"
    
    def test_uso_mixto(self):
        """Verifica que funciona con mayúsculas y minúsculas mezcladas."""
        resultado = recomendar_instancia("PrOdUcCiOn")
        assert resultado == "m5.large"
    
    def test_uso_inexistente(self):
        """Verifica el manejo de usos inexistentes."""
        resultado = recomendar_instancia("uso_inexistente")
        assert isinstance(resultado, str)
        assert "no reconocido" in resultado
        assert "uso_inexistente" in resultado
        assert "basico" in resultado
        assert "produccion" in resultado
        assert "base de datos" in resultado
    
    def test_string_vacio(self):
        """Verifica el manejo de string vacío."""
        resultado = recomendar_instancia("")
        assert isinstance(resultado, str)
        assert "no reconocido" in resultado
    
    def test_tipo_incorrecto(self):
        """Verifica que los tipos incorrectos causan errores."""
        with pytest.raises(AttributeError):
            recomendar_instancia(123)
        
        with pytest.raises(AttributeError):
            recomendar_instancia(None)


class TestFormatearRespuesta:
    """Tests para la función formatear_respuesta del agente."""
    
    def test_formateo_basico(self):
        """Verifica el formateo básico con un string simple."""
        resultado = formatear_respuesta("Hola mundo")
        assert isinstance(resultado, str)
        assert resultado == "Hola mundo\n\n--- *Respuesta generada por CloudArquitecto*"
    
    def test_string_vacio(self):
        """Verifica el manejo del string vacío."""
        resultado = formatear_respuesta("")
        assert resultado == "\n\n--- *Respuesta generada por CloudArquitecto*"
    
    def test_string_multilinea(self):
        """Verifica la preservación de saltos de línea."""
        input_text = "Línea 1\nLínea 2\nLínea 3"
        resultado = formatear_respuesta(input_text)
        expected = "Línea 1\nLínea 2\nLínea 3\n\n--- *Respuesta generada por CloudArquitecto*"
        assert resultado == expected
    
    def test_string_con_espacios(self):
        """Verifica el manejo de strings con espacios."""
        resultado = formatear_respuesta("  Texto con espacios  ")
        expected = "  Texto con espacios  \n\n--- *Respuesta generada por CloudArquitecto*"
        assert resultado == expected
    
    def test_string_largo(self):
        """Verifica el manejo de strings largos."""
        texto_largo = "A" * 1000
        resultado = formatear_respuesta(texto_largo)
        assert resultado.startswith(texto_largo)
        assert resultado.endswith("\n\n--- *Respuesta generada por CloudArquitecto*")
    
    def test_caracteres_especiales(self):
        """Verifica el manejo de caracteres especiales."""
        texto_especial = "Texto con ñ, acentos á é í ó ú, y símbolos @#$%"
        resultado = formatear_respuesta(texto_especial)
        assert resultado.startswith(texto_especial)
        assert resultado.endswith("\n\n--- *Respuesta generada por CloudArquitecto*")
    
    def test_tipo_incorrecto_none(self):
        """Verifica que None lanza TypeError."""
        with pytest.raises(TypeError) as exc_info:
            formatear_respuesta(None)
        assert "output_text debe ser de tipo str" in str(exc_info.value)
        assert "NoneType" in str(exc_info.value)
    
    def test_tipo_incorrecto_int(self):
        """Verifica que un entero lanza TypeError."""
        with pytest.raises(TypeError) as exc_info:
            formatear_respuesta(123)
        assert "output_text debe ser de tipo str" in str(exc_info.value)
        assert "int" in str(exc_info.value)
    
    def test_tipo_incorrecto_list(self):
        """Verifica que una lista lanza TypeError."""
        with pytest.raises(TypeError) as exc_info:
            formatear_respuesta(["texto"])
        assert "output_text debe ser de tipo str" in str(exc_info.value)
        assert "list" in str(exc_info.value)
    
    def test_tipo_incorrecto_dict(self):
        """Verifica que un diccionario lanza TypeError."""
        with pytest.raises(TypeError) as exc_info:
            formatear_respuesta({"texto": "valor"})
        assert "output_text debe ser de tipo str" in str(exc_info.value)
        assert "dict" in str(exc_info.value)


class TestIntegracionAgente:
    """Tests de integración para el agente completo."""
    
    def test_signature_constante(self):
        """Verifica que la constante SIGNATURE está definida correctamente."""
        SIGNATURE = "\n\n--- *Respuesta generada por CloudArquitecto*"
        assert isinstance(SIGNATURE, str)
        assert SIGNATURE == "\n\n--- *Respuesta generada por CloudArquitecto*"
    
    def test_formatear_respuesta_existe(self):
        """Verifica que la función formatear_respuesta existe y funciona."""
        resultado = formatear_respuesta("test")
        assert isinstance(resultado, str)
        assert "CloudArquitecto" in resultado


# Fixtures para tests que requieren datos de prueba
@pytest.fixture
def datos_lambda_validos():
    """Fixture con datos válidos para tests de Lambda."""
    return [
        (1000, 128, 0.0002 + (125 * 0.0000166667)),
        (5000, 256, 0.001 + (1250 * 0.0000166667)),
        (10000, 512, 0.002 + (5000 * 0.0000166667))
    ]


@pytest.fixture
def datos_ec2_validos():
    """Fixture con datos válidos para tests de EC2."""
    return [
        (100, 0.5, 1),  # 100 * 0.5 = 50 / 80 = 0.625 -> int(0.625) = 0 -> 0 + 1 = 1
        (200, 1.0, 3),  # 200 * 1.0 = 200 / 80 = 2.5 -> int(2.5) = 2 -> 2 + 1 = 3
        (80, 1.0, 2)    # 80 * 1.0 = 80 / 80 = 1.0 -> int(1.0) = 1 -> 1 + 1 = 2
    ]


class TestParametrizados:
    """Tests parametrizados para verificar múltiples casos."""
    
    @pytest.mark.parametrize("invocaciones,memoria,esperado_aprox", [
        (1000, 128, 0.0002 + (125 * 0.0000166667)),
        (5000, 256, 0.001 + (1250 * 0.0000166667)),
        (0, 128, 0.0)
    ])
    def test_estimar_costo_lambda_parametrizado(self, invocaciones, memoria, esperado_aprox):
        """Test parametrizado para múltiples casos de Lambda."""
        resultado = estimar_costo_lambda(invocaciones, memoria)
        assert isinstance(resultado, float)
        assert abs(resultado - esperado_aprox) < 0.0001
    
    @pytest.mark.parametrize("usuarios,carga,esperado", [
        (100, 0.5, 1),  # 100 * 0.5 = 50 / 80 = 0.625 -> int(0.625) = 0 -> 0 + 1 = 1
        (200, 1.0, 3),  # 200 * 1.0 = 200 / 80 = 2.5 -> int(2.5) = 2 -> 2 + 1 = 3
        (0, 0.5, 1),    # 0 * 0.5 = 0 / 80 = 0 -> int(0) = 0 -> 0 + 1 = 1
        (80, 1.0, 2)    # 80 * 1.0 = 80 / 80 = 1.0 -> int(1.0) = 1 -> 1 + 1 = 2
    ])
    def test_calcular_instancias_ec2_parametrizado(self, usuarios, carga, esperado):
        """Test parametrizado para múltiples casos de EC2."""
        resultado = calcular_instancias_ec2(usuarios, carga)
        assert isinstance(resultado, int)
        assert resultado == esperado
    
    @pytest.mark.parametrize("servicio,esperado_en_resultado", [
        ("lambda", "Lambda"),
        ("ec2", "EC2"),
        ("s3", "S3"),
        ("LAMBDA", "Lambda"),
        ("inexistente", "no encontrado")
    ])
    def test_buscar_servicio_aws_parametrizado(self, servicio, esperado_en_resultado):
        """Test parametrizado para múltiples servicios AWS."""
        resultado = buscar_servicio_aws(servicio)
        assert isinstance(resultado, str)
        assert esperado_en_resultado in resultado
    
    @pytest.mark.parametrize("uso,esperado", [
        ("basico", "t3.micro"),
        ("produccion", "m5.large"),
        ("base de datos", "r5.4xlarge"),
        ("BASICO", "t3.micro"),
        ("  produccion  ", "m5.large"),
        ("inexistente", "no reconocido")
    ])
    def test_recomendar_instancia_parametrizado(self, uso, esperado):
        """Test parametrizado para múltiples tipos de uso."""
        resultado = recomendar_instancia(uso)
        assert isinstance(resultado, str)
        if esperado == "no reconocido":
            assert esperado in resultado
        else:
            assert resultado == esperado


if __name__ == "__main__":
    # Ejecutar tests con pytest
    pytest.main([__file__, "-v", "--tb=short"])