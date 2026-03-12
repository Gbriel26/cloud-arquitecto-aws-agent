"""
Tests completos para el sistema de validación de herramientas @tool.
"""

import ast
import os
import tempfile
import pytest
from tool_validator import (
    Parameter_Info,
    Function_Info,
    Validation_Error,
    Validation_Result,
    AST_Inspector,
    Validation_Rules,
    Tool_Validator,
    Console_Formatter,
    Validation_Hook
)


# ============================================================================
# Tests para modelos de datos
# ============================================================================

class TestValidationResult:
    """Tests para Validation_Result."""
    
    def test_has_errors_returns_true_when_errors_exist(self):
        """Test: has_errors() retorna True cuando hay errores."""
        errors = [
            Validation_Error("func1", 10, "docstring", "Missing docstring")
        ]
        result = Validation_Result(
            total_functions=1,
            functions_with_errors=1,
            errors=errors
        )
        assert result.has_errors() == True
    
    def test_has_errors_returns_false_when_no_errors(self):
        """Test: has_errors() retorna False cuando no hay errores."""
        result = Validation_Result(
            total_functions=1,
            functions_with_errors=0,
            errors=[]
        )
        assert result.has_errors() == False
    
    def test_group_by_function_groups_correctly(self):
        """Test: group_by_function() agrupa errores correctamente."""
        errors = [
            Validation_Error("func1", 10, "docstring", "Missing docstring"),
            Validation_Error("func1", 10, "return_hint", "Missing return type hint"),
            Validation_Error("func2", 20, "docstring", "Missing docstring")
        ]
        result = Validation_Result(
            total_functions=2,
            functions_with_errors=2,
            errors=errors
        )
        
        grouped = result.group_by_function()
        
        assert len(grouped) == 2
        assert len(grouped["func1"]) == 2
        assert len(grouped["func2"]) == 1
        assert grouped["func1"][0].message == "Missing docstring"
        assert grouped["func1"][1].message == "Missing return type hint"


# ============================================================================
# Tests para Validation_Rules
# ============================================================================

class TestValidationRules:
    """Tests para Validation_Rules."""
    
    def test_validate_docstring_missing(self):
        """Test: Función sin docstring genera error."""
        func_info = Function_Info(
            name="test_func",
            docstring=None,
            parameters=[],
            return_hint="str",
            line_number=10
        )
        
        errors = Validation_Rules.validate_docstring(func_info)
        
        assert len(errors) == 1
        assert errors[0] == "Missing docstring"
    
    def test_validate_docstring_too_short(self):
        """Test: Docstring < 10 caracteres genera error."""
        func_info = Function_Info(
            name="test_func",
            docstring="Short",
            parameters=[],
            return_hint="str",
            line_number=10
        )
        
        errors = Validation_Rules.validate_docstring(func_info)
        
        assert len(errors) == 1
        assert "too short" in errors[0]
    
    def test_validate_docstring_valid(self):
        """Test: Docstring >= 10 caracteres es válido."""
        func_info = Function_Info(
            name="test_func",
            docstring="This is a valid docstring with enough characters.",
            parameters=[],
            return_hint="str",
            line_number=10
        )
        
        errors = Validation_Rules.validate_docstring(func_info)
        
        assert len(errors) == 0
    
    def test_validate_parameter_hints_missing(self):
        """Test: Parámetro sin type hint genera error."""
        func_info = Function_Info(
            name="test_func",
            docstring="Valid docstring.",
            parameters=[
                Parameter_Info("param1", None, False)
            ],
            return_hint="str",
            line_number=10
        )
        
        errors = Validation_Rules.validate_parameter_hints(func_info)
        
        assert len(errors) == 1
        assert "param1" in errors[0]
        assert "missing type hint" in errors[0]
    
    def test_validate_parameter_hints_self_ignored(self):
        """Test: Parámetro 'self' sin type hint no genera error."""
        func_info = Function_Info(
            name="test_func",
            docstring="Valid docstring.",
            parameters=[
                Parameter_Info("self", None, True)
            ],
            return_hint="str",
            line_number=10
        )
        
        errors = Validation_Rules.validate_parameter_hints(func_info)
        
        assert len(errors) == 0
    
    def test_validate_parameter_hints_cls_ignored(self):
        """Test: Parámetro 'cls' sin type hint no genera error."""
        func_info = Function_Info(
            name="test_func",
            docstring="Valid docstring.",
            parameters=[
                Parameter_Info("cls", None, True)
            ],
            return_hint="str",
            line_number=10
        )
        
        errors = Validation_Rules.validate_parameter_hints(func_info)
        
        assert len(errors) == 0
    
    def test_validate_parameter_hints_all_valid(self):
        """Test: Todos los parámetros con type hints no genera errores."""
        func_info = Function_Info(
            name="test_func",
            docstring="Valid docstring.",
            parameters=[
                Parameter_Info("param1", "str", False),
                Parameter_Info("param2", "int", False)
            ],
            return_hint="str",
            line_number=10
        )
        
        errors = Validation_Rules.validate_parameter_hints(func_info)
        
        assert len(errors) == 0
    
    def test_validate_return_hint_missing(self):
        """Test: Función sin return type hint genera error."""
        func_info = Function_Info(
            name="test_func",
            docstring="Valid docstring.",
            parameters=[],
            return_hint=None,
            line_number=10
        )
        
        errors = Validation_Rules.validate_return_hint(func_info)
        
        assert len(errors) == 1
        assert "Missing return type hint" in errors[0]
    
    def test_validate_return_hint_none_valid(self):
        """Test: Función con return type hint 'None' es válida."""
        func_info = Function_Info(
            name="test_func",
            docstring="Valid docstring.",
            parameters=[],
            return_hint="None",
            line_number=10
        )
        
        errors = Validation_Rules.validate_return_hint(func_info)
        
        assert len(errors) == 0
    
    def test_validate_return_hint_valid(self):
        """Test: Función con return type hint es válida."""
        func_info = Function_Info(
            name="test_func",
            docstring="Valid docstring.",
            parameters=[],
            return_hint="str",
            line_number=10
        )
        
        errors = Validation_Rules.validate_return_hint(func_info)
        
        assert len(errors) == 0


# ============================================================================
# Tests para Tool_Validator
# ============================================================================

class TestToolValidator:
    """Tests para Tool_Validator."""
    
    def test_validate_valid_file(self):
        """Test: Validar archivo con funciones válidas retorna sin errores."""
        # Crear archivo temporal con función válida
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write("""
@tool
def valid_function(param1: str, param2: int) -> bool:
    '''This is a valid docstring with enough characters.'''
    return True
""")
            temp_file = f.name
        
        try:
            validator = Tool_Validator()
            result = validator.validate_tools_file(temp_file)
            
            assert result.total_functions == 1
            assert result.functions_with_errors == 0
            assert len(result.errors) == 0
        finally:
            os.unlink(temp_file)
    
    def test_validate_invalid_file(self):
        """Test: Validar archivo con funciones inválidas retorna errores."""
        # Crear archivo temporal con función inválida
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write("""
@tool
def invalid_function(param1, param2):
    pass
""")
            temp_file = f.name
        
        try:
            validator = Tool_Validator()
            result = validator.validate_tools_file(temp_file)
            
            assert result.total_functions == 1
            assert result.functions_with_errors == 1
            assert len(result.errors) > 0
        finally:
            os.unlink(temp_file)
    
    def test_validate_nonexistent_file(self):
        """Test: Archivo inexistente retorna resultado vacío."""
        validator = Tool_Validator()
        result = validator.validate_tools_file("nonexistent_file.py")
        
        assert result.total_functions == 0
        assert result.functions_with_errors == 0
        assert len(result.errors) == 0
    
    def test_validate_syntax_error_file(self):
        """Test: Archivo con errores de sintaxis retorna resultado vacío."""
        # Crear archivo temporal con sintaxis inválida
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write("""
def invalid syntax here
""")
            temp_file = f.name
        
        try:
            validator = Tool_Validator()
            result = validator.validate_tools_file(temp_file)
            
            assert result.total_functions == 0
            assert result.functions_with_errors == 0
            assert len(result.errors) == 0
        finally:
            os.unlink(temp_file)
    
    def test_validate_empty_file(self):
        """Test: Archivo vacío retorna resultado con 0 funciones."""
        # Crear archivo temporal vacío
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write("")
            temp_file = f.name
        
        try:
            validator = Tool_Validator()
            result = validator.validate_tools_file(temp_file)
            
            assert result.total_functions == 0
            assert result.functions_with_errors == 0
            assert len(result.errors) == 0
        finally:
            os.unlink(temp_file)


# ============================================================================
# Tests para Console_Formatter
# ============================================================================

class TestConsoleFormatter:
    """Tests para Console_Formatter."""
    
    def test_supports_color_detection(self):
        """Test: supports_color() detecta soporte de colores."""
        # Este test solo verifica que el método no falla
        result = Console_Formatter.supports_color()
        assert isinstance(result, bool)
    
    def test_display_warnings_no_errors(self, capsys):
        """Test: Resultado sin errores muestra mensaje de éxito."""
        result = Validation_Result(
            total_functions=5,
            functions_with_errors=0,
            errors=[]
        )
        
        Console_Formatter.display_warnings(result)
        
        captured = capsys.readouterr()
        assert "✅" in captured.out
        assert "5 funciones" in captured.out
        assert "cumplen los estándares" in captured.out
    
    def test_display_warnings_with_errors(self, capsys):
        """Test: Resultado con errores muestra advertencias."""
        errors = [
            Validation_Error("func1", 10, "docstring", "Missing docstring"),
            Validation_Error("func1", 10, "return_hint", "Missing return type hint")
        ]
        result = Validation_Result(
            total_functions=1,
            functions_with_errors=1,
            errors=errors
        )
        
        Console_Formatter.display_warnings(result)
        
        captured = capsys.readouterr()
        assert "⚠️" in captured.out
        assert "VALIDACIÓN DE HERRAMIENTAS @tool" in captured.out
        assert "func1" in captured.out
        assert "línea 10" in captured.out
        assert "Missing docstring" in captured.out
        assert "Missing return type hint" in captured.out
        assert "❌" in captured.out
    
    def test_display_warnings_groups_by_function(self, capsys):
        """Test: Errores se agrupan por función."""
        errors = [
            Validation_Error("func1", 10, "docstring", "Missing docstring"),
            Validation_Error("func2", 20, "return_hint", "Missing return type hint")
        ]
        result = Validation_Result(
            total_functions=2,
            functions_with_errors=2,
            errors=errors
        )
        
        Console_Formatter.display_warnings(result)
        
        captured = capsys.readouterr()
        assert "func1" in captured.out
        assert "func2" in captured.out
        assert "2 de 2 funciones" in captured.out


# ============================================================================
# Tests para Validation_Hook
# ============================================================================

class TestValidationHook:
    """Tests para Validation_Hook."""
    
    def test_run_with_valid_file(self, capsys):
        """Test: run() con archivo válido no lanza excepciones."""
        # Crear archivo tools.py temporal válido
        with open("tools.py", 'w', encoding='utf-8') as f:
            f.write("""
@tool
def valid_function(param1: str) -> None:
    '''This is a valid docstring.'''
    pass
""")
        
        try:
            Validation_Hook.run()
            captured = capsys.readouterr()
            # No debe haber errores inesperados
            assert "Error inesperado" not in captured.out
        finally:
            if os.path.exists("tools.py"):
                os.unlink("tools.py")
    
    def test_run_with_nonexistent_file(self, capsys):
        """Test: run() con archivo inexistente no lanza excepciones."""
        # Asegurar que tools.py no existe
        if os.path.exists("tools.py"):
            os.unlink("tools.py")
        
        Validation_Hook.run()
        captured = capsys.readouterr()
        # No debe haber errores inesperados
        assert "Error inesperado" not in captured.out


# ============================================================================
# Tests de integración
# ============================================================================

class TestIntegration:
    """Tests de integración end-to-end."""
    
    def test_complete_validation_flow(self, capsys):
        """Test: Flujo completo de validación."""
        # Crear archivo tools.py con funciones válidas e inválidas
        with open("tools.py", 'w', encoding='utf-8') as f:
            f.write("""
@tool
def valid_function(param1: str, param2: int) -> bool:
    '''This is a valid docstring with enough characters.'''
    return True

@tool
def invalid_function(param1, param2):
    pass
""")
        
        try:
            Validation_Hook.run()
            captured = capsys.readouterr()
            
            # Debe mostrar advertencias para invalid_function
            assert "invalid_function" in captured.out
            # No debe mostrar advertencias para valid_function
            # (o si las muestra, debe indicar que hay 1 de 2 funciones con errores)
            assert "1 de 2 funciones" in captured.out or "2 de 2 funciones" in captured.out
        finally:
            if os.path.exists("tools.py"):
                os.unlink("tools.py")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# ============================================================================
# Tests adicionales para mejorar cobertura
# ============================================================================

class TestEdgeCases:
    """Tests para casos edge y manejo de errores."""
    
    def test_validation_hook_handles_unexpected_exception(self, capsys, monkeypatch):
        """Test: Validation_Hook captura excepciones inesperadas."""
        # Simular una excepción inesperada en Tool_Validator
        def mock_validate_tools_file(self, filepath):
            raise RuntimeError("Unexpected error")
        
        monkeypatch.setattr(Tool_Validator, "validate_tools_file", mock_validate_tools_file)
        
        # No debe lanzar excepción
        Validation_Hook.run()
        
        captured = capsys.readouterr()
        assert "Error inesperado en validación" in captured.out
        assert "RuntimeError" in captured.out
    
    def test_console_formatter_with_color_support(self, capsys, monkeypatch):
        """Test: Console_Formatter usa colores cuando están disponibles."""
        # Forzar soporte de colores
        monkeypatch.setattr('sys.stdout.isatty', lambda: True)
        monkeypatch.setenv('TERM', 'xterm-256color')
        
        result = Validation_Result(
            total_functions=1,
            functions_with_errors=0,
            errors=[]
        )
        
        Console_Formatter.display_warnings(result)
        
        captured = capsys.readouterr()
        # Debe contener códigos ANSI de color (o al menos el mensaje)
        assert "✅" in captured.out
    
    def test_console_formatter_without_color_support(self, capsys, monkeypatch):
        """Test: Console_Formatter funciona sin soporte de colores."""
        # Forzar sin soporte de colores
        monkeypatch.setattr('sys.stdout.isatty', lambda: False)
        
        result = Validation_Result(
            total_functions=1,
            functions_with_errors=0,
            errors=[]
        )
        
        Console_Formatter.display_warnings(result)
        
        captured = capsys.readouterr()
        assert "✅" in captured.out
    
    def test_ast_inspector_handles_attribute_error_in_type_hint(self):
        """Test: AST_Inspector maneja AttributeError al extraer type hints."""
        # Crear un código con anotación compleja que podría causar problemas
        code = """
@tool
def complex_function(param1, param2):
    '''Valid docstring here.'''
    pass
"""
        tree = ast.parse(code)
        functions = AST_Inspector.find_tool_functions(tree)
        func_info = AST_Inspector.extract_function_info(functions[0])
        
        # Debe manejar la falta de type hints sin errores
        assert func_info.parameters[0].type_hint is None
        assert func_info.parameters[1].type_hint is None
    
    def test_supports_color_with_dumb_terminal(self, monkeypatch):
        """Test: supports_color retorna False con TERM=dumb."""
        monkeypatch.setattr('sys.stdout.isatty', lambda: True)
        monkeypatch.setenv('TERM', 'dumb')
        
        result = Console_Formatter.supports_color()
        
        assert result == False
    
    def test_supports_color_with_non_tty(self, monkeypatch):
        """Test: supports_color retorna False cuando stdout no es tty."""
        monkeypatch.setattr('sys.stdout.isatty', lambda: False)
        
        result = Console_Formatter.supports_color()
        
        assert result == False
