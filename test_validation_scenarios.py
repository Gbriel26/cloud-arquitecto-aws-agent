"""
Script de prueba para validar diferentes escenarios del sistema de validación.
"""

import os
import sys
from tool_validator import Validation_Hook, Tool_Validator, Console_Formatter

def test_scenario_1_no_file():
    """Escenario 1: tools.py no existe"""
    print("=" * 60)
    print("ESCENARIO 1: tools.py no existe")
    print("=" * 60)
    
    # Asegurar que tools.py no existe
    if os.path.exists("tools.py"):
        os.remove("tools.py")
    
    # Ejecutar validación
    Validation_Hook.run()
    print()

def test_scenario_2_valid_tools():
    """Escenario 2: tools.py con funciones válidas"""
    print("=" * 60)
    print("ESCENARIO 2: tools.py con funciones @tool válidas")
    print("=" * 60)
    
    # Crear tools.py con funciones válidas
    valid_code = '''
from strands import tool

@tool
def calcular_costo(instancias: int, horas: int) -> float:
    """
    Calcula el costo total de instancias EC2.
    
    Args:
        instancias: Número de instancias
        horas: Horas de uso
        
    Returns:
        Costo total en dólares
    """
    return instancias * horas * 0.10

@tool
def listar_regiones() -> list[str]:
    """
    Retorna la lista de regiones AWS disponibles.
    
    Returns:
        Lista de nombres de regiones
    """
    return ["us-east-1", "us-west-2", "eu-west-1"]
'''
    
    with open("tools.py", "w", encoding="utf-8") as f:
        f.write(valid_code)
    
    # Ejecutar validación
    Validation_Hook.run()
    print()

def test_scenario_3_invalid_tools():
    """Escenario 3: tools.py con errores de validación"""
    print("=" * 60)
    print("ESCENARIO 3: tools.py con errores de validación")
    print("=" * 60)
    
    # Crear tools.py con funciones inválidas
    invalid_code = '''
from strands import tool

@tool
def estimar_costo_lambda(invocaciones, duracion):
    """Calcula costo de Lambda"""
    return invocaciones * duracion * 0.0000002

@tool
def buscar_servicio(nombre: str):
    return f"Buscando {nombre}"

@tool
def sin_doc(param: str) -> None:
    pass
'''
    
    with open("tools.py", "w", encoding="utf-8") as f:
        f.write(invalid_code)
    
    # Ejecutar validación
    Validation_Hook.run()
    print()

def test_scenario_4_syntax_error():
    """Escenario 4: tools.py con errores de sintaxis"""
    print("=" * 60)
    print("ESCENARIO 4: tools.py con errores de sintaxis")
    print("=" * 60)
    
    # Crear tools.py con error de sintaxis
    syntax_error_code = '''
from strands import tool

@tool
def funcion_rota(param: str) -> str:
    """Esta función tiene un error de sintaxis"""
    return "hola
'''
    
    with open("tools.py", "w", encoding="utf-8") as f:
        f.write(syntax_error_code)
    
    # Ejecutar validación
    Validation_Hook.run()
    print()

def cleanup():
    """Limpia el archivo tools.py de prueba"""
    if os.path.exists("tools.py"):
        os.remove("tools.py")
        print("✓ Archivo tools.py de prueba eliminado")

if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "VALIDACIÓN COMPLETA DEL SISTEMA" + " " * 16 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    try:
        # Ejecutar todos los escenarios
        test_scenario_1_no_file()
        test_scenario_2_valid_tools()
        test_scenario_3_invalid_tools()
        test_scenario_4_syntax_error()
        
        print("=" * 60)
        print("RESUMEN DE PRUEBAS")
        print("=" * 60)
        print("✓ Escenario 1: tools.py inexistente - COMPLETADO")
        print("✓ Escenario 2: tools.py válido - COMPLETADO")
        print("✓ Escenario 3: tools.py con errores - COMPLETADO")
        print("✓ Escenario 4: tools.py con sintaxis inválida - COMPLETADO")
        print()
        print("✅ Todas las pruebas completadas exitosamente")
        print()
        
    finally:
        cleanup()
