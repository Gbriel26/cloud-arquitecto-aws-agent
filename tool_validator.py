"""
Sistema de validación de herramientas @tool.

Este módulo proporciona funcionalidad para validar que las funciones decoradas
con @tool cumplan con estándares de calidad de código (docstrings y type hints).
"""

from dataclasses import dataclass


@dataclass
class Parameter_Info:
    """Información de un parámetro de función."""
    name: str
    type_hint: str | None
    is_self_or_cls: bool


@dataclass
class Function_Info:
    """Información extraída de una función @tool."""
    name: str
    docstring: str | None
    parameters: list[Parameter_Info]
    return_hint: str | None
    line_number: int


@dataclass
class Validation_Error:
    """Error de validación encontrado en una función."""
    function_name: str
    line_number: int
    error_type: str  # "docstring", "parameter_hint", "return_hint"
    message: str


@dataclass
class Validation_Result:
    """Resultado completo de la validación."""
    total_functions: int
    functions_with_errors: int
    errors: list[Validation_Error]
    
    def has_errors(self) -> bool:
        """
        Retorna True si hay errores de validación.
        
        Returns:
            bool: True si la lista de errores no está vacía, False en caso contrario
        """
        return len(self.errors) > 0
    
    def group_by_function(self) -> dict[str, list[Validation_Error]]:
        """
        Agrupa errores por nombre de función.
        
        Returns:
            dict[str, list[Validation_Error]]: Diccionario donde las claves son
                nombres de funciones y los valores son listas de errores para
                esa función
        """
        grouped = {}
        for error in self.errors:
            if error.function_name not in grouped:
                grouped[error.function_name] = []
            grouped[error.function_name].append(error)
        return grouped


import ast


class AST_Inspector:
    """Extrae información de funciones usando el árbol AST."""
    
    @staticmethod
    def find_tool_functions(tree: ast.Module) -> list[ast.FunctionDef]:
        """
        Encuentra todas las funciones decoradas con @tool.
        
        Identifica funciones con decorador @tool en dos formatos:
        - Decorador simple: @tool
        - Decorador con módulo: @strands.tool (o cualquier módulo)
        
        Args:
            tree: Árbol AST del módulo a analizar
            
        Returns:
            list[ast.FunctionDef]: Lista de nodos de funciones decoradas con @tool
        """
        tool_functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    # Caso 1: Decorador simple @tool
                    if isinstance(decorator, ast.Name) and decorator.id == "tool":
                        tool_functions.append(node)
                        break
                    # Caso 2: Decorador con módulo @module.tool
                    elif isinstance(decorator, ast.Attribute) and decorator.attr == "tool":
                        tool_functions.append(node)
                        break
        
        return tool_functions
    
    @staticmethod
    def extract_function_info(func_node: ast.FunctionDef) -> Function_Info:
        """
        Extrae información relevante de un nodo de función.
        
        Extrae nombre, docstring, parámetros con type hints, return type hint
        y número de línea. Maneja AttributeError con valores por defecto seguros.
        
        Args:
            func_node: Nodo AST de la función a analizar
            
        Returns:
            Function_Info: Objeto con toda la información extraída de la función
        """
        # Extraer nombre de función
        name = func_node.name
        
        # Extraer docstring
        docstring = ast.get_docstring(func_node)
        
        # Extraer parámetros
        parameters = []
        try:
            for arg in func_node.args.args:
                param_name = arg.arg
                
                # Identificar si es self o cls
                is_self_or_cls = param_name in ('self', 'cls')
                
                # Extraer type hint
                type_hint = None
                if arg.annotation is not None:
                    try:
                        type_hint = ast.unparse(arg.annotation)
                    except AttributeError:
                        type_hint = None
                
                parameters.append(Parameter_Info(
                    name=param_name,
                    type_hint=type_hint,
                    is_self_or_cls=is_self_or_cls
                ))
        except AttributeError:
            # Si no hay args, usar lista vacía
            parameters = []
        
        # Extraer return type hint
        return_hint = None
        try:
            if func_node.returns is not None:
                return_hint = ast.unparse(func_node.returns)
        except AttributeError:
            return_hint = None
        
        # Extraer número de línea
        line_number = func_node.lineno
        
        return Function_Info(
            name=name,
            docstring=docstring,
            parameters=parameters,
            return_hint=return_hint,
            line_number=line_number
        )



class Validation_Rules:
    """Conjunto de reglas que verifican docstrings y type hints."""
    
    @staticmethod
    def validate_docstring(func_info: Function_Info) -> list[str]:
        """
        Valida la presencia y calidad del docstring.
        
        Verifica que el docstring existe y tiene al menos 10 caracteres.
        
        Args:
            func_info: Información de la función a validar
            
        Returns:
            list[str]: Lista de mensajes de error. Vacía si el docstring es válido.
                Posibles mensajes:
                - "Missing docstring": cuando no hay docstring
                - "Docstring too short (minimum 10 characters)": cuando tiene < 10 chars
        """
        errors = []
        
        # Verificar que docstring existe
        if func_info.docstring is None:
            errors.append("Missing docstring")
        # Verificar longitud mínima
        elif len(func_info.docstring) < 10:
            errors.append("Docstring too short (minimum 10 characters)")
        
        return errors
    
    @staticmethod
    def validate_parameter_hints(func_info: Function_Info) -> list[str]:
        """
        Valida type hints en parámetros.
        
        Verifica que todos los parámetros (excepto self y cls) tienen type hints.
        
        Args:
            func_info: Información de la función a validar
            
        Returns:
            list[str]: Lista de mensajes de error. Vacía si todos los parámetros
                tienen type hints. Cada mensaje tiene el formato:
                "Parameter '{name}' missing type hint"
        """
        errors = []
        
        for param in func_info.parameters:
            # Omitir validación para self y cls
            if param.is_self_or_cls:
                continue
            
            # Verificar que el parámetro tiene type hint
            if param.type_hint is None:
                errors.append(f"Parameter '{param.name}' missing type hint")
        
        return errors
    
    @staticmethod
    def validate_return_hint(func_info: Function_Info) -> list[str]:
        """
        Valida type hint de retorno.
        
        Verifica que la función tiene un return type hint. Acepta "None" como válido.
        
        Args:
            func_info: Información de la función a validar
            
        Returns:
            list[str]: Lista de mensajes de error. Vacía si el return type hint existe.
                Posibles mensajes:
                - "Missing return type hint": cuando no hay return type hint
        """
        errors = []
        
        # Verificar que return type hint existe
        # None (el valor Python) significa que no hay type hint
        # "None" (el string) es un type hint válido
        if func_info.return_hint is None:
            errors.append("Missing return type hint")
        
        return errors



class Tool_Validator:
    """
    Motor de validación que coordina el análisis AST.
    
    Coordina la lectura de archivos, parsing AST, extracción de información
    de funciones y aplicación de reglas de validación.
    """
    
    def __init__(self):
        """
        Inicializa el validador.
        
        Crea instancias de AST_Inspector y Validation_Rules para uso interno.
        """
        self.ast_inspector = AST_Inspector()
        self.validation_rules = Validation_Rules()
    
    def validate_tools_file(self, filepath: str) -> Validation_Result:
        """
        Valida todas las funciones @tool en un archivo.
        
        Lee el archivo, parsea el código usando AST, identifica funciones
        decoradas con @tool, aplica reglas de validación y retorna resultados.
        
        Args:
            filepath: Ruta al archivo Python a validar
            
        Returns:
            Validation_Result: Objeto con estadísticas y lista de errores encontrados.
                Si el archivo no existe o tiene errores de sintaxis, retorna
                resultado vacío con total_functions=0.
                
        Raises:
            No lanza excepciones. Maneja FileNotFoundError y SyntaxError
            internamente y retorna resultados vacíos.
        """
        # Intentar leer el archivo
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source_code = f.read()
        except FileNotFoundError:
            # Archivo no existe - retornar resultado vacío
            return Validation_Result(
                total_functions=0,
                functions_with_errors=0,
                errors=[]
            )
        
        # Intentar parsear el código
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            # Error de sintaxis - retornar resultado vacío
            return Validation_Result(
                total_functions=0,
                functions_with_errors=0,
                errors=[]
            )
        
        # Encontrar todas las funciones @tool
        tool_functions = self.ast_inspector.find_tool_functions(tree)
        total_functions = len(tool_functions)
        
        # Acumular errores
        all_errors = []
        
        # Validar cada función
        for func_node in tool_functions:
            # Extraer información de la función
            func_info = self.ast_inspector.extract_function_info(func_node)
            
            # Aplicar reglas de validación
            docstring_errors = self.validation_rules.validate_docstring(func_info)
            parameter_errors = self.validation_rules.validate_parameter_hints(func_info)
            return_errors = self.validation_rules.validate_return_hint(func_info)
            
            # Convertir mensajes de error a objetos Validation_Error
            for error_msg in docstring_errors:
                all_errors.append(Validation_Error(
                    function_name=func_info.name,
                    line_number=func_info.line_number,
                    error_type="docstring",
                    message=error_msg
                ))
            
            for error_msg in parameter_errors:
                all_errors.append(Validation_Error(
                    function_name=func_info.name,
                    line_number=func_info.line_number,
                    error_type="parameter_hint",
                    message=error_msg
                ))
            
            for error_msg in return_errors:
                all_errors.append(Validation_Error(
                    function_name=func_info.name,
                    line_number=func_info.line_number,
                    error_type="return_hint",
                    message=error_msg
                ))
        
        # Calcular funciones con errores
        functions_with_errors_set = set()
        for error in all_errors:
            functions_with_errors_set.add(error.function_name)
        functions_with_errors = len(functions_with_errors_set)
        
        # Crear y retornar resultado
        return Validation_Result(
            total_functions=total_functions,
            functions_with_errors=functions_with_errors,
            errors=all_errors
        )


import sys
import os


class Validation_Hook:
    """Punto de entrada público para ejecutar la validación."""
    
    @staticmethod
    def run() -> None:
        """
        Ejecuta la validación de herramientas @tool.
        
        Crea una instancia de Tool_Validator, ejecuta la validación del archivo
        tools.py, y muestra advertencias en consola si hay errores. Captura y
        maneja cualquier excepción sin propagarla, garantizando que el agente
        pueda iniciar incluso si la validación falla.
        
        Side effects:
            - Muestra advertencias en consola si hay errores de validación
            - Muestra mensaje de error si ocurre una excepción inesperada
            - Captura y maneja cualquier excepción sin propagarla
        """
        try:
            # Crear instancia de Tool_Validator
            validator = Tool_Validator()
            
            # Ejecutar validación del archivo tools.py
            result = validator.validate_tools_file("tools.py")
            
            # Mostrar advertencias en consola
            Console_Formatter.display_warnings(result)
            
        except Exception as e:
            # Capturar cualquier excepción inesperada
            error_type = type(e).__name__
            error_message = str(e)
            print(f"⚠️  Error inesperado en validación: {error_type}: {error_message}")


class Console_Formatter:
    """Formatea y muestra advertencias en la consola."""
    
    @staticmethod
    def supports_color() -> bool:
        """
        Detecta si el terminal soporta colores ANSI.
        
        Verifica dos condiciones:
        1. stdout es un terminal (no un archivo o pipe)
        2. La variable de entorno TERM no es "dumb"
        
        Returns:
            bool: True si el terminal soporta colores ANSI, False en caso contrario
        """
        # Verificar si stdout es un terminal
        if not sys.stdout.isatty():
            return False
        
        # Verificar que TERM no es "dumb"
        term = os.environ.get('TERM', '')
        if term == 'dumb':
            return False
        
        return True
    
    @staticmethod
    def display_warnings(result: Validation_Result) -> None:
        """
        Muestra advertencias de validación en la consola.
        
        Si no hay errores, muestra mensaje de éxito con ✅.
        Si hay errores, muestra:
        - Encabezado con ⚠️ y separador visual
        - Errores agrupados por función con nombre, línea y lista de errores
        - Separador visual al final
        - Resumen con total de funciones con errores
        
        Aplica colores ANSI si el terminal los soporta:
        - Amarillo para encabezado
        - Rojo para errores
        - Verde para éxito
        
        Args:
            result: Resultado de validación con errores
            
        Side effects:
            Imprime en stdout con formato visual
        """
        # Códigos ANSI para colores
        use_color = Console_Formatter.supports_color()
        
        if use_color:
            YELLOW = '\033[93m'
            RED = '\033[91m'
            GREEN = '\033[92m'
            RESET = '\033[0m'
        else:
            YELLOW = RED = GREEN = RESET = ''
        
        # Si no hay errores, mostrar mensaje de éxito
        if not result.has_errors():
            print(f"{GREEN}✅ Validación exitosa: {result.total_functions} funciones @tool cumplen los estándares{RESET}")
            return
        
        # Mostrar encabezado con separador
        print(f"{YELLOW}⚠️  VALIDACIÓN DE HERRAMIENTAS @tool{RESET}")
        print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        print()
        
        # Agrupar errores por función
        grouped_errors = result.group_by_function()
        
        # Mostrar errores por función
        for function_name, errors in grouped_errors.items():
            # Obtener número de línea del primer error (todos tienen el mismo)
            line_number = errors[0].line_number
            
            print(f"Función: {function_name} (línea {line_number})")
            
            # Listar cada error con símbolo ✗
            for error in errors:
                print(f"  {RED}✗{RESET} {error.message}")
            
            print()
        
        # Mostrar separador final
        print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        # Mostrar resumen
        print(f"{RED}❌ {result.functions_with_errors} de {result.total_functions} funciones tienen errores de validación{RESET}")
