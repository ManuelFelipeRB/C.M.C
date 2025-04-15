import re
from datetime import datetime

class ScaleProtocolParser:
    """
    Clase para analizar datos recibidos de diferentes indicadores de báscula
    Implementa lógica para interpretar formatos comunes de básculas industriales
    """
    def __init__(self, protocol_type="generic"):
        """
        Inicializar el parser con un tipo de protocolo específico
        
        Args:
            protocol_type (str): Tipo de protocolo a utilizar:
                - "generic": Formato genérico (extrae cualquier número)
                - "cardinal": Protocolo Cardinal
                - "rice_lake": Protocolo Rice Lake
                - "toledo": Protocolo Toledo
                - "cas": Protocolo CAS
        """
        self.protocol_type = protocol_type
        self.last_stable_weight = 0
        self.weight_unit = "kg"
        self.status = "unknown"
        
        # Expresiones regulares para diferentes protocolos
        self.patterns = {
            "generic": r'([+-]?\d+(?:\.\d+)?)',  # Cualquier número, posiblemente con signo y decimales
            "cardinal": r'ST,GS,\s+([+-]?\d+(?:\.\d+)?)\s?(\w+)',  # Formato: ST,GS, 1234.5 kg
            "rice_lake": r'G\s+([+-]?\d+(?:\.\d+)?)\s?(\w+)',  # Formato: G  1234.5 kg
            "toledo": r'[SW][TN],\s*([+-]?\d+(?:\.\d+)?)\s?(\w+)',  # Formato: ST, 1234.5 kg o WT, 1234.5 kg
            "cas": r'[WN][TG]\s*([+-]?\d+(?:\.\d+)?)\s?(\w+)',  # Formato: WT 1234.5 kg o NT 1234.5 kg
        }
        
        # Patrones para detectar inestabilidad en la lectura
        self.unstable_patterns = {
            "generic": r'(US|M|MOT)',  # Cualquier indicador de inestabilidad
            "cardinal": r'(US|M|MOT)',
            "rice_lake": r'(US|M|MOT)',
            "toledo": r'(US|M|MOT)',
            "cas": r'(US|M|MOT)',
        }
    
    def parse(self, data):
        """
        Analizar los datos recibidos según el protocolo configurado
        
        Args:
            data (str): Datos recibidos del puerto serial
            
        Returns:
            dict: Información extraída con las siguientes claves:
                - weight: Valor numérico del peso (float)
                - unit: Unidad de medida (str)
                - is_stable: Si la lectura es estable (bool)
                - status: Estado de la lectura (str) - puede ser "stable", "unstable", "motion", "error"
                - raw_data: Datos originales recibidos (str)
        """
        result = {
            "weight": None,
            "unit": self.weight_unit,
            "is_stable": False,
            "status": "error",
            "raw_data": data,
            "timestamp": datetime.now()
        }
        
        # Verificar si hay indicador de inestabilidad
        unstable_pattern = self.unstable_patterns.get(self.protocol_type, self.unstable_patterns["generic"])
        unstable_match = re.search(unstable_pattern, data, re.IGNORECASE)
        
        if unstable_match:
            result["status"] = "unstable"
            # Intentamos extraer el peso de todas formas
        
        # Extraer peso según el protocolo
        pattern = self.patterns.get(self.protocol_type, self.patterns["generic"])
        match = re.search(pattern, data)
        
        if match:
            try:
                weight = float(match.group(1))
                result["weight"] = weight
                
                # Si hay grupo para unidad, usarlo
                if len(match.groups()) > 1 and match.group(2):
                    result["unit"] = match.group(2)
                
                # Si no se detectó inestabilidad, marcar como estable
                if result["status"] == "error":
                    result["status"] = "stable"
                    result["is_stable"] = True
                    self.last_stable_weight = weight
                
                # Actualizar estado
                self.status = result["status"]
                
                return result
            except (ValueError, IndexError):
                # Error al convertir a número
                pass
        
        # Si llegamos aquí, hubo un error en el análisis
        return result
    
    def get_last_stable_weight(self):
        """Obtener el último peso estable registrado"""
        return self.last_stable_weight
    
    @staticmethod
    def get_available_protocols():
        """
        Retorna una lista de protocolos disponibles
        """
        return [
            "generic", 
            "cardinal", 
            "rice_lake", 
            "toledo", 
            "cas"
        ]
    
    @staticmethod
    def format_weight(weight, unit="kg", decimals=2):
        """
        Formatea un peso con una cantidad específica de decimales y unidad
        """
        if weight is None:
            return "0.00 kg"
        
        format_str = f"{{:.{decimals}f}} {unit}"
        return format_str.format(weight)


class WeightRecord:
    """
    Clase para representar un registro de pesaje
    """
    def __init__(self, placa, peso, unidad="kg", proceso=None, 
                fecha=None, estable=True, conductor=None, origen=None, destino=None):
        self.placa = placa
        self.peso = peso
        self.unidad = unidad
        self.proceso = proceso
        self.fecha = fecha if fecha else datetime.now()
        self.estable = estable
        self.conductor = conductor
        self.origen = origen
        self.destino = destino
        self.id = None  # ID en la base de datos
    
    def to_dict(self):
        """Convertir a diccionario para guardar en BD"""
        return {
            "ID": self.id,
            "Placa": self.placa,
            "Peso": self.peso,
            "Unidad": self.unidad,
            "Proceso": self.proceso,
            "Fecha": self.fecha,
            "Estable": self.estable,
            "Conductor": self.conductor,
            "Origen": self.origen,
            "Destino": self.destino
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crear desde un diccionario"""
        record = cls(
            placa=data.get("Placa", ""),
            peso=data.get("Peso", 0),
            unidad=data.get("Unidad", "kg"),
            proceso=data.get("Proceso", ""),
            fecha=data.get("Fecha", datetime.now()),
            estable=data.get("Estable", True),
            conductor=data.get("Conductor", ""),
            origen=data.get("Origen", ""),
            destino=data.get("Destino", "")
        )
        record.id = data.get("ID", None)
        return record