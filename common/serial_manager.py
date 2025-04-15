# En common/serial_manager.py
import serial
import serial.tools.list_ports
import threading
import time

class SerialManager:
    def __init__(self):
        self.port = None
        self.baudrate = 9600
        self.serial_connection = None
        self.is_connected = False
        
        # Atributos de configuración
        self.bytesize = serial.EIGHTBITS if 'serial' in globals() else 8
        self.parity = serial.PARITY_NONE if 'serial' in globals() else 'N'
        self.stopbits = serial.STOPBITS_ONE if 'serial' in globals() else 1
        self.timeout = 1
        
        # Para manejar callbacks de datos
        self.data_callback = None
        self.read_thread = None
        self.reading_active = False
    
    def get_available_ports(self):
        """Devuelve una lista de puertos COM disponibles"""
        try:
            ports = []
            for port in serial.tools.list_ports.comports():
                ports.append(port.device)
            return ports
        except Exception as e:
            print(f"Error al obtener puertos disponibles: {e}")
            return []
    
    def set_data_callback(self, callback_function):
        """Establece la función de callback que se llamará cuando se reciban datos"""
        self.data_callback = callback_function
        
        # Si estamos conectados y no hay un hilo de lectura activo, iniciarlo
        if self.is_connected and not self.reading_active:
            self.start_reading()
    
    def start_reading(self):
        """Inicia un hilo para leer continuamente del puerto serial"""
        if self.is_connected and self.serial_connection:
            self.reading_active = True
            self.read_thread = threading.Thread(target=self._read_loop)
            self.read_thread.daemon = True  # El hilo se cerrará cuando termine el programa
            self.read_thread.start()
    
    def stop_reading(self):
        """Detiene el hilo de lectura"""
        self.reading_active = False
        if self.read_thread:
            # Esperar a que el hilo termine (con timeout)
            if self.read_thread.is_alive():
                self.read_thread.join(timeout=1.0)
            self.read_thread = None
    
    def _read_loop(self):
        """Bucle que se ejecuta en un hilo separado para leer datos"""
        while self.reading_active and self.is_connected:
            try:
                if self.serial_connection.in_waiting > 0:
                    # Hay datos disponibles para leer
                    data = self.serial_connection.readline().decode('utf-8', errors='replace').strip()
                    if data and self.data_callback:
                        # Llamar al callback con los datos recibidos
                        self.data_callback(data)
                else:
                    # No hay datos, esperar un poco para no consumir CPU
                    time.sleep(0.1)
            except Exception as e:
                print(f"Error reading from serial port: {e}")
                time.sleep(1)  # Esperar un poco antes de intentar de nuevo
    
    def connect(self, port):
        """Conecta al puerto especificado"""
        try:
            self.serial_connection = serial.Serial(
                port=port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
                timeout=self.timeout
            )
            self.port = port
            self.is_connected = True
            
            # Si hay un callback de datos registrado, iniciar la lectura
            if self.data_callback:
                self.start_reading()
                
            return True
        except Exception as e:
            print(f"Error al conectar: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Desconecta el puerto serial"""
        # Primero detener la lectura
        self.stop_reading()
        
        # Luego cerrar la conexión
        if self.serial_connection and self.is_connected:
            self.serial_connection.close()
            self.is_connected = False
    
    def get_connection_settings(self):
        """Devuelve un diccionario con la configuración actual de la conexión"""
        return {
            "port": self.port,
            "baudrate": self.baudrate,
            "bytesize": self.bytesize,
            "parity": self.parity,
            "stopbits": self.stopbits,
            "timeout": self.timeout,
            "is_connected": self.is_connected
        }