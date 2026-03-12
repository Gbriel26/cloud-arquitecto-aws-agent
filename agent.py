from strands import Agent
from history_manager import History_Manager
from tool_validator import Validation_Hook

# Ejecutar validación de herramientas @tool al inicio
# Esto verifica que todas las funciones decoradas con @tool cumplan
# con estándares de calidad (docstrings y type hints)
Validation_Hook.run()

# Constante de firma para las respuestas del agente
SIGNATURE = "\n\n--- *Respuesta generada por CloudArquitecto*"

def formatear_respuesta(output_text: str) -> str:
    """
    Formatea el texto de salida del agente añadiendo una firma al final.
    
    Esta función intercepta las respuestas generadas por el agente y añade
    automáticamente una firma consistente que identifica al agente CloudArquitecto.
    El texto original se preserva sin modificaciones, y la firma se concatena
    al final del mismo.
    
    Args:
        output_text: El texto de respuesta generado por el agente. Debe ser
                     de tipo str. Puede ser un string vacío o contener múltiples
                     líneas con saltos de línea.
    
    Returns:
        El texto de respuesta con la firma añadida al final. El formato es:
        {output_text}{SIGNATURE}
    
    Raises:
        TypeError: Si output_text no es de tipo str. El mensaje de error
                   incluye el tipo recibido para facilitar el debugging.
    
    Examples:
        >>> formatear_respuesta("Hola mundo")
        'Hola mundo\\n\\n--- *Respuesta generada por CloudArquitecto*'
        
        >>> formatear_respuesta("")
        '\\n\\n--- *Respuesta generada por CloudArquitecto*'
    """
    # Validación de tipo
    if not isinstance(output_text, str):
        raise TypeError(
            f"output_text debe ser de tipo str, se recibió {type(output_text).__name__}"
        )
    
    # Concatenar el texto de entrada con la firma
    return output_text + SIGNATURE

# 1. Definimos las instrucciones
# 1. Definimos las instrucciones
SYSTEM_PROMPT = """
Eres CloudArquitecto, un experto en Amazon Web Services.
Respondes de forma concisa y practica, siempre en español.
Cuando alguien te pregunta algo tecnico, das ejemplos concretos.
"""

# 2. Inicializamos el agente con el modelo Haiku
agent = Agent(
    system_prompt=SYSTEM_PROMPT,
    model="anthropic.claude-3-haiku-20240307-v1:0",
    output_hooks=[formatear_respuesta]
)

print("=" * 35)
print("=== CloudArquitecto esta listo ===")
print("=" * 35)
print("Escribe 'salir' para terminar.\n")

# Inicializar History_Manager y cargar historial
history_mgr = History_Manager()
summary = history_mgr.load_history()
print()  # Línea en blanco después del resumen

# 3. Bucle de conversación
while True:
    user_input = input("Tu: ").strip()
    
    if not user_input:
        continue
        
    if user_input.lower() == "salir":
        print("¡Hasta luego!")
        break
        
    print("\nCloudArquitecto esta pensando...")
    
    try:
        # En esta version de Strands, simplemente llamamos al agente asi:
        respuesta = agent(user_input) 
        print(f"\nCloudArquitecto: {respuesta}\n")
        
        # Guardar en historial
        history_mgr.save_entry(user_input, respuesta)
        
    except Exception as e:
        print(f"\nOcurrio un detalle tecnico: {e}")
        print("Revisa la conexion con AWS.\n")
