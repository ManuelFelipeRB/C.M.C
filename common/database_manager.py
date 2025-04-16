import pyodbc
import flet as ft

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
                SELECT ID, Consecutivo, FechaEnturne, HoraEnturne, Cedula, NombreConductor, 
                Placa, Remolque, GrupoProducto, Producto, Proceso, Cliente, Origen, Destino, 
                Estado, Transportador, Folio, FechaBasculaEntrada, HoraBasculaEntrada,
                FechaBasculaSalida, HoraBasculaSalida, Manifiesto, GUT, Ejes, BasculaOUT,
                BasculaIN, PesoEntrada, Tara, PesoSalida, FechaEnvio, HoraEnvio, 
                Precalentamiento, DobleCiclo, TipoEmbalaje
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
                SELECT ID, Consecutivo, FechaEnturne, HoraEnturne, Cedula, NombreConductor, 
                Placa, Remolque, GrupoProducto, Producto, Proceso, Cliente, Origen, Destino, 
                Estado, Transportador, Folio, FechaBasculaEntrada, HoraBasculaEntrada,
                FechaBasculaSalida, HoraBasculaSalida, Manifiesto, GUT, Ejes, BasculaOUT,
                BasculaIN, PesoEntrada, Tara, PesoSalida, FechaEnvio, HoraEnvio, 
                Precalentamiento, DobleCiclo, TipoEmbalaje
                FROM BDEnturne 
                WHERE ID = ?""", 
                (vehicle_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "ID": row.ID,
                    "Consecutivo": row.Consecutivo if hasattr(row, 'Consecutivo') else None,
                    "FechaEnturne": row.FechaEnturne if hasattr(row, 'FechaEnturne') else None,
                    "HoraEnturne": row.HoraEnturne if hasattr(row, 'HoraEnturne') else None,
                    "Cedula": row.Cedula,
                    "NombreConductor": row.NombreConductor,
                    "Placa": row.Placa,
                    "Remolque": row.Remolque,
                    "GrupoProducto": row.GrupoProducto,
                    "Producto": row.Producto,
                    "Proceso": row.Proceso,
                    "Cliente": row.Cliente,
                    "Origen": row.Origen if hasattr(row, 'Origen') else None,
                    "Destino": row.Destino if hasattr(row, 'Destino') else None,
                    "Estado": row.Estado,
                    "Transportador": row.Transportador if hasattr(row, 'Transportador') else None,
                    "Folio": row.Folio if hasattr(row, 'Folio') else None,
                    "FechaBasculaEntrada": row.FechaBasculaEntrada if hasattr(row, 'FechaBasculaEntrada') else None,
                    "HoraBasculaEntrada": row.HoraBasculaEntrada if hasattr(row, 'HoraBasculaEntrada') else None,
                    "FechaBasculaSalida": row.FechaBasculaSalida if hasattr(row, 'FechaBasculaSalida') else None,
                    "HoraBasculaSalida": row.HoraBasculaSalida if hasattr(row, 'HoraBasculaSalida') else None,
                    "Manifiesto": row.Manifiesto if hasattr(row, 'Manifiesto') else None,
                    "GUT": row.GUT if hasattr(row, 'GUT') else None,
                    "Ejes": row.Ejes if hasattr(row, 'Ejes') else None,
                    "BasculaOUT": row.BasculaOUT if hasattr(row, 'BasculaOUT') else None,
                    "BasculaIN": row.BasculaIN if hasattr(row, 'BasculaIN') else None,
                    "PesoEntrada": row.PesoEntrada if hasattr(row, 'PesoEntrada') else None,
                    "Tara": row.Tara if hasattr(row, 'Tara') else None,
                    "PesoSalida": row.PesoSalida if hasattr(row, 'PesoSalida') else None,
                    "FechaEnvio": row.FechaEnvio if hasattr(row, 'FechaEnvio') else None,
                    "HoraEnvio": row.HoraEnvio if hasattr(row, 'HoraEnvio') else None,
                    "Precalentamiento": row.Precalentamiento if hasattr(row, 'Precalentamiento') else None,
                    "DobleCiclo": row.DobleCiclo if hasattr(row, 'DobleCiclo') else None,
                    "TipoEmbalaje": row.TipoEmbalaje if hasattr(row, 'TipoEmbalaje') else None
                    
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
            cedula_str = vehicle_data.get("Cedula")
            
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
            
            # Debug: Imprimir los valores para depuración
            print("Datos del vehículo a actualizar:", vehicle_data)
            
            # Vamos a retroceder a los campos básicos que sabemos que funcionan
            # Esta versión se centra solo en los campos que se ven en los datos actualizados
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
                    Estado = ?,
                    Ejes = ?,
                    TipoEmbalaje = ?
                WHERE ID = ?""",
                (
                cedula_value,
                vehicle_data.get("NombreConductor"),
                vehicle_data.get("Placa"),
                vehicle_data.get("Remolque"),
                vehicle_data.get("GrupoProducto"),
                vehicle_data.get("Producto"),
                vehicle_data.get("Proceso"),
                vehicle_data.get("Cliente"),
                vehicle_data.get("Origen"),
                vehicle_data.get("Destino"),
                vehicle_data.get("Estado"),
                vehicle_data.get("Ejes"),
                vehicle_data.get("TipoEmbalaje"),
                vehicle_data.get("ID")),
            )
            conn.commit()
            return True
        except pyodbc.Error as e:
            print(f"Error al actualizar vehículo: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
            
    def execute_query_with_condition(self, folio_actual):
        """
        Ejecuta una consulta similar a la de VBA con condiciones específicas.
        
        Args:
            folio_actual: Valor equivalente a Hoja7.Range("C1").value en VBA
        
        Returns:
            Lista de resultados de la consulta
        """
        conn = self.connect()
        if not conn:
            return []
        
        cursor = conn.cursor()
        try:
            query = """
                SELECT ID, Consecutivo, FechaEnturne, HoraEnturne, Cedula, NombreConductor, 
                Placa, Remolque, Estado, Proceso, Producto, Cliente, Transportador, 
                GrupoProducto, Folio, FechaBasculaEntrada, HoraBasculaEntrada, 
                FechaBasculaSalida, HoraBasculaSalida, Manifiesto, GUT, Ejes, BasculaOUT,
                BasculaIN, PesoEntrada, Tara, PesoSalida, FechaEnvio, HoraEnvio, 
                Precalentamiento, DobleCiclo, EjecutadoRNDC, Origen, Destino, TipoEmbalaje
                FROM BDEnturne 
                WHERE ((FechaBasculaSalida = 0) AND (EstadoRegistro <> 'Eliminado') AND (Folio <= ?)) 
                OR ((Folio = ?) AND (Estado = 'Finalizado'))
                ORDER BY Consecutivo
            """
            cursor.execute(query, (folio_actual, folio_actual))
            rows = cursor.fetchall()
            return rows
        except pyodbc.Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            return []
        finally:
            cursor.close()
            conn.close()


class PesajesManager:    
    
    def __init__(self):
        self.conn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=\\ttrafejt2k02\Shared\Safety Program\CEV 2021\BaseDatos\DBIsotanques1\Isotanques.mdb'

    def connect(self):
        try:
            return pyodbc.connect(self.conn_str)
        except pyodbc.Error as e:
            print(f"Error de conexión a la base de datos: {e}")
            return None

    def get_pesajes_by_folio(self, folio):
        conn = self.connect()
        if not conn:
            return []

        cursor = conn.cursor()
        try:
            query = """
                SELECT id, folio, consecutivo, contenedor, producto, fechahorainicio, 
                       pesoinicio, basculainicio, usuarioinicio, fechahorafinal, 
                       pesofinal, basculafinal, usuariofinal, tara, neto, referencia, 
                       clase, terminaltractor
                FROM Pesajes1
                WHERE folio = ?
                ORDER BY consecutivo
            """
            cursor.execute(query, (folio,))
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]

            result = []
            for row in rows:
                result.append({col: getattr(row, col) for col in columns})

            return result
        except pyodbc.Error as e:
            print(f"Error al consultar datos en Pesajes1: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def build_table(self, data):
        if not data:
            return ft.Text("No hay datos disponibles", color="red")

        # Crear encabezados
        columns = [ft.DataColumn(ft.Text(key)) for key in data[0].keys()]

        # Crear filas
        rows = []
        for item in data:
            row = ft.DataRow(
                cells=[ft.DataCell(ft.Text(str(item[key]) if item[key] is not None else "")) for key in item]
            )
            rows.append(row)

        return ft.DataTable(columns=columns, rows=rows)
