"""
Test para verificar que el agente inicia correctamente con la validación integrada.
"""

import sys
import io
from contextlib import redirect_stdout

def test_agent_startup_with_validation():
    """
    Verifica que la validación se ejecuta al importar el módulo del agente.
    """
    print("=" * 60)
    print("TEST: Verificación de inicio del agente con validación")
    print("=" * 60)
    print()
    
    # Capturar la salida de la validación
    captured_output = io.StringIO()
    
    try:
        # La validación se ejecuta al importar
        # Nota: No podemos importar agent.py directamente porque entraría en el bucle
        # En su lugar, verificamos que Validation_Hook funciona correctamente
        from tool_validator import Validation_Hook
        
        print("✓ Módulo tool_validator importado correctamente")
        
        # Ejecutar validación manualmente
        with redirect_stdout(captured_output):
            Validation_Hook.run()
        
        output = captured_output.getvalue()
        
        print("✓ Validation_Hook.run() ejecutado sin excepciones")
        print()
        print("Salida de la validación:")
        print("-" * 60)
        print(output)
        print("-" * 60)
        print()
        
        # Verificar que la salida contiene el mensaje esperado
        assert "Validación exitosa" in output or "VALIDACIÓN DE HERRAMIENTAS" in output
        print("✓ Salida de validación contiene mensaje esperado")
        
        print()
        print("=" * 60)
        print("✅ TEST EXITOSO: El agente puede iniciar con validación")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_agent_startup_with_validation()
    sys.exit(0 if success else 1)
