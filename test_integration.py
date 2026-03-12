"""
Test de integración completa para verificar el flujo end-to-end del historial.
"""

import os
import json
import pytest
from history_manager import History_Manager


class TestCompleteIntegration:
    """Tests de integración completa del sistema de historial."""
    
    def setup_method(self):
        """Limpia archivos de test antes de cada prueba."""
        self.test_file = "test_integration_historial.json"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def teardown_method(self):
        """Limpia archivos de test después de cada prueba."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_full_conversation_flow(self):
        """
        Test de integración: Simula el flujo completo del agente.
        
        Flujo:
        1. Primera sesión: cargar historial (debe crear archivo nuevo)
        2. Simular 3 conversaciones y guardarlas
        3. Segunda sesión: cargar historial (debe mostrar 3 conversaciones)
        4. Agregar 2 conversaciones más
        5. Tercera sesión: verificar que hay 5 conversaciones en total
        """
        # === PRIMERA SESIÓN ===
        print("\n=== PRIMERA SESIÓN ===")
        mgr1 = History_Manager(self.test_file)
        summary1 = mgr1.load_history()
        
        # Verificar primera sesión
        assert summary1["success"] == True
        assert summary1["count"] == 0
        assert summary1["last_date"] is None
        assert "Primera sesión" in summary1["message"]
        assert os.path.exists(self.test_file)
        
        # Simular 3 conversaciones
        conversations_session1 = [
            ("¿Qué es S3?", "S3 es un servicio de almacenamiento de objetos en AWS..."),
            ("¿Cómo funciona Lambda?", "Lambda es un servicio de cómputo serverless..."),
            ("¿Cuánto cuesta DynamoDB?", "DynamoDB cobra por lectura/escritura y almacenamiento...")
        ]
        
        for pregunta, respuesta in conversations_session1:
            result = mgr1.save_entry(pregunta, respuesta)
            assert result == True
        
        # Verificar que se guardaron en memoria
        assert len(mgr1.history) == 3
        
        # === SEGUNDA SESIÓN ===
        print("\n=== SEGUNDA SESIÓN ===")
        mgr2 = History_Manager(self.test_file)
        summary2 = mgr2.load_history()
        
        # Verificar que se cargaron las 3 conversaciones
        assert summary2["success"] == True
        assert summary2["count"] == 3
        assert summary2["last_date"] is not None
        assert "3 conversaciones" in summary2["message"]
        assert len(mgr2.history) == 3
        
        # Verificar que las conversaciones son las correctas
        assert mgr2.history[0]["pregunta"] == "¿Qué es S3?"
        assert mgr2.history[1]["pregunta"] == "¿Cómo funciona Lambda?"
        assert mgr2.history[2]["pregunta"] == "¿Cuánto cuesta DynamoDB?"
        
        # Agregar 2 conversaciones más
        conversations_session2 = [
            ("¿Qué es EC2?", "EC2 es un servicio de cómputo en la nube..."),
            ("¿Cómo configurar VPC?", "VPC permite crear redes virtuales aisladas...")
        ]
        
        for pregunta, respuesta in conversations_session2:
            result = mgr2.save_entry(pregunta, respuesta)
            assert result == True
        
        # Verificar que ahora hay 5 conversaciones en memoria
        assert len(mgr2.history) == 5
        
        # === TERCERA SESIÓN ===
        print("\n=== TERCERA SESIÓN ===")
        mgr3 = History_Manager(self.test_file)
        summary3 = mgr3.load_history()
        
        # Verificar que se cargaron las 5 conversaciones
        assert summary3["success"] == True
        assert summary3["count"] == 5
        assert summary3["last_date"] is not None
        assert "5 conversaciones" in summary3["message"]
        assert len(mgr3.history) == 5
        
        # Verificar orden cronológico
        assert mgr3.history[0]["pregunta"] == "¿Qué es S3?"
        assert mgr3.history[4]["pregunta"] == "¿Cómo configurar VPC?"
        
        # Verificar que last_date corresponde a la última conversación
        assert summary3["last_date"] == mgr3.history[-1]["timestamp"]
        
        print("\n✅ Test de integración completo exitoso!")
    
    def test_error_resilience_during_conversation(self):
        """
        Test de resiliencia: Verificar que errores de I/O no interrumpen el flujo.
        """
        mgr = History_Manager(self.test_file)
        mgr.load_history()
        
        # Guardar una conversación exitosamente
        result1 = mgr.save_entry("pregunta1", "respuesta1")
        assert result1 == True
        assert len(mgr.history) == 1
        
        # Simular error de escritura (hacer el archivo de solo lectura)
        os.chmod(self.test_file, 0o444)  # Solo lectura
        
        try:
            # Intentar guardar otra conversación (debería fallar pero no crashear)
            result2 = mgr.save_entry("pregunta2", "respuesta2")
            assert result2 == False  # Debe retornar False
            
            # La entrada debe estar en memoria aunque no se guardó en disco
            assert len(mgr.history) == 2
            assert mgr.history[1]["pregunta"] == "pregunta2"
        finally:
            # Restaurar permisos
            os.chmod(self.test_file, 0o644)
        
        # Siguiente guardado debe funcionar normalmente
        result3 = mgr.save_entry("pregunta3", "respuesta3")
        assert result3 == True
        assert len(mgr.history) == 3
        
        print("\n✅ Test de resiliencia exitoso!")
    
    def test_utf8_preservation_across_sessions(self):
        """
        Test de preservación UTF-8: Verificar que caracteres especiales
        se preservan correctamente a través de múltiples sesiones.
        """
        # Primera sesión: guardar con caracteres especiales
        mgr1 = History_Manager(self.test_file)
        mgr1.load_history()
        
        preguntas_especiales = [
            "¿Cómo funciona λ (Lambda)? 🚀",
            "¿Qué es Ñoño en español? 😊",
            "Símbolos: €, £, ¥, ₹, 中文, 日本語"
        ]
        
        respuestas_especiales = [
            "Lambda (λ) es serverless 💻",
            "Ñoño tiene la letra Ñ 🇪🇸",
            "Soportamos múltiples monedas e idiomas ✨"
        ]
        
        for p, r in zip(preguntas_especiales, respuestas_especiales):
            mgr1.save_entry(p, r)
        
        # Segunda sesión: cargar y verificar
        mgr2 = History_Manager(self.test_file)
        mgr2.load_history()
        
        assert len(mgr2.history) == 3
        
        for i, (p, r) in enumerate(zip(preguntas_especiales, respuestas_especiales)):
            assert mgr2.history[i]["pregunta"] == p
            assert mgr2.history[i]["respuesta"] == r
        
        print("\n✅ Test de preservación UTF-8 exitoso!")
    
    def test_json_structure_validation(self):
        """
        Test de estructura JSON: Verificar que el archivo tiene la estructura correcta.
        """
        mgr = History_Manager(self.test_file)
        mgr.load_history()
        
        # Guardar algunas conversaciones
        mgr.save_entry("test1", "response1")
        mgr.save_entry("test2", "response2")
        
        # Leer archivo directamente y validar estructura
        with open(self.test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Debe ser un array
        assert isinstance(data, list)
        assert len(data) == 2
        
        # Cada entrada debe tener exactamente 3 campos
        for entry in data:
            assert isinstance(entry, dict)
            assert len(entry) == 3
            assert "timestamp" in entry
            assert "pregunta" in entry
            assert "respuesta" in entry
            assert isinstance(entry["timestamp"], str)
            assert isinstance(entry["pregunta"], str)
            assert isinstance(entry["respuesta"], str)
        
        # Verificar indentación de 2 espacios
        with open(self.test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert '  {' in content  # 2 espacios antes de {
        assert '    "' in content  # 4 espacios para campos
        
        print("\n✅ Test de estructura JSON exitoso!")
    
    def test_timestamp_chronological_order(self):
        """
        Test de orden cronológico: Verificar que los timestamps están en orden.
        """
        import time
        
        mgr = History_Manager(self.test_file)
        mgr.load_history()
        
        # Guardar 5 conversaciones con pequeñas pausas
        for i in range(5):
            mgr.save_entry(f"pregunta{i}", f"respuesta{i}")
            time.sleep(0.01)  # Pequeña pausa para asegurar timestamps diferentes
        
        # Verificar que los timestamps están en orden cronológico
        timestamps = [entry["timestamp"] for entry in mgr.history]
        
        for i in range(len(timestamps) - 1):
            assert timestamps[i] < timestamps[i + 1], \
                f"Timestamps no están en orden: {timestamps[i]} >= {timestamps[i + 1]}"
        
        print("\n✅ Test de orden cronológico exitoso!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
