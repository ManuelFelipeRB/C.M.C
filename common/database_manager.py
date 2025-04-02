import pyodbc

class DatabaseManager:
    def __init__(self):
        self.conn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=\\ttrafejt2k02\Shared\Safety Program\CEV 2021\BaseDatos\EnturneVehiculosSPITB2.mdb'
    
    def connect(self):
        try:
            return pyodbc.connect(self.conn_str)
        except pyodbc.Error as e:
            print(f"Error de conexión a la base de datos: {e}")
            return None
    
    def fetch_vehicle_data(self, fecha_numerica_excel):
        conn = self.connect()
        if not conn:
            return []
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT ID, Cedula, NombreConductor, Placa, Remolque, 
                GrupoProducto, Producto, Proceso, Cliente, Origen, Destino, Estado 
                FROM BDEnturne 
                WHERE EstadoRegistro = 'Activo' AND Folio = ? 
                ORDER BY Consecutivo""", 
                (fecha_numerica_excel,))
            rows = cursor.fetchall()
            return rows
        except pyodbc.Error as e:
            print(f"Error al consultar datos: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def get_vehicle_by_id(self, vehicle_id):
        conn = self.connect()
        if not conn:
            return None
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT ID, Cedula, NombreConductor, Placa, Remolque,
                GrupoProducto, Producto, Proceso, Cliente, Origen, Destino, Estado 
                FROM BDEnturne 
                WHERE ID = ?""", 
                (vehicle_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "ID": row.ID,
                    "Cedula": (row.Cedula),
                    "NombreConductor": row.NombreConductor,
                    "Placa": row.Placa,
                    "Remolque": row.Remolque,
                    "GrupoProducto": row.GrupoProducto,
                    "Producto": row.Producto,
                    "Proceso": row.Proceso,
                    "Cliente": row.Cliente,
                    "Origen": row.Origen,
                    "Destino": row.Destino,
                    "Estado": row.Estado,
                }
            return None
        except pyodbc.Error as e:
            print(f"Error al consultar vehículo: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    def update_vehicle(self, vehicle_data):
        conn = self.connect()
        if not conn:
            return False
        
        cursor = conn.cursor()
        try:
            # Convertir cédula a float para la base de datos
            cedula_value = None
            cedula_str = vehicle_data["Cedula"]
            
            # Verificar el tipo de dato antes de aplicar strip()
            if cedula_str is not None:
                if isinstance(cedula_str, str):
                    # Es una cadena, podemos usar strip()
                    if cedula_str.strip():
                        try:
                            cedula_value = float(cedula_str.replace('.', '').strip())
                        except ValueError:
                            cedula_value = cedula_str
                elif isinstance(cedula_str, (int, float)):
                    # Ya es un número, no necesita conversión
                    cedula_value = float(cedula_str)
                else:
                    # Otro tipo, convertir a string y luego a float si es posible
                    try:
                        cedula_value = float(str(cedula_str))
                    except ValueError:
                        cedula_value = str(cedula_str)
            
            cursor.execute(
                """UPDATE BDEnturne 
                SET Cedula = ?, 
                    NombreConductor = ?, 
                    Placa = ?, 
                    Remolque = ?,
                    GrupoProducto = ?,
                    Producto = ?, 
                    Proceso = ?, 
                    Cliente = ?,
                    Origen = ?,
                    Destino = ?,
                    Estado = ?
                WHERE ID = ?""",
                (cedula_value,
                vehicle_data["NombreConductor"],
                vehicle_data["Placa"],
                vehicle_data["Remolque"],
                vehicle_data["GrupoProducto"],
                vehicle_data["Producto"],
                vehicle_data["Proceso"],
                vehicle_data["Cliente"],
                vehicle_data["Origen"],
                vehicle_data["Destino"],
                vehicle_data["Estado"],
                vehicle_data["ID"])
            )
            conn.commit()
            return True
        except pyodbc.Error as e:
            print(f"Error al actualizar vehículo: {e}")
            return False
        finally:
            cursor.close()
            conn.close()