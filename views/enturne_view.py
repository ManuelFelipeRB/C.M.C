import flet as ft
from datetime import datetime

class EnturneView:
    def __init__(self, page, color_principal, db_manager=None, on_save_callback=None):
        self.page = page
        self.color_principal = color_principal
        self.db_manager = db_manager  # Gestor de base de datos
        self.on_save_callback = on_save_callback  # Callback para cuando se guarda
        
        # Campos de formulario
        self.cedula = ft.TextField(
            label="Numero de Cédula",
            border_color=ft.Colors.GREY_400,
            border_radius=8,
            height=40,
            width=150
        )

        self.nombre_conductor = ft.TextField(
            label="Nombre del Conductor",
            border_color=ft.Colors.GREY_400,
            border_radius=8,
            height=40,
            width=380
        )
        
        self.celular = ft.TextField(
            label="Celular",
            border_color=ft.Colors.GREY_400,
            border_radius=8,
            height=40,
            width=150
        )
        self.direccion = ft.TextField(
            label="Dirección",
            border_color=ft.Colors.GREY_400,
            border_radius=8,
            height=40,
            width=250
        )
        self.placa = ft.TextField(
            label="Placa vehículo",
            border_color=ft.Colors.GREY_400,
            border_radius=8,
            height=40,
            width=120
        )

        self.trailer = ft.TextField(
            label="Placa trailer",
            border_color=ft.Colors.GREY_400,
            border_radius=8,
            height=40,
            width=120
        )

        self.trasportadora = ft.TextField(
            label="Transportadora",
            border_color=ft.Colors.GREY_400,
            border_radius=8,
            height=40,
            width=350
        )

        self.nit_transportadora = ft.TextField(
            label="Nit transportadora",
            border_color=ft.Colors.GREY_400,
            border_radius=8,
            height=40,
            width=160
        )

        self.manifiesto = ft.TextField(
            label="Manifiesto",
            border_color=ft.Colors.GREY_400,
            border_radius=8,
            height=40,
            width=150
        )

        self.estado_dropdown = ft.Dropdown(
            label="Estado",
            options=[
                ft.dropdown.Option("Enturnado"),
                ft.dropdown.Option("No enturnado"),
                ft.dropdown.Option("En proceso"),
            ],
            width=200,
            border_color=ft.Colors.GREY_400,
            border_radius=8,
            
        )
        
        # Botones de acción
        self.guardar_button = ft.ElevatedButton(
            "Guardar",
            #icon=ft.Icons.SAVE,
            bgcolor=self.color_principal,
            color=ft.Colors.WHITE,
            on_click=self.save_data
        )
        
        self.cancelar_button = ft.OutlinedButton(
            "Cancelar",
            #icon=ft.Icons.CANCEL,
            on_click=self.hide
        )
        
        # Crear la vista
        self.view = self.create_view()
    
    def create_view(self):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Información del conductor",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=self.color_principal
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        #ft.Text("Conductor:", size=16),
                                        self.cedula,
                                        self.nombre_conductor,
                                        self.celular,
                                        self.direccion,
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                            ],
                            spacing=20,
                        ),
                        padding=20,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=10,
                        margin=ft.margin.only(top=20),
                        border=ft.border.all(1, ft.Colors.GREY_300),
                    ),

                        ft.Text(
                            "Información del vehículo",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=self.color_principal
                        ),

                    ft.Container(
                            content=ft.Column(
                            [
                                ft.Row(
                                    [   
                                        #ft.Text("Vehículo:", size=14),
                                        self.placa,
                                        self.trailer,
                                        self.nit_transportadora,
                                        self.trasportadora,
                                    ],
                                    expand=True,
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.Row(
                                    [
                                        #ft.Text("Conductor:", size=14),
                                        
                                        self.estado_dropdown,
                                        self.manifiesto,
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),

                                ft.Divider(),
                                ft.Row(
                                    [
                                        self.cancelar_button,
                                        self.guardar_button,
                                    ],
                                    alignment=ft.MainAxisAlignment.END,
                                    spacing=10
                                ),
                            ],
                            spacing=20,
                        ),

                        padding=20,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=10,
                        margin=ft.margin.only(top=20),
                        border=ft.border.all(1, ft.Colors.GREY_300),
                    ),

                ],
                spacing=10,
            ),
            padding=ft.padding.all(30),
            expand=True,
            visible=False,
        )
    
    def get_view(self):
        return self.view
    
    def show(self, vehicle_id=None):
        """Mostrar el formulario y cargar datos si se proporciona un ID"""
        self.clear_form()
        
        if vehicle_id is not None:
            self.load_data(vehicle_id)
            
        self.view.visible = True
        self.page.update()
    
    def hide(self, e=None):
        """Ocultar el formulario"""
        self.view.visible = False
        self.page.update()
    
    def clear_form(self):
        """Limpiar todos los campos del formulario"""
        self.nombre_conductor.value = ""
        self.celular.value = ""
        self.placa.value = ""
        self.estado_dropdown.value = None
        self.page.update()
    
    def load_data(self, vehicle_id):
        """Cargar datos del vehículo desde la base de datos"""
        if self.db_manager is None:
            return
            
        # Aquí iría el código para cargar datos específicos
        # Ejemplo:
        # vehicle_data = self.db_manager.get_vehicle_by_id(vehicle_id)
        # if vehicle_data:
        #     self.nombre_conductor.value = vehicle_data.get('NombreConductor', '')
        #     self.celular.value = vehicle_data.get('Celular', '')
        #     self.placa.value = vehicle_data.get('Placa', '')
        #     self.estado_dropdown.value = vehicle_data.get('Estado', '')
        
        self.page.update()
    
    def save_data(self, e=None):
        """Guardar los datos del formulario en la base de datos"""
        # Validar campos
        if not self.validate_form():
            return
            
        # Recopilar datos del formulario
        vehicle_data = {
            'NombreConductor': self.nombre_conductor.value,
            'Celular': self.celular.value,
            'Placa': self.placa.value,
            'Estado': self.estado_dropdown.value,
            'FechaRegistro': datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        
        # Guardar en la base de datos
        if self.db_manager is not None:
            # Aquí iría el código para guardar en la base de datos
            # Ejemplo:
            # result = self.db_manager.save_vehicle(vehicle_data)
            # if result:
            #    print("Vehículo guardado correctamente")
            pass
            
        # Llamar al callback si existe
        if self.on_save_callback:
            self.on_save_callback()
            
        # Ocultar el formulario
        self.hide()
    
    def validate_form(self):
        """Validar que todos los campos requeridos estén completos"""
        is_valid = True
        
        if not self.nombre_conductor.value:
            self.nombre_conductor.error_text = "El nombre es obligatorio"
            is_valid = False
        else:
            self.nombre_conductor.error_text = None
            
        if not self.placa.value:
            self.placa.error_text = "La placa es obligatoria"
            is_valid = False
        else:
            self.placa.error_text = None
            
        if not self.estado_dropdown.value:
            self.estado_dropdown.error_text = "Seleccione un estado"
            is_valid = False
        else:
            self.estado_dropdown.error_text = None
            
        self.page.update()
        return is_valid