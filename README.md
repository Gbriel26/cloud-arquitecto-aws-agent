# CloudArquitecto 🏗️☁️

**Agente conversacional experto en Amazon Web Services (AWS) potenciado por Amazon Bedrock**

CloudArquitecto es un asistente inteligente especializado en arquitectura de AWS que utiliza Claude 3 Haiku a través de Amazon Bedrock. Diseñado para proporcionar recomendaciones técnicas precisas, estimaciones de costos y mejores prácticas de AWS en español.

---

## 📋 Características

### 🔧 Funcionalidades Principales

- **Agente Conversacional Inteligente**: Basado en Claude 3 Haiku de Anthropic a través de Amazon Bedrock
- **Respuestas en Español**: Comunicación natural y técnica en español
- **Herramientas Especializadas**: Conjunto de funciones para cálculos y recomendaciones de AWS

### 🎯 Módulos Implementados

#### **Módulo 6.2: Validación de Herramientas**
Sistema de validación automática que verifica la calidad del código de las herramientas:
- Validación de docstrings completos
- Verificación de type hints en parámetros y retornos
- Inspección AST (Abstract Syntax Tree) para análisis estático
- Ejecución automática al inicio del agente

#### **Módulo 6.3: Hook de Salida con Firma**
Interceptor de respuestas que añade firma automática:
- Formateo consistente de todas las respuestas
- Firma personalizada: `--- *Respuesta generada por CloudArquitecto*`
- Validación de tipos robusta
- Property-based testing con Hypothesis

#### **Persistencia de Historial**
Sistema de gestión de conversaciones:
- Almacenamiento en formato JSON (`historial.json`)
- Carga automática del historial al iniciar
- Resumen de conversaciones previas
- Seguimiento de interacciones usuario-agente

---

## 🛠️ Herramientas Disponibles

CloudArquitecto incluye las siguientes herramientas especializadas:

### 1. **Estimación de Costos Lambda**
```python
estimar_costo_lambda(invocaciones: int, memoria_mb: int) -> float
```
Calcula el costo mensual estimado de funciones AWS Lambda basándose en invocaciones y memoria asignada.

### 2. **Cálculo de Instancias EC2**
```python
calcular_instancias_ec2(usuarios: int, carga_por_usuario: float) -> int
```
Determina el número óptimo de instancias EC2 necesarias según usuarios concurrentes y carga.

### 3. **Búsqueda de Servicios AWS**
```python
buscar_servicio_aws(nombre: str) -> str
```
Proporciona información sobre servicios de AWS (Lambda, EC2, S3, etc.).

### 4. **Recomendación de Instancias EC2**
```python
recomendar_instancia(uso: str) -> str
```
Recomienda el tipo de instancia EC2 más apropiado según el caso de uso:
- `'basico'` → `t3.micro` (desarrollo y cargas ligeras)
- `'produccion'` → `m5.large` (aplicaciones en producción)
- `'base de datos'` → `r5.4xlarge` (bases de datos con alta demanda de memoria)

---

## 🚀 Instalación

### Prerrequisitos

- Python 3.8 o superior
- Cuenta de AWS con acceso a Amazon Bedrock
- Credenciales de AWS configuradas

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd CloudArquitecto
```

2. **Crear entorno virtual (recomendado)**
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**

Copia el archivo de ejemplo y configura tus credenciales:
```bash
cp .env.example .env
```

Edita el archivo `.env` con tus credenciales de AWS:
```env
# AWS Bedrock Configuration
AWS_ACCESS_KEY_ID=tu_access_key_aqui
AWS_SECRET_ACCESS_KEY=tu_secret_key_aqui
AWS_REGION=us-east-1

# Optional: Si usas otros proveedores
OPENAI_API_KEY=tu_openai_api_key_aqui
ANTHROPIC_API_KEY=tu_anthropic_api_key_aqui
```

5. **Verificar acceso a Amazon Bedrock**

Asegúrate de que tu cuenta de AWS tiene habilitado el acceso a Amazon Bedrock y al modelo Claude 3 Haiku:
- Región: `us-east-1` (o la región configurada)
- Modelo: `anthropic.claude-3-haiku-20240307-v1:0`

---

## 💻 Uso

### Ejecutar el Agente

```bash
python agent.py
```

### Ejemplo de Conversación

```
===================================
=== CloudArquitecto esta listo ===
===================================
Escribe 'salir' para terminar.

Historial cargado: 5 conversaciones previas

Tu: ¿Qué instancia EC2 recomiendas para una base de datos?

CloudArquitecto esta pensando...

CloudArquitecto: Para una base de datos, te recomiendo usar una instancia r5.4xlarge. 
Este tipo de instancia está optimizada para cargas de trabajo con alta demanda de memoria, 
lo cual es ideal para bases de datos que requieren acceso rápido a grandes conjuntos de datos.

--- *Respuesta generada por CloudArquitecto*

Tu: salir
¡Hasta luego!
```

### Comandos Disponibles

- Escribe tu pregunta o solicitud en lenguaje natural
- Escribe `salir` para terminar la sesión
- El historial se guarda automáticamente en `historial.json`

---

## 📁 Estructura del Proyecto

```
CloudArquitecto/
├── agent.py                    # Agente principal con bucle de conversación
├── tools.py                    # Herramientas especializadas de AWS
├── history_manager.py          # Gestión de persistencia de historial
├── tool_validator.py           # Validación de calidad de herramientas
├── requirements.txt            # Dependencias del proyecto
├── .env.example               # Plantilla de configuración
├── historial.json             # Historial de conversaciones (generado)
├── README.md                  # Este archivo
└── .kiro/                     # Especificaciones y documentación
    └── specs/
        ├── tool-validation-hook/
        └── output-hook-formatter/
```

---

## 🧪 Testing

El proyecto incluye tests exhaustivos usando pytest y property-based testing con Hypothesis.

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Tests de property-based testing
pytest test_formatear_respuesta_properties.py

# Tests con cobertura
pytest --cov=. --cov-report=html
```

### Property-Based Tests

Los tests basados en propiedades verifican comportamientos universales:
- **Property 1**: Concatenación correcta de firma para cualquier string
- **Property 2**: Validación de tipos con TypeError para inputs no-string
- Configuración: 100 ejemplos por propiedad

---

## 🔒 Seguridad

- **Credenciales**: Nunca subas el archivo `.env` al repositorio
- **AWS IAM**: Usa políticas de IAM con permisos mínimos necesarios
- **Bedrock**: Asegúrate de tener habilitado el acceso a Amazon Bedrock en tu región
- **Validación**: Todas las herramientas pasan validación de calidad automática

---

## 📚 Documentación Adicional

### Especificaciones Técnicas

- [Tool Validation Hook](/.kiro/specs/tool-validation-hook/) - Documentación del módulo de validación
- [Output Hook Formatter](/.kiro/specs/output-hook-formatter/) - Documentación del módulo de formateo

### Recursos de AWS

- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Claude 3 Models](https://www.anthropic.com/claude)
- [AWS SDK for Python (Boto3)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-herramienta`)
3. Asegúrate de que tus herramientas pasen la validación
4. Commit tus cambios (`git commit -m 'Añadir nueva herramienta'`)
5. Push a la rama (`git push origin feature/nueva-herramienta`)
6. Abre un Pull Request

### Estándares de Código

- Todas las funciones `@tool` deben tener docstrings completos
- Type hints obligatorios en parámetros y retornos
- Tests para nuevas funcionalidades
- Código en español para consistencia

---

## 📝 Licencia

Este proyecto es parte de un curso educativo sobre agentes de IA y Amazon Bedrock.

---

## 👥 Autores

Desarrollado como parte del aprendizaje de Strands Agents y Amazon Bedrock.

---

## 🐛 Reporte de Issues

Si encuentras algún problema o tienes sugerencias:

1. Verifica que tus credenciales de AWS estén correctamente configuradas
2. Asegúrate de tener acceso a Amazon Bedrock en tu región
3. Revisa los logs para mensajes de error específicos
4. Abre un issue con detalles del problema

---

## 🎓 Aprendizaje

Este proyecto implementa conceptos avanzados de:
- Agentes conversacionales con LLMs
- Amazon Bedrock y Claude 3
- Validación estática de código con AST
- Property-based testing
- Hooks y middleware patterns
- Persistencia de datos en JSON

---

**¡Gracias por usar CloudArquitecto!** ☁️🚀
