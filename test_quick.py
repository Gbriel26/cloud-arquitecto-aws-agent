#!/usr/bin/env python3
"""
Script de prueba rápida para verificar que CloudArquitecto funciona con Haiku
"""

from strands import Agent
from strands.models import BedrockModel

# Configurar el modelo Bedrock (usando Haiku)
bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-haiku-20240307-v1:0"
)

# Prompt simple para prueba
SYSTEM_PROMPT = """
Eres CloudArquitecto, un experto en Amazon Web Services.
Respondes de forma concisa y práctica, siempre en español.
"""

# Crear agente
agent = Agent(
    system_prompt=SYSTEM_PROMPT,
    model=bedrock_model
)

print("🧪 Probando CloudArquitecto con Haiku...")

try:
    # Prueba simple
    respuesta = agent("¿Qué es AWS Lambda?")
    print(f"✅ Respuesta: {respuesta}")
    print("\n🎉 CloudArquitecto funciona correctamente con Haiku!")
    
except Exception as e:
    print(f"❌ Error: {e}")