"""
Tests para verificar la funcionalidad básica de persistencia del History_Manager.
"""

import os
import json
import pytest
from datetime import datetime
from history_manager import History_Manager


class TestBasicPersistence:
    """Tests para verificar la persistencia básica del historial."""
    
    def setup_method(self):
        """Limpia archivos de test antes de cada prueba."""
        self.test_file = "test_historial.json"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def teardown_method(self):
        """Limpia archivos de test después de cada prueba."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_create_entry_structure(self):
        """Verifica que _create_entry crea la estructura correcta."""
        mgr = History_Manager(self.test_file)
        pregunta = "¿Qué es Lambda?"
        respuesta = "AWS Lambda es un servicio serverless"
        
        entry = mgr._create_entry(pregunta, respuesta)
        
        # Verificar estructura
        assert "timestamp" in entry
        assert "pregunta" in entry
        assert "respuesta" in entry
        assert len(entry) == 3  # Solo 3 campos
        
        # Verificar contenido
        assert entry["pregunta"] == pregunta
        assert entry["respuesta"] == respuesta
    
    def test_timestamp_iso8601_format(self):
        """Verifica que el timestamp está en formato ISO 8601."""
        mgr = History_Manager(self.test_file)
        entry = mgr._create_entry("test", "response")
        
        timestamp = entry["timestamp"]
        
        # Debe poder parsearse como datetime ISO 8601
        parsed = datetime.fromisoformat(timestamp)
        assert isinstance(parsed, datetime)
        
        # Verificar formato básico YYYY-MM-DDTHH:MM:SS
        assert "T" in timestamp
        assert len(timestamp.split("T")) == 2
    
    def test_save_entry_creates_file(self):
        """Verifica que save_entry crea el archivo JSON."""
        mgr = History_Manager(self.test_file)
        
        result = mgr.save_entry("¿Qué es S3?", "S3 es almacenamiento de objetos")
        
        assert result == True
        assert os.path.exists(self.test_file)
    
    def test_save_entry_writes_json(self):
        """Verifica que save_entry escribe JSON válido."""
        mgr = History_Manager(self.test_file)
        
        mgr.save_entry("pregunta1", "respuesta1")
        
        # Leer archivo y verificar que es JSON válido
        with open(self.test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["pregunta"] == "pregunta1"
        assert data[0]["respuesta"] == "respuesta1"
    
    def test_multiple_entries_preserved(self):
        """Verifica que múltiples entradas se preservan en orden."""
        mgr = History_Manager(self.test_file)
        
        # Guardar 3 entradas
        mgr.save_entry("pregunta1", "respuesta1")
        mgr.save_entry("pregunta2", "respuesta2")
        mgr.save_entry("pregunta3", "respuesta3")
        
        # Leer archivo
        with open(self.test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert len(data) == 3
        assert data[0]["pregunta"] == "pregunta1"
        assert data[1]["pregunta"] == "pregunta2"
        assert data[2]["pregunta"] == "pregunta3"
    
    def test_json_indentation(self):
        """Verifica que el JSON usa indentación de 2 espacios."""
        mgr = History_Manager(self.test_file)
        mgr.save_entry("test", "response")
        
        with open(self.test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar indentación de 2 espacios
        assert '  {' in content  # 2 espacios antes de {
        assert '    "timestamp"' in content or '    "pregunta"' in content  # 4 espacios para campos
    
    def test_utf8_characters(self):
        """Verifica que caracteres UTF-8 se preservan correctamente."""
        mgr = History_Manager(self.test_file)
        
        pregunta = "¿Cómo funciona λ en AWS? 🚀"
        respuesta = "AWS Lambda (λ) es serverless 💻"
        
        mgr.save_entry(pregunta, respuesta)
        
        # Leer archivo
        with open(self.test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data[0]["pregunta"] == pregunta
        assert data[0]["respuesta"] == respuesta
    
    def test_roundtrip_persistence(self):
        """Verifica que guardar y cargar preserva los datos exactamente."""
        mgr = History_Manager(self.test_file)
        
        pregunta = "¿Cuánto cuesta DynamoDB?"
        respuesta = "DynamoDB cobra por lectura/escritura y almacenamiento"
        
        # Guardar
        mgr.save_entry(pregunta, respuesta)
        
        # Leer directamente del archivo
        with open(self.test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        last_entry = data[-1]
        assert last_entry["pregunta"] == pregunta
        assert last_entry["respuesta"] == respuesta


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestLoadHistory:
    """Tests para verificar la funcionalidad de load_history."""
    
    def setup_method(self):
        """Limpia archivos de test antes de cada prueba."""
        self.test_file = "test_load_historial.json"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def teardown_method(self):
        """Limpia archivos de test después de cada prueba."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_first_session_no_file(self):
        """Primera sesión debe crear archivo y retornar mensaje apropiado."""
        mgr = History_Manager(self.test_file)
        
        summary = mgr.load_history()
        
        assert summary["success"] == True
        assert summary["count"] == 0
        assert summary["last_date"] is None
        assert "Primera sesión" in summary["message"]
        assert os.path.exists(self.test_file)
        
        # Verificar que el archivo contiene un array vacío
        with open(self.test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert data == []
    
    def test_load_existing_history(self):
        """Cargar historial existente debe retornar estadísticas correctas."""
        # Crear archivo con 3 entradas
        mgr = History_Manager(self.test_file)
        mgr.save_entry("pregunta1", "respuesta1")
        mgr.save_entry("pregunta2", "respuesta2")
        mgr.save_entry("pregunta3", "respuesta3")
        
        # Crear nueva instancia y cargar
        mgr2 = History_Manager(self.test_file)
        summary = mgr2.load_history()
        
        assert summary["success"] == True
        assert summary["count"] == 3
        assert summary["last_date"] is not None
        assert "3 conversaciones" in summary["message"]
        assert len(mgr2.history) == 3
    
    def test_load_empty_history_file(self):
        """Cargar archivo con array vacío debe funcionar correctamente."""
        # Crear archivo con array vacío
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
        
        mgr = History_Manager(self.test_file)
        summary = mgr.load_history()
        
        assert summary["success"] == True
        assert summary["count"] == 0
        assert summary["last_date"] is None
        assert "0 conversaciones" in summary["message"]
    
    def test_corrupted_json_file(self):
        """Archivo corrupto debe manejarse sin crash."""
        # Crear archivo con JSON inválido
        with open(self.test_file, 'w') as f:
            f.write("{invalid json content")
        
        mgr = History_Manager(self.test_file)
        summary = mgr.load_history()
        
        assert summary["success"] == False
        assert summary["count"] == 0
        assert summary["last_date"] is None
        assert "corrupto" in summary["message"].lower()
        
        # Verificar que se creó un archivo nuevo válido
        with open(self.test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert data == []
    
    def test_last_date_calculation(self):
        """Verificar que last_date corresponde a la última conversación."""
        mgr = History_Manager(self.test_file)
        
        # Guardar entradas con pequeña pausa para timestamps diferentes
        import time
        mgr.save_entry("primera", "respuesta1")
        time.sleep(0.01)
        mgr.save_entry("segunda", "respuesta2")
        time.sleep(0.01)
        mgr.save_entry("tercera", "respuesta3")
        
        # Cargar y verificar
        mgr2 = History_Manager(self.test_file)
        summary = mgr2.load_history()
        
        # last_date debe ser el timestamp de la última entrada
        assert summary["last_date"] == mgr2.history[-1]["timestamp"]
        assert summary["last_date"] == mgr2.history[2]["timestamp"]
    
    def test_summary_message_format(self):
        """Verificar que el mensaje de resumen tiene el formato correcto."""
        mgr = History_Manager(self.test_file)
        mgr.save_entry("test", "response")
        
        mgr2 = History_Manager(self.test_file)
        summary = mgr2.load_history()
        
        # Mensaje debe incluir emoji, count y fecha formateada
        assert "📚" in summary["message"]
        assert "1 conversaciones" in summary["message"] or "1 conversación" in summary["message"]
        assert "Última:" in summary["message"]
    
    def test_permission_error_handling(self, monkeypatch):
        """Error de permisos debe manejarse sin crash."""
        # Crear archivo primero
        with open(self.test_file, 'w') as f:
            json.dump([], f)
        
        mgr = History_Manager(self.test_file)
        
        # Simular error de permisos
        original_open = open
        def mock_open(file, mode='r', *args, **kwargs):
            if mode == 'r' and file == self.test_file:
                raise PermissionError("No read permission")
            return original_open(file, mode, *args, **kwargs)
        
        monkeypatch.setattr("builtins.open", mock_open)
        
        summary = mgr.load_history()
        
        assert summary["success"] == False
        assert summary["count"] == 0
        assert "No se pudo leer" in summary["message"]
        assert mgr.history == []  # Debe continuar con historial vacío
    
    def test_history_loaded_into_memory(self):
        """Verificar que load_history carga las entradas en self.history."""
        # Crear historial
        mgr = History_Manager(self.test_file)
        mgr.save_entry("p1", "r1")
        mgr.save_entry("p2", "r2")
        
        # Cargar en nueva instancia
        mgr2 = History_Manager(self.test_file)
        assert mgr2.history == []  # Antes de cargar
        
        mgr2.load_history()
        
        assert len(mgr2.history) == 2
        assert mgr2.history[0]["pregunta"] == "p1"
        assert mgr2.history[1]["pregunta"] == "p2"
