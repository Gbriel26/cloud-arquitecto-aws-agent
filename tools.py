"""Herramientas para CloudArquitecto."""

from strands import tool


@tool
def estimar_costo_lambda(invocaciones: int, memoria_mb: int) -> float:
    """
    Estima el costo mensual de una función Lambda en AWS.
    
    Args:
        invocaciones: Número de invocaciones mensuales
        memoria_mb: Memoria asignada en MB
        
    Returns:
        Costo estimado en USD
    """
    costo_por_invocacion = 0.0000002
    costo_por_gb_segundo = 0.0000166667
    
    costo_invocaciones = invocaciones * costo_por_invocacion
    costo_memoria = (invocaciones * memoria_mb / 1024) * costo_por_gb_segundo
    
    return costo_invocaciones + costo_memoria


@tool
def calcular_instancias_ec2(usuarios: int, carga_por_usuario: float) -> int:
    """
    Calcula el número de instancias EC2 necesarias para una carga de trabajo.
    
    Args:
        usuarios: Número de usuarios concurrentes
        carga_por_usuario: Carga promedio por usuario en CPU
        
    Returns:
        Número de instancias recomendadas
    """
    carga_total = usuarios * carga_por_usuario
    capacidad_por_instancia = 80  # Asumiendo 80% de utilización
    
    instancias = int(carga_total / capacidad_por_instancia) + 1
    return instancias


@tool
def buscar_servicio_aws(nombre: str) -> str:
    """
    Busca información sobre un servicio de AWS por nombre.
    
    Args:
        nombre: Nombre del servicio AWS a buscar
        
    Returns:
        Descripción del servicio encontrado
    """
    servicios = {
        "lambda": "AWS Lambda - Servicio de computación serverless",
        "ec2": "Amazon EC2 - Servidores virtuales en la nube",
        "s3": "Amazon S3 - Almacenamiento de objetos escalable"
    }
    
    return servicios.get(nombre.lower(), f"Servicio '{nombre}' no encontrado")


@tool
def recomendar_instancia(uso: str) -> str:
    """
    Recomienda un tipo de instancia EC2 según el caso de uso específico.

    Esta función analiza el caso de uso proporcionado y retorna la instancia
    EC2 más apropiada para ese escenario, optimizando costo y rendimiento.

    Args:
        uso: Tipo de uso de la instancia. Valores válidos:
            - 'basico': Para cargas de trabajo ligeras y desarrollo
            - 'produccion': Para aplicaciones en producción con carga media
            - 'base de datos': Para bases de datos con alta demanda de memoria

    Returns:
        str: Tipo de instancia EC2 recomendada (ej: 't3.micro', 'm5.large')

    Examples:
        >>> recomendar_instancia('basico')
        't3.micro'
        >>> recomendar_instancia('produccion')
        'm5.large'
        >>> recomendar_instancia('base de datos')
        'r5.4xlarge'
    """
    recomendaciones = {
        'basico': 't3.micro',
        'produccion': 'm5.large',
        'base de datos': 'r5.4xlarge'
    }

    uso_normalizado = uso.lower().strip()
    return recomendaciones.get(uso_normalizado, f"Uso '{uso}' no reconocido. Valores válidos: basico, produccion, base de datos")

