"""
Módulo History_Manager para gestionar la persistencia del historial de conversación.

Este módulo proporciona la clase History_Manager que permite guardar y cargar
el historial de conversaciones entre el usuario y el agente CloudArquitecto
en un archivo JSON estructurado.
"""

import json
import os
from datetime import datetime


class History_Manager:
    """
    Gestiona la persistencia del historial de conversación.
    
    Attributes:
        history_file (str): Ruta al archivo JSON de historial
        history (list): Lista de entradas de conversación en memoria
    """
    
    def __init__(self, history_file: str = "historial.json"):
        """
        Inicializa el gestor de historial.
        
        Args:
            history_file: Nombre del archivo JSON (default: "historial.json")
        """
        self.history_file = history_file
        self.history = []
    
    def _create_entry(self, pregunta: str, respuesta: str) -> dict:
        """
        Crea un objeto Conversation_Entry.
        
        Args:
            pregunta: Texto de la pregunta
            respuesta: Texto de la respuesta
        
        Returns:
            dict con estructura: {
                "timestamp": str (ISO 8601),
                "pregunta": str,
                "respuesta": str
            }
        """
        timestamp = datetime.now().isoformat()
        return {
            "timestamp": timestamp,
            "pregunta": pregunta,
            "respuesta": respuesta
        }

    def _write_history(self) -> bool:
        """
        Escribe self.history al archivo JSON.

        Returns:
            bool: True si escritura exitosa, False si error

        Side effects:
            - Escribe archivo con encoding UTF-8
            - Usa indentación de 2 espacios
        """
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
            return True
        except (IOError, PermissionError) as e:
            print(f"⚠️  No se pudo escribir en historial: {e}")
            return False

    def load_history(self) -> dict:
        """
        Carga el historial desde el archivo JSON.
        
        Returns:
            dict con:
                - success (bool): True si carga exitosa
                - count (int): Número de conversaciones cargadas
                - last_date (str): Fecha de última conversación (ISO 8601)
                - message (str): Mensaje descriptivo para mostrar al usuario
        
        Side effects:
            - Carga self.history con las entradas del archivo
            - Crea archivo vacío si no existe
            - Muestra mensaje en consola
        """
        # Caso 1: Archivo no existe (primera sesión)
        if not os.path.exists(self.history_file):
            self.history = []
            self._write_history()  # Crear archivo vacío
            message = "🆕 Primera sesión. Se creará un nuevo historial."
            print(message)
            return {
                "success": True,
                "count": 0,
                "last_date": None,
                "message": message
            }
        
        # Caso 2: Intentar cargar archivo existente
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
            
            # Calcular estadísticas
            count = len(self.history)
            last_date = None
            
            if count > 0:
                last_date = self.history[-1]["timestamp"]
                # Formatear fecha para mostrar (solo fecha y hora, sin microsegundos)
                try:
                    dt = datetime.fromisoformat(last_date)
                    formatted_date = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    formatted_date = last_date
                
                message = f"📚 Historial cargado: {count} conversaciones. Última: {formatted_date}"
            else:
                message = "📚 Historial cargado: 0 conversaciones."
            
            print(message)
            return {
                "success": True,
                "count": count,
                "last_date": last_date,
                "message": message
            }
        
        except json.JSONDecodeError:
            # Caso 3: Archivo corrupto
            message = "⚠️  Historial corrupto. Se creará uno nuevo."
            print(message)
            self.history = []
            self._write_history()  # Sobrescribir con archivo vacío
            return {
                "success": False,
                "count": 0,
                "last_date": None,
                "message": message
            }
        
        except (IOError, PermissionError) as e:
            # Caso 4: Error de lectura (permisos)
            message = f"⚠️  No se pudo leer historial: {e}"
            print(message)
            self.history = []
            return {
                "success": False,
                "count": 0,
                "last_date": None,
                "message": message
            }

    def save_entry(self, pregunta: str, respuesta: str) -> bool:
        """
        Guarda una nueva entrada de conversación.
        
        Args:
            pregunta: Texto de la pregunta del usuario
            respuesta: Texto de la respuesta del agente
        
        Returns:
            bool: True si guardado exitoso, False si hubo error
        
        Side effects:
            - Agrega entrada a self.history
            - Escribe archivo JSON actualizado
            - Muestra advertencia en consola si hay error
        """
        try:
            entry = self._create_entry(pregunta, respuesta)
            self.history.append(entry)
            return self._write_history()
        except Exception as e:
            print(f"⚠️  No se pudo guardar en historial: {e}")
            return False
