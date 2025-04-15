import flet as ft
import serial

class SerialConfigDialog:
    def __init__(self, page, serial_manager, on_config_saved=None):
        self.page = page
        self.serial_manager = serial_manager
        self.on_config_saved = on_config_saved
        
        # Obtener opciones de configuración
        self.baudrate_options = serial_manager.get_available_baudrates()
        self.bytesize_options = serial_manager.get_available_bytesizes()
        self.parity_options = serial_manager.get_available_parities()
        self.stopbits_options = serial_manager.get_available_stopbits()
        
        # Obtener configuración actual
        current_settings = serial_manager.get_connection_settings()
        
        # Controles para configuración
        self.baudrate_dropdown = ft.Dropdown(
            label="Velocidad (baudios)",
            width=200,
            options=[ft.dropdown.Option(str(baud)) for baud in self.baudrate_options],
            value=str(current_settings['baudrate'])
        )
        
        self.bytesize_dropdown = ft.Dropdown(
            label="Bits de datos",
            width=200,
            options=[ft.dropdown.Option(key) for key in self.bytesize_options.keys()],
            value="8 bits"  # Valor predeterminado
        )
        
        self.parity_dropdown = ft.Dropdown(
            label="Paridad",
            width=200,
            options=[ft.dropdown.Option(key) for key in self.parity_options.keys()],
            value="Ninguna"  # Valor predeterminado
        )
        
        self.stopbits_dropdown = ft.Dropdown(
            label="Bits de parada",
            width=200,
            options=[ft.dropdown.Option(key) for key in self.stopbits_options.keys()],
            value="1 bit"  # Valor predeterminado
        )
        
        self.timeout_field = ft.TextField(
            label="Timeout (segundos)",
            width=200,
            value=str(current_settings['timeout']),
            hint_text="1.0"
        )
        
        # Botones
        self.save_button = ft.ElevatedButton(
            "Guardar configuración",
            on_click=self.save_config,
            bgcolor="#8c4191",
            color=ft.Colors.WHITE
        )
        
        self.cancel_button = ft.OutlinedButton(
            "Cancelar",
            on_click=self.close_dialog
        )
        
        # Crear el diálogo
        self.dialog = ft.AlertDialog(
            title=ft.Text("Configuración avanzada del puerto serial"),
            content=self.create_dialog_content(),
            actions=[self.cancel_button, self.save_button],
            actions_alignment=ft.MainAxisAlignment.END
        )
    
    def create_dialog_content(self):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Configure los parámetros del puerto serial",
                        size=14,
                        color="#666666"
                    ),
                    ft.Divider(),
                    self.baudrate_dropdown,
                    ft.Row(
                        [
                            self.bytesize_dropdown,
                            self.parity_dropdown
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Row(
                        [
                            self.stopbits_dropdown,
                            self.timeout_field
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Divider(),
                    ft.Text(
                        "Nota: La configuración se aplicará en la próxima conexión",
                        italic=True,
                        size=12,
                        color="#666666"
                    )
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO
            ),
            width=480,
            height=380,
            padding=20
        )
    
    def show(self):
        # Mostrar el diálogo
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()
    
    def close_dialog(self, e=None):
        self.dialog.open = False
        self.page.update()
    
    def save_config(self, e):
        try:
            # Obtener los valores de los controles
            baudrate = int(self.baudrate_dropdown.value)
            
            # Obtener el valor correspondiente del diccionario
            bytesize_key = self.bytesize_dropdown.value
            bytesize = self.bytesize_options[bytesize_key]
            
            parity_key = self.parity_dropdown.value
            parity = self.parity_options[parity_key]
            
            stopbits_key = self.stopbits_dropdown.value
            stopbits = self.stopbits_options[stopbits_key]
            
            # Convertir timeout a float
            try:
                timeout = float(self.timeout_field.value)
                if timeout <= 0:
                    raise ValueError("El timeout debe ser mayor que cero")
            except ValueError:
                # Mostrar error
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("El valor de timeout no es válido"),
                    bgcolor=ft.Colors.RED
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            # Guardar la configuración en el serial_manager
            # Nota: Esto no cierra la conexión actual, solo establece
            # los parámetros para la próxima conexión
            self.serial_manager.baudrate = baudrate
            self.serial_manager.bytesize = bytesize
            self.serial_manager.parity = parity
            self.serial_manager.stopbits = stopbits
            self.serial_manager.timeout = timeout
            
            # Cerrar el diálogo
            self.close_dialog()
            
            # Mostrar mensaje de éxito
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Configuración guardada correctamente"),
                bgcolor=ft.Colors.GREEN
            )
            self.page.snack_bar.open = True
            self.page.update()
            
            # Llamar al callback si existe
            if self.on_config_saved:
                self.on_config_saved()
                
        except Exception as e:
            # Mostrar error
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error al guardar la configuración: {str(e)}"),
                bgcolor=ft.Colors.RED
            )
            self.page.snack_bar.open = True
            self.page.update()