import flet as ft

class EditVehicleModal:
    def __init__(self, page, db_manager, on_vehicle_updated):
        self.page = page
        self.db_manager = db_manager
        self.on_vehicle_updated = on_vehicle_updated
        self.vehicle_id = None
        self.estados_opciones = [
            "Enturnado", "No enturnado", "Anunciado", "Autorizado", 
            "En inspeccion", "Revision documental", "Transito entrando", 
            "Procesado", "Ingresó", "En proceso", "Finalizado"
        ]
        self.tipo_vehiculo_opciones = [
            "Camión", "Furgón", "TractoCamión", "Camabaja", 
            "Volqueta", "Grua", "Planchon"
        ]
        # Campos de formulario

        self.cedula_conductor = self.crear_textfield("Numero Cédula")

        self.nombre_conductor = self.crear_textfield("Nombre conductor")
        
        self.placa = self.crear_textfield("Placa")
        
        self.remolque = self.crear_textfield("Remolque")

        self.grupo_producto = self.crear_textfield("Grupo producto")

        self.producto = self.crear_textfield("Producto")
        
        self.proceso = self.crear_textfield("Proceso")
        
        self.cliente = self.crear_textfield("Cliente")

        self.origen = self.crear_textfield("Origen")

        self.destino = self.crear_textfield("Destino")

        self.manifiesto = self.crear_textfield("Manifiesto")

        self.gut = self.crear_textfield("GUT")

        self.tipo_vehiculo = ft.Dropdown(
            label="Tipo vehículo",
            options=[ft.dropdown.Option(tipo_vehiculo) for tipo_vehiculo in self.tipo_vehiculo_opciones],
            border_color=ft.Colors.GREY_400,
            border_radius=8,
            enable_filter=True,
            filled=True,
            fill_color=ft.Colors.WHITE54   
        )
        
        self.estado = ft.Dropdown(
            label="Estado",
            options=[ft.dropdown.Option(estado) for estado in self.estados_opciones],
            border_color=ft.Colors.GREY_400,
            border_radius=8,
            enable_filter=True,
            filled=True,
            fill_color=ft.Colors.WHITE54    
        )
        # Botones
        self.guardar_btn = ft.ElevatedButton(
            "Guardar",
            #icon=ft.Icons.SAVE,
            on_click=self.save_changes,
            style=ft.ButtonStyle(
                bgcolor="#8c4191",
                color=ft.Colors.WHITE,
            ),
            width=120
        )
        
        self.cancelar_btn = ft.OutlinedButton(
            "Cancelar",
            #icon=ft.Icons.CANCEL,
            on_click=self.close_modal,
            width=120
        )

    def crear_textfield(self, label):
        return ft.TextField(
            label=label,
            border_color=ft.Colors.GREY_400,
            border_radius=6,
            height=50,
            expand=True,
            bgcolor=ft.Colors.WHITE54
        )
    
    def load_vehicle_data(self, vehicle_id):
        self.vehicle_id = vehicle_id
        vehicle_data = self.db_manager.get_vehicle_by_id(vehicle_id)
        
        if vehicle_data:
            self.cedula_conductor.value = vehicle_data["Cedula"]
            self.nombre_conductor.value = vehicle_data["NombreConductor"]
            self.placa.value = vehicle_data["Placa"]
            self.remolque.value = vehicle_data["Remolque"]
            self.grupo_producto.value = vehicle_data["GrupoProducto"]
            self.producto.value = vehicle_data["Producto"]
            self.proceso.value = vehicle_data["Proceso"]
            self.cliente.value = vehicle_data["Cliente"]
            self.tipo_vehiculo.value = vehicle_data["TipoEmbalaje"]
            self.manifiesto.value = vehicle_data["Manifiesto"]
            self.origen.value = vehicle_data["Origen"]
            self.destino.value = vehicle_data["Destino"]
            self.estado.value = vehicle_data["Estado"]
            self.page.update()
        else:
            print(f"No se pudieron cargar los datos para ID: {vehicle_id}")
    
    def show(self, vehicle_id):
        try:
            # Limpiar los campos
            self.cedula_conductor.value = ""
            self.nombre_conductor.value = ""
            self.placa.value = ""
            self.producto.value = ""
            self.proceso.value = ""
            self.cliente.value = ""
            self.manifiesto.value = ""
            self.estado.value = None
            self.tipo_vehiculo.value = None
            
            # Cargar los datos del vehículo
            self.load_vehicle_data(vehicle_id)
            
            # Crear un diálogo personalizado en lugar de usar AlertDialog

            self.overlay = ft.AlertDialog(
                content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Editar Vehículo", size=20, weight=ft.FontWeight.BOLD),
                        #ft.Text("Edite la información del vehículo", size=14),
                        ft.Row(
                            [
                                self.placa,
                                self.remolque,
                            ],
                        ),
                        ft.Row(
                            [
                                self.cedula_conductor,
                                self.nombre_conductor,
                            ],
                        ),
                        ft.Row(
                            [
                            self.grupo_producto,
                            self.producto,
                            ],
                        ),
                        self.cliente,
                        self.proceso,
                        ft.Row(
                            [
                                self.origen,
                                self.destino,
                            ],
                        ),
                        ft.Row(
                            [
                                self.estado,
                                self.tipo_vehiculo,
                                self.manifiesto,
                            ],
                        ),
                        
                        ft.Row(
                            [
                                self.cancelar_btn,
                                self.guardar_btn,
                            ],
                            alignment=ft.MainAxisAlignment.END,
                        )
                    ],
                    spacing=20,
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=680,
                height=680,
            )
            )
            
            # Mostrar el diálogo personalizado
            self.page.overlay.append(self.overlay)
            self.overlay.open = True
            self.page.update()
            print("Modo de edición activado")
        except Exception as e:
            print(f"Error al mostrar el modal: {e}")

    def close_modal(self, e):
        # Eliminar el overlay
        self.overlay.open = False
        self.page.update()
        print("Modo edición cerrado")
    
    def save_changes(self, e):
        # Validar datos
        if not self.nombre_conductor.value or not self.placa.value or not self.estado.value:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Por favor complete los campos obligatorios"),
                bgcolor=ft.Colors.RED_400
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        # Crear objeto con los datos actualizados
        updated_data = {
            "ID": self.vehicle_id,
            "Cedula": self.cedula_conductor.value,
            "NombreConductor": self.nombre_conductor.value,
            "Placa": self.placa.value,
            "Remolque": self.remolque.value,
            "GrupoProducto": self.grupo_producto.value,
            "Producto": self.producto.value,
            "Proceso": self.proceso.value,
            "Cliente": self.cliente.value,
            "Manifiesto": self.manifiesto.value,
            "Origen": self.origen.value,
            "Destino": self.destino.value,
            "Estado": self.estado.value,
            "TipoEmbalaje": self.tipo_vehiculo.value,
        }
        
        # Intentar guardar los cambios
        if self.db_manager.update_vehicle(updated_data):
            # Cerrar el modal
            self.close_modal(e)
            
            # Mostrar mensaje de éxito
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("¡Cambios guardados correctamente!"),
                bgcolor=ft.Colors.GREEN_400
            )
            self.page.snack_bar.open = True
            
            # Llamar al callback para actualizar los datos
            if self.on_vehicle_updated:
                self.on_vehicle_updated()
        else:
            # Mostrar mensaje de error
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Error al guardar los cambios"),
                bgcolor=ft.Colors.RED_400
            )
            self.page.snack_bar.open = True
        
        self.page.update()

        # Modificación de la clase VehicleData para incluir ID 
class VehicleData:
    def __init__(self):
        
        from common.database_manager import DatabaseManager  # Import the DatabaseManager class
        self.db_manager = DatabaseManager()
        self.data = []
        self.filtered_data = []
        self.totals = {
            'total_pesajes': 0,
            'total_entrando': 0,
            'total_finalizados': 0,
            'total_proceso': 0,
            'total_pendiente': 0
        }
    
    def load_data(self, fecha_numerica_excel):
        rows = self.db_manager.fetch_vehicle_data(fecha_numerica_excel)
        self.data = []
        self.reset_counters()
        
        for row in rows:
            # Para cédula, necesitamos formatear el número sin decimales si es float
            self.cedula_str = ""
            if row.Cedula is not None:
                if isinstance(row.Cedula, float):
                    # Si es un número entero (como 12345.0), mostrar sin decimal
                    if row.Cedula.is_integer():
                        self.cedula_str = str(int(row.Cedula))
                    else:
                        self.cedula_str = str(row.Cedula)
                else:
                    self.cedula_str = str(row.Cedula)


            item = {
                "ID": row.ID,
                "Cedula": row.Cedula,
                "NombreConductor": row.NombreConductor,
                "Placa": row.Placa,
                "Remolque": row.Remolque,
                "GrupoProducto": row.GrupoProducto,
                "Producto": row.Producto,
                "Proceso": row.Proceso,
                "Cliente": row.Cliente,
                "Origen": getattr(row, 'Origen', None),
                "Destino": getattr(row, 'Destino', None),
                "Estado": row.Estado,
                "Manifiesto": getattr(row, 'Manifiesto', None),
                "TipoEmbalaje": getattr(row, 'TipoEmbalaje', None),
            }
            self.data.append(item)
            
            # Contar estados
            self._count_state(row.Estado)
        
        self.totals['total_pesajes'] = len(self.data)
        self.totals['total_pendiente'] = self.totals['total_pesajes'] - self.totals['total_entrando']- self.totals['total_proceso'] - self.totals['total_finalizados']
        self.filtered_data = self.data
        
    def _count_state(self, estado):
        if estado == "Finalizado":
            self.totals['total_finalizados'] += 1
        elif estado == "En proceso":
            self.totals['total_proceso'] += 1
        elif estado == "Transito entrando":
            self.totals['total_entrando'] += 1
    
    def reset_counters(self):
        for key in self.totals:
            self.totals[key] = 0
    
    def apply_filter(self, filtro):
        if filtro == 'todos':
            self.filtered_data = self.data
        elif filtro == 'en_proceso':
            self.filtered_data = [item for item in self.data if item['Estado'] == 'En proceso']
        elif filtro == 'entrando':
            self.filtered_data = [item for item in self.data if item['Estado'] == 'Transito entrando']
        elif filtro == 'finalizado':
            self.filtered_data = [item for item in self.data if item['Estado'] == 'Finalizado']
        elif filtro == 'pendiente':
            self.filtered_data = [item for item in self.data if item['Estado'] != 'En proceso' and 
                                                                 item['Estado'] != 'Finalizado' and 
                                                                 item['Estado'] != 'Transito entrando']
        return self.filtered_data
    
    def search_data(self, search_text):
        if not search_text:
            return self.filtered_data
        
        search_text = search_text.lower()
        
        def safe_search(value):
            """Busca text en value manejando distintos tipos de datos"""
            if value is None:
                return False
            
            # Convertir a string para poder buscar, sin importar el tipo original
            if isinstance(value, (int, float)):
                # Para números, convertir a string
                value_str = str(value)
            elif isinstance(value, str):
                # Para strings, mantener como está pero en minúsculas
                value_str = value.lower()
            else:
                # Para otros tipos, intentar convertir a string
                value_str = str(value).lower()
                
            return search_text in value_str
        
        # Filtrar usando la función safe_search para cada campo
        result = []
        for item in self.filtered_data:
            if (safe_search(item['Cedula']) or
                safe_search(item['NombreConductor']) or
                safe_search(item['Placa']) or
                safe_search(item['Remolque']) or
                safe_search(item['GrupoProducto']) or
                safe_search(item['Producto']) or
                safe_search(item['Proceso']) or
                safe_search(item['Cliente']) or
                safe_search(item['Origen']) or
                safe_search(item['Manifiesto']) or
                safe_search(item['Destino']) or
                safe_search(item['Estado'])or
                safe_search(item['TipoEmbalaje'])):
                result.append(item)
        
        return result