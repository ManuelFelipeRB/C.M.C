import flet as ft
import serial

class SerialConfigModal:
    def __init__(self, page, serial_manager, on_config_saved=None, parent_view=None):
        self.page = page
        self.serial_manager = serial_manager
        self.on_config_saved = on_config_saved
        self.parent_view = parent_view  # Referencia a BasculaView
        
        # Obtener opciones disponibles
        self.available_ports = serial_manager.get_available_ports()
        
        # Dropdowns y campos de configuración
        self.port_dropdown = ft.Dropdown(
            label="Puerto Serial",
            options=[ft.dropdown.Option(port) for port in self.available_ports],
            width=300
        )
        
        self.baudrate_dropdown = ft.Dropdown(
            label="Velocidad (baudios)",
            options=[
                ft.dropdown.Option("9600"),
                ft.dropdown.Option("19200"),
                ft.dropdown.Option("38400"),
                ft.dropdown.Option("57600"),
                ft.dropdown.Option("115200")
            ],
            value="9600",
            width=300
        )
        
        # Indicador de estado
        self.connection_status = ft.Text(
            "Desconectado",
            color=ft.Colors.RED,
            weight=ft.FontWeight.BOLD
        )
        
        # Botones
        self.connect_button = ft.ElevatedButton(
            "Conectar",
            icon=ft.Icons.CABLE,
            on_click=self.toggle_connection,
            bgcolor=ft.Colors.GREEN,
            color=ft.Colors.WHITE
        )
        
        self.disconnect_button = ft.ElevatedButton(
            "Desconectar",
            icon=ft.Icons.CANCEL,
            on_click=self.disconnect_port,
            bgcolor=ft.Colors.RED,
            color=ft.Colors.WHITE,
            disabled=True
        )
        
        self.refresh_ports_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip="Actualizar puertos",
            on_click=self.refresh_ports
        )
        
        self.close_button = ft.OutlinedButton(
            "Cerrar",
            on_click=self.close_modal
        )
        
        self.save_button = ft.ElevatedButton(
            "Guardar configuración",
            on_click=self.save_config,
            bgcolor="#8c4191",
            color=ft.Colors.WHITE
        )
    
    def show(self):
        """Mostrar el modal de configuración"""
        try:
            # Actualizar puertos disponibles
            self.refresh_ports(None)
            
            # Actualizar estado según el serial_manager
            if self.serial_manager.is_connected:
                self.connection_status.value = "Conectado"
                self.connection_status.color = ft.Colors.GREEN
                self.connect_button.disabled = True
                self.disconnect_button.disabled = False
                
                # Seleccionar el puerto actualmente conectado si está disponible
                current_port = self.serial_manager.port if hasattr(self.serial_manager, 'port') else None
                if current_port:
                    self.port_dropdown.value = current_port
            else:
                self.connection_status.value = "Desconectado"
                self.connection_status.color = ft.Colors.RED
                self.connect_button.disabled = False
                self.disconnect_button.disabled = True
                
            # Actualizar baudrate seleccionado
            current_baudrate = str(self.serial_manager.baudrate) if hasattr(self.serial_manager, 'baudrate') else "9600"
            self.baudrate_dropdown.value = current_baudrate
            
            # Crear el diálogo
            self.overlay = ft.AlertDialog(
                title=ft.Text("Configuración de Puerto Serial"),
                content=ft.Container(
                    content=ft.Column([
                        # Sección de puerto y conexión
                        ft.Text("Puerto y Conexión", weight=ft.FontWeight.BOLD),
                        ft.Row([
                            self.port_dropdown,
                            self.refresh_ports_button
                        ]),
                        ft.Row([
                            self.connect_button,
                            self.disconnect_button,
                            self.connection_status
                        ], alignment=ft.MainAxisAlignment.START, spacing=10),
                        
                        ft.Divider(),
                        
                        # Sección de configuración
                        ft.Text("Parámetros de Comunicación", weight=ft.FontWeight.BOLD),
                        self.baudrate_dropdown,
                    ], spacing=10, scroll=ft.ScrollMode.AUTO),
                    width=500,
                    height=400,
                    padding=20
                ),
                actions=[
                    self.close_button,
                    self.save_button
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )
            
            # Mostrar el diálogo
            self.page.overlay.append(self.overlay)
            self.overlay.open = True
            self.page.update()
            
        except Exception as e:
            print(f"Error al mostrar el modal de configuración: {e}")
            import traceback
            traceback.print_exc()
    
    def refresh_ports(self, e):
        """Actualizar lista de puertos disponibles"""
        # Actualizar lista de puertos usando el método de BasculaView si está disponible
        if self.parent_view and hasattr(self.parent_view, 'refresh_ports'):
            # Primero actualizamos los puertos disponibles en BasculaView
            self.parent_view.refresh_ports()
            
            # Luego copiamos los puertos actualizados a nuestro dropdown
            self.available_ports = self.serial_manager.get_available_ports()
            self.port_dropdown.options.clear()
            for port in self.available_ports:
                self.port_dropdown.options.append(ft.dropdown.Option(port))
                
            # Registrar evento - lo registramos a través de BasculaView
            ports_str = ", ".join(self.available_ports) if self.available_ports else "ninguno"
            refresh_msg = f"Lista de puertos actualizada. Puertos disponibles: {ports_str}"
            if hasattr(self.parent_view, 'add_event_log'):
                self.parent_view.add_event_log(refresh_msg)
        else:
            # Actualización estándar si no hay BasculaView
            self.available_ports = self.serial_manager.get_available_ports()
            self.port_dropdown.options.clear()
            for port in self.available_ports:
                self.port_dropdown.options.append(ft.dropdown.Option(port))
        
        self.page.update()
    
    def toggle_connection(self, e):
        """Conectar o desconectar del puerto serial"""
        # Si tenemos referencia a BasculaView, usamos su método toggle_connection
        if self.parent_view and hasattr(self.parent_view, 'toggle_connection'):
            # Primero guardamos el puerto seleccionado en el dropdown de BasculaView
            if hasattr(self.parent_view, 'port_dropdown') and self.port_dropdown.value:
                self.parent_view.port_dropdown.value = self.port_dropdown.value
                
            # Luego llamamos al método toggle_connection de BasculaView
            self.parent_view.toggle_connection(e)
            
            # Actualizamos nuestro estado según el resultado
            if self.serial_manager.is_connected:
                self.connection_status.value = "Conectado"
                self.connection_status.color = ft.Colors.GREEN
                self.connect_button.disabled = True
                self.disconnect_button.disabled = False
            else:
                self.connection_status.value = "Desconectado"
                self.connection_status.color = ft.Colors.RED
                self.connect_button.disabled = False
                self.disconnect_button.disabled = True
        else:
            # Implementación estándar si no hay BasculaView
            if not self.serial_manager.is_connected:
                if not self.port_dropdown.value:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Por favor seleccione un puerto"),
                        bgcolor=ft.Colors.RED
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                    return
                
                if self.serial_manager.connect(self.port_dropdown.value):
                    self.connection_status.value = "Conectado"
                    self.connection_status.color = ft.Colors.GREEN
                    self.connect_button.disabled = True
                    self.disconnect_button.disabled = False
                else:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Error al conectar a {self.port_dropdown.value}"),
                        bgcolor=ft.Colors.RED
                    )
                    self.page.snack_bar.open = True
            else:
                self.serial_manager.disconnect()
                self.connection_status.value = "Desconectado"
                self.connection_status.color = ft.Colors.RED
                self.connect_button.disabled = False
                self.disconnect_button.disabled = True
                
        self.page.update()
    
    def disconnect_port(self, e):
        """Desconectar del puerto serial"""
        # Si tenemos referencia a BasculaView y ya está conectado, usamos su método toggle_connection
        if self.parent_view and hasattr(self.parent_view, 'toggle_connection') and self.serial_manager.is_connected:
            self.parent_view.toggle_connection(e)
            
            # Actualizamos nuestro estado
            self.connection_status.value = "Desconectado"
            self.connection_status.color = ft.Colors.RED
            self.connect_button.disabled = False
            self.disconnect_button.disabled = True
        else:
            # Implementación estándar
            self.serial_manager.disconnect()
            self.connection_status.value = "Desconectado"
            self.connection_status.color = ft.Colors.RED
            self.connect_button.disabled = False
            self.disconnect_button.disabled = True
        
        self.page.update()
    
    def save_config(self, e):
        """Guardar la configuración"""
        try:
            # Guardar baudrate
            baudrate = int(self.baudrate_dropdown.value)
            self.serial_manager.baudrate = baudrate
            
            # Registrar evento - lo hacemos a través de BasculaView
            config_msg = f"Configuración guardada: {baudrate} baudios"
            if self.parent_view and hasattr(self.parent_view, 'add_event_log'):
                self.parent_view.add_event_log(config_msg)
            
            # Cerrar el modal
            self.close_modal()
            
            # Notificar cambios a través de BasculaView si está disponible
            if self.parent_view and hasattr(self.parent_view, 'on_config_saved'):
                self.parent_view.on_config_saved()
            elif self.on_config_saved:
                self.on_config_saved()
                
            # Mostrar notificación
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(config_msg),
                bgcolor=ft.Colors.GREEN
            )
            self.page.snack_bar.open = True
            self.page.update()
                
        except Exception as e:
            error_msg = f"Error al guardar la configuración: {e}"
            if self.parent_view and hasattr(self.parent_view, 'add_event_log'):
                self.parent_view.add_event_log(error_msg, is_error=True)
            print(error_msg)
    
    def close_modal(self, e=None):
        """Cerrar el modal"""
        self.overlay.open = False
        self.page.update()