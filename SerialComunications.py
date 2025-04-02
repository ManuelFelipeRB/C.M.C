import serial
import serial.tools.list_ports
import threading
import time

class SerialPortManager:
    def __init__(self):
        self.port = None
        self.baudrate = 9600
        self.is_connected = False
        self.serial_thread = None
        self.stop_thread = False
        self.data_callback = None

    def get_available_ports(self):
        """Get a list of available serial ports"""
        return [port.device for port in serial.tools.list_ports.comports()]

    def connect(self, port_name):
        """Connect to a specific serial port"""
        try:
            self.port = serial.Serial(
                port=port_name, 
                baudrate=self.baudrate, 
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            self.is_connected = True
            self.start_reading_thread()
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from the serial port"""
        self.stop_thread = True
        if self.serial_thread:
            self.serial_thread.join()
        
        if self.port and self.port.is_open:
            self.port.close()
        
        self.is_connected = False
        self.port = None

    def start_reading_thread(self):
        """Start a thread to continuously read serial data"""
        self.stop_thread = False
        self.serial_thread = threading.Thread(target=self._read_data)
        self.serial_thread.daemon = True
        self.serial_thread.start()

    def _read_data(self):
        """Internal method to read data from serial port"""
        while not self.stop_thread and self.port and self.port.is_open:
            try:
                if self.port.in_waiting:
                    data = self.port.readline().decode('utf-8').strip()
                    if self.data_callback and data:
                        self.data_callback(data)
            except Exception as e:
                print(f"Serial read error: {e}")
                break
            time.sleep(0.1)

    def set_data_callback(self, callback):
        """Set a callback function for received data"""
        self.data_callback = callback