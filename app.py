from flask import Flask, render_template, request
from flask_cors import CORS
import pyodbc
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Habilita CORS para toda la app

@app.route('/api/pesajes')
def index():
    # Obtener el parámetro de filtro (si existe)
    filtro = request.args.get('filtro', 'todos')
    
    # Conectar a la primera base de datos (Isotanques.accdb)
    conn_str1 = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=\\TTRAFEJT2K02\User$\Manuel.Rodriguez\enturne\Isotanques1\Isotanques.accdb'
    conn1 = pyodbc.connect(conn_str1)
    cursor1 = conn1.cursor()

    # Realiza la consulta para la primera tabla (Taras)
    cursor1.execute("SELECT * FROM Taras")
    rows_taras = cursor1.fetchall()

    # Convierte los datos a un formato adecuado para pasar al frontend
    pesajes_data = []
    for row in rows_taras:
        pesajes_data.append({
            "Vehiculo": row.VEHICULO,  
            "Peso": row.PESO,  
            "Fecha": row.FECHA,  
        })

    # Cerrar la conexión a la primera base de datos
    cursor1.close()
    conn1.close()

    # Conectar a la segunda base de datos (EnturneVehiculosSPITB2.mdb)
    conn_str2 = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=\\ttrafejt2k02\Shared\Safety Program\CEV 2021\BaseDatos\EnturneVehiculosSPITB2.mdb'
    conn2 = pyodbc.connect(conn_str2)
    cursor2 = conn2.cursor()

    # Calcular la fecha actual en formato numérico de Excel
    hoy = datetime.now()
    fecha_numerica_excel = (hoy - datetime(1900, 1, 1)).days + 2  

    # Realiza la consulta para la segunda tabla (BDEnturne)
    cursor2.execute("SELECT NombreConductor, Placa, Producto, Proceso, Cliente, Estado FROM BDEnturne WHERE Folio = ? Order By Consecutivo", (fecha_numerica_excel,))
    rows_pesajes1 = cursor2.fetchall()

    # Convierte los datos de la segunda consulta
    pesajes1_data = []
    total_finalizados = 0  # Contador de registros con Estado "Finalizado"
    total_proceso = 0  
    total_inspeccion = 0
    total_pendiente = 0
    filtered_data = []

    for row in rows_pesajes1:
        item = {
            "NombreConductor": row.NombreConductor,
            "Placa": row.Placa,
            "Producto": row.Producto,
            "Proceso": row.Proceso,
            "Cliente": row.Cliente,
            "Estado": row.Estado,
        }
        pesajes1_data.append(item)
        
        # Contar registros con estado "Finalizado"
        if row.Estado == "Finalizado":
            total_finalizados += 1
        # Contar registros con estado "En proceso"
        elif row.Estado == "En proceso":
            total_proceso += 1  
        elif row.Estado == "En inspeccion":
            total_inspeccion += 1  

    total_pesajes1 = len(pesajes1_data)
    total_pendiente = total_pesajes1 - total_proceso - total_finalizados

    # Filtrar los datos según el filtro seleccionado
    if filtro == 'todos':
        filtered_data = pesajes1_data
    elif filtro == 'en_proceso':
        filtered_data = [item for item in pesajes1_data if item['Estado'] == 'En proceso']
    elif filtro == 'finalizado':
        filtered_data = [item for item in pesajes1_data if item['Estado'] == 'Finalizado']
    elif filtro == 'inspeccion':
        filtered_data = [item for item in pesajes1_data if item['Estado'] != 'En inspeccion'and item['Estado'] != 'Finalizado']
    elif filtro == 'pendiente':
        filtered_data = [item for item in pesajes1_data if item['Estado'] != 'En proceso' and item['Estado'] != 'Finalizado']

    # Cerrar la conexión a la segunda base de datos
    cursor2.close()
    conn2.close()

    # Pasar ambas consultas a la plantilla junto con el filtro activo
    return render_template('index.html', 
                          pesajes_data=pesajes_data, 
                          pesajes1_data=filtered_data, 
                          total_pesajes1=total_pesajes1, 
                          total_finalizados=total_finalizados, 
                          total_proceso=total_proceso, 
                          total_inspeccion=total_inspeccion, 
                          total_pendiente=total_pendiente,
                          filtro_activo=filtro)

if __name__ == '__main__':
    app.run(debug=True, port=5001)