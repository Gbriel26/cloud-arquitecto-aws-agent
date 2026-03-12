"""
Tests básicos para verificar la implementación de AST_Inspector.
"""

import ast
from tool_validator import AST_Inspector, Function_Info, Parameter_Info


def test_find_tool_functions_simple_decorator():
    """Test: Identificar función con decorador @tool simple."""
    code = """
@tool
def my_function():
    pass
"""
    tree = ast.parse(code)
    functions = AST_Inspector.find_tool_functions(tree)
    
    assert len(functions) == 1
    assert functions[0].name == "my_function"
    print("✓ Test passed: find_tool_functions with simple @tool decorator")


def test_find_tool_functions_module_decorator():
    """Test: Identificar función con decorador @strands.tool."""
    code = """
@strands.tool
def my_function():
    pass
"""
    tree = ast.parse(code)
    functions = AST_Inspector.find_tool_functions(tree)
    
    assert len(functions) == 1
    assert functions[0].name == "my_function"
    print("✓ Test passed: find_tool_functions with @strands.tool decorator")


def test_find_tool_functions_ignore_other_decorators():
    """Test: Ignorar funciones con otros decoradores."""
    code = """
@staticmethod
def my_function():
    pass

@tool
def tool_function():
    pass
"""
    tree = ast.parse(code)
    functions = AST_Inspector.find_tool_functions(tree)
    
    assert len(functions) == 1
    assert functions[0].name == "tool_function"
    print("✓ Test passed: find_tool_functions ignores other decorators")


def test_extract_function_info_basic():
    """Test: Extraer información básica de una función."""
    code = """
@tool
def my_function(param1: str, param2: int) -> bool:
    '''This is a docstring with more than 10 characters.'''
    return True
"""
    tree = ast.parse(code)
    functions = AST_Inspector.find_tool_functions(tree)
    func_info = AST_Inspector.extract_function_info(functions[0])
    
    assert func_info.name == "my_function"
    assert func_info.docstring == "This is a docstring with more than 10 characters."
    assert len(func_info.parameters) == 2
    assert func_info.parameters[0].name == "param1"
    assert func_info.parameters[0].type_hint == "str"
    assert func_info.parameters[0].is_self_or_cls == False
    assert func_info.parameters[1].name == "param2"
    assert func_info.parameters[1].type_hint == "int"
    assert func_info.return_hint == "bool"
    assert func_info.line_number > 0  # Line number should be positive
    print("✓ Test passed: extract_function_info extracts all information correctly")


def test_extract_function_info_self_parameter():
    """Test: Identificar correctamente parámetro 'self'."""
    code = """
@tool
def my_method(self, param1: str) -> None:
    '''A method with self parameter.'''
    pass
"""
    tree = ast.parse(code)
    functions = AST_Inspector.find_tool_functions(tree)
    func_info = AST_Inspector.extract_function_info(functions[0])
    
    assert len(func_info.parameters) == 2
    assert func_info.parameters[0].name == "self"
    assert func_info.parameters[0].is_self_or_cls == True
    assert func_info.parameters[1].name == "param1"
    assert func_info.parameters[1].is_self_or_cls == False
    print("✓ Test passed: extract_function_info identifies 'self' parameter")


def test_extract_function_info_cls_parameter():
    """Test: Identificar correctamente parámetro 'cls'."""
    code = """
@tool
def my_classmethod(cls, param1: str) -> None:
    '''A classmethod with cls parameter.'''
    pass
"""
    tree = ast.parse(code)
    functions = AST_Inspector.find_tool_functions(tree)
    func_info = AST_Inspector.extract_function_info(functions[0])
    
    assert len(func_info.parameters) == 2
    assert func_info.parameters[0].name == "cls"
    assert func_info.parameters[0].is_self_or_cls == True
    assert func_info.parameters[1].name == "param1"
    assert func_info.parameters[1].is_self_or_cls == False
    print("✓ Test passed: extract_function_info identifies 'cls' parameter")


def test_extract_function_info_no_docstring():
    """Test: Manejar función sin docstring."""
    code = """
@tool
def my_function(param1: str) -> None:
    pass
"""
    tree = ast.parse(code)
    functions = AST_Inspector.find_tool_functions(tree)
    func_info = AST_Inspector.extract_function_info(functions[0])
    
    assert func_info.docstring is None
    print("✓ Test passed: extract_function_info handles missing docstring")


def test_extract_function_info_no_type_hints():
    """Test: Manejar parámetros sin type hints."""
    code = """
@tool
def my_function(param1, param2):
    '''Function without type hints.'''
    pass
"""
    tree = ast.parse(code)
    functions = AST_Inspector.find_tool_functions(tree)
    func_info = AST_Inspector.extract_function_info(functions[0])
    
    assert func_info.parameters[0].type_hint is None
    assert func_info.parameters[1].type_hint is None
    assert func_info.return_hint is None
    print("✓ Test passed: extract_function_info handles missing type hints")


def test_extract_function_info_no_parameters():
    """Test: Manejar función sin parámetros."""
    code = """
@tool
def my_function() -> str:
    '''Function without parameters.'''
    return "test"
"""
    tree = ast.parse(code)
    functions = AST_Inspector.find_tool_functions(tree)
    func_info = AST_Inspector.extract_function_info(functions[0])
    
    assert len(func_info.parameters) == 0
    assert func_info.return_hint == "str"
    print("✓ Test passed: extract_function_info handles functions without parameters")


if __name__ == "__main__":
    print("\n=== Running AST_Inspector Tests ===\n")
    
    test_find_tool_functions_simple_decorator()
    test_find_tool_functions_module_decorator()
    test_find_tool_functions_ignore_other_decorators()
    test_extract_function_info_basic()
    test_extract_function_info_self_parameter()
    test_extract_function_info_cls_parameter()
    test_extract_function_info_no_docstring()
    test_extract_function_info_no_type_hints()
    test_extract_function_info_no_parameters()
    
    print("\n=== All Tests Passed! ===\n")
