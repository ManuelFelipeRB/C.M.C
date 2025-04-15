import pyodbc
from datetime import datetime

class WeightDatabaseManager:
    """
    Clase para gestionar registros de pesaje en la base de datos
    """
    def __init__(self, db_manager=None):
        """
        Inicializar el gestor de base de datos de pesaje
        
        Args:
            db_manager: Instancia opcional de DatabaseManager existente
                        Si no se proporciona, se crea uno nuevo
        """
        if db_manager:
            self.db_manager = db_manager
        else:
            from common.database_manager import DatabaseManager
            self.db_manager = DatabaseManager()
    
    def save_weight_record(self, weight_record):
        """
        Guardar un registro de pesaje en la base de datos
        
        Args:
            weight_record: Instancia de WeightRecord con los datos a guardar
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
            int: ID del registro creado/actualizado, None si hubo error
        """
        conn = self.db_manager.connect()
        if not conn:
            return False, None
        
        cursor = conn.cursor()
        try:
            # Verificar si ya existe un registro con este ID
            if weight_record.id:
                # Actualizar registro existente
                cursor.execute("""
                    UPDATE BDPesajes 
                    SET Placa = ?, 
                        Peso = ?, 
                        Unidad = ?, 
                        Proceso = ?, 
                        Fecha = ?, 
                        Estable = ?, 
                        Conductor = ?, 
                        Origen = ?, 
                        Destino = ?
                    WHERE ID = ?
                """, (
                    weight_record.placa,
                    weight_record.peso,
                    weight_record.unidad,
                    weight_record.proceso,
                    weight_record.fecha,
                    weight_record.estable,
                    weight_record.conductor,
                    weight_record.origen,
                    weight_record.destino,
                    weight_record.id
                ))
                conn.commit()
                return True, weight_record.id
            else:
                # Verificar si la tabla existe, y crearla si no
                self.ensure_table_exists(cursor)
                
                # Insertar nuevo registro
                cursor.execute("""
                    INSERT INTO BDPesajes 
                    (Placa, Peso, Unidad, Proceso, Fecha, Estable, Conductor, Origen, Destino)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    weight_record.placa,
                    weight_record.peso,
                    weight_record.unidad,
                    weight_record.proceso,
                    weight_record.fecha,
                    weight_record.estable,
                    weight_record.conductor,
                    weight_record.origen,
                    weight_record.destino
                ))
                conn.commit()
                
                # Obtener el ID del registro creado
                cursor.execute("SELECT @@IDENTITY")
                row = cursor.fetchone()
                if row:
                    weight_record.id = row[0]
                    return True, weight_record.id
                
                return True, None
        except pyodbc.Error as e:
            print(f"Error al guardar registro de pesaje: {e}")
            return False, None
        finally:
            cursor.close()
            conn.close()
    
    def ensure_table_exists(self, cursor):
        """
        Asegurarse de que la tabla BDPesajes existe en la base de datos
        
        Args:
            cursor: Cursor de la conexión a la base de datos
        """
        try:
            # Verificar si la tabla existe
            cursor.execute("SELECT TOP 1 * FROM BDPesajes")
            cursor.fetchone()
        except pyodbc.Error:
            # La tabla no existe, crearla
            try:
                cursor.execute("""
                    CREATE TABLE BDPesajes (
                        ID AUTOINCREMENT PRIMARY KEY,
                        Placa TEXT(20),
                        Peso DOUBLE,
                        Unidad TEXT(10),
                        Proceso TEXT(50),
                        Fecha DATETIME,
                        Estable YESNO,
                        Conductor TEXT(100),
                        Origen TEXT(100),
                        Destino TEXT(100)
                    )
                """)
                cursor.commit()
            except pyodbc.Error as e:
                print(f"Error al crear tabla BDPesajes: {e}")
    
    def get_weight_records(self, fecha=None, placa=None, limite=100):
        """
        Obtener registros de pesaje con filtros opcionales
        
        Args:
            fecha: Fecha para filtrar (opcional)
            placa: Placa del vehículo para filtrar (opcional)
            limite: Número máximo de registros a retornar
            
        Returns:
            list: Lista de registros de pesaje
        """
        conn = self.db_manager.connect()
        if not conn:
            return []
        
        cursor = conn.cursor()
        
        try:
            # Construir la consulta según los filtros
            query = "SELECT * FROM BDPesajes WHERE 1=1"
            params = []
            
            if fecha:
                query += " AND Fecha >= ? AND Fecha < DATEADD(day, 1, ?)"
                params.append(fecha)
                params.append(fecha)
            
            if placa:
                query += " AND Placa LIKE ?"
                params.append(f"%{placa}%")
            
            query += " ORDER BY Fecha DESC"
            
            if limite:
                query += f" LIMIT {limite}"
            
            # Ejecutar la consulta
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convertir filas a objetos WeightRecord
            from common.scale_protocols import WeightRecord
            result = []
            for row in rows:
                record = WeightRecord(
                    placa=row.Placa,
                    peso=row.Peso,
                    unidad=row.Unidad,
                    proceso=row.Proceso,
                    fecha=row.Fecha,
                    estable=row.Estable,
                    conductor=row.Conductor,
                    origen=row.Origen,
                    destino=row.Destino
                )
                record.id = row.ID
                result.append(record)
            
            return result
        except pyodbc.Error as e:
            print(f"Error al consultar registros de pesaje: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def get_weight_statistics(self, fecha=None, proceso=None):
        """
        Obtener estadísticas de pesaje (total, promedio, etc.)
        
        Args:
            fecha: Fecha para filtrar (opcional)
            proceso: Proceso para filtrar (opcional)
            
        Returns:
            dict: Diccionario con estadísticas
        """
        conn = self.db_manager.connect()
        if not conn:
            return {
                "total_registros": 0,
                "peso_total": 0,
                "peso_promedio": 0,
                "peso_minimo": 0,
                "peso_maximo": 0
            }
        
        cursor = conn.cursor()
        
        try:
            # Construir la consulta según los filtros
            query = """
                SELECT COUNT(*) as total, 
                       SUM(Peso) as suma, 
                       AVG(Peso) as promedio, 
                       MIN(Peso) as minimo, 
                       MAX(Peso) as maximo 
                FROM BDPesajes 
                WHERE 1=1
            """
            params = []
            
            if fecha:
                query += " AND Fecha >= ? AND Fecha < DATEADD(day, 1, ?)"
                params.append(fecha)
                params.append(fecha)
            
            if proceso:
                query += " AND Proceso LIKE ?"
                params.append(f"%{proceso}%")
            
            # Ejecutar la consulta
            cursor.execute(query, params)
            row = cursor.fetchone()
            
            if row:
                return {
                    "total_registros": row.total,
                    "peso_total": row.suma or 0,
                    "peso_promedio": row.promedio or 0,
                    "peso_minimo": row.minimo or 0,
                    "peso_maximo": row.maximo or 0
                }
            else:
                return {
                    "total_registros": 0,
                    "peso_total": 0,
                    "peso_promedio": 0,
                    "peso_minimo": 0,
                    "peso_maximo": 0
                }
        except pyodbc.Error as e:
            print(f"Error al consultar estadísticas de pesaje: {e}")
            return {
                "total_registros": 0,
                "peso_total": 0,
                "peso_promedio": 0,
                "peso_minimo": 0,
                "peso_maximo": 0
            }
        finally:
            cursor.close()
            conn.close()