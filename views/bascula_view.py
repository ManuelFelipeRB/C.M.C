import flet as ft
import threading
from datetime import datetime
from common.serial_manager import SerialManager
from common.ui_components import UIComponents
from common.database_manager import PesajesManager


class BasculaView:
    def __init__(self, page, color_principal, color_secundario, pagination=None, vehicle_data=None, update_data_callback=None, stat_cards=None):
        self.page = page
        self.color_principal = color_principal
        self.color_secundario = color_secundario
            
    # Referencias a componentes externos
        self.pagination = pagination
        self.vehicle_data = vehicle_data
        self.update_data_callback = update_data_callback
        self.stat_cards = stat_cards or {}

        self.ui_components = UIComponents(page, color_principal)

        # Inicializar el gestor de puerto serie
        self.serial_manager = SerialManager()
        
        # Valores para puerto serie
        self.available_ports = self.serial_manager.get_available_ports()
        self.current_weight = "0.00"
        

        # Lista para mantener un historial de pesos
        self.weight_history = []
        self.MAX_HISTORY_SIZE = 10  # Máximo número de pesos a mantener
        
        # Lista para registro de eventos
        self.event_log = []
        self.MAX_LOG_SIZE = 50
        
        # Inicializar componentes UI
        self.stat_cards = self.create_stat_cards()
        self.port_dropdown = self.create_port_dropdown()

        self.Proceso_opciones = [
            "Repesaje Cisterna", "Tara Verificada", "Pesaje Isotanque",
            "Pesaje Contenedor Lleno", "Pesaje Vehiculo Externo"
        ]
        self.ejes_opciones = [
            "2", "3", "4", "2S2", "2S3", "3S2", "3S3","Extra"
        ]

        self.placa_field = ft.TextField(
            label="Placa",
            width=150,
            height=50,
            border_color=ft.Colors.GREY_400,
            bgcolor=ft.Colors.WHITE70,
            border_radius=8
        )
        self.ejes_field = ft.Dropdown(
            label="Ejes",
            options=[ft.dropdown.Option(ejes_opciones) for ejes_opciones in self.ejes_opciones],
            border_color=ft.Colors.GREY_400,
            border_radius=8,
            enable_filter=True,
            filled=True,
            bgcolor=ft.Colors.WHITE70,
            fill_color=ft.Colors.WHITE54   
        )

        self.cliente_field = ft.TextField(
            label="Cliente",
            width=320,
            expand=True,
            height=50,
            border_color=ft.Colors.GREY_400,
            bgcolor=ft.Colors.WHITE70,
            border_radius=8
        )
        self.conductor_field = ft.TextField(
            label="Conductor",
            width=320,
            expand=True,
            height=50,
            border_color=ft.Colors.GREY_400,
            bgcolor=ft.Colors.WHITE70,
            border_radius=8
        )
        self.date_field = ft.TextField(
            label="Fecha y Hora",
            value=datetime.now().strftime("%d/%m/%Y %H:%M"),
            disabled=True,
            width=160,
            height=50,
            border_color=ft.Colors.GREY_400,
            bgcolor=ft.Colors.WHITE70,
            border_radius=8
        )
        
        # Componentes para mostrar estado de conexión
        self.connection_status = ft.Text(
            "Desconectado",
            color=ft.Colors.RED,
            weight=ft.FontWeight.BOLD
        )
        
        # Lista para mostrar historial de pesos
        self.weight_history_list = ft.ListView(
            height=125,
            spacing=2,
            width=250,
            divider_thickness=1,
            auto_scroll=True
        )
        
        # Lista para mostrar registro de eventos
        self.event_log_list = ft.ListView(
            height=125,
            spacing=2,
            divider_thickness=1,
            auto_scroll=True
        )
        
        # Botones
        self.connect_button = ft.ElevatedButton(
            "Conectar",
            icon=ft.Icons.CABLE,
            on_click=self.toggle_connection,
            bgcolor=ft.Colors.BLUE,
            color=ft.Colors.WHITE
        )
        
        self.refresh_ports_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip="Actualizar puertos",
            on_click=self.refresh_ports
        )
        
        self.config_button = ft.IconButton(
            icon=ft.Icons.SETTINGS,
            tooltip="Configuración avanzada",
            
        )
        
        self.register_button = ft.ElevatedButton(
            "Registrar",
            #icon=ft.Icons.SCALE,
            bgcolor=self.color_principal,
            color=ft.Colors.WHITE,
            on_click=self.register_weight
        )

        self.cancelar_button = ft.ElevatedButton(
            "Cancelar",
            #icon=ft.Icons.SCALE,
            bgcolor=ft.Colors.WHITE,
            color=self.color_principal,
            #on_click=self.register_weight
        )

        self.print_button = ft.ElevatedButton(
            "Imprimir",
            bgcolor="#4df0dd",
            color=self.color_principal,
            on_click=self.imprimir_pesaje
        )
        
        self.Proceso_bascula = ft.Dropdown(
            label="Proceso pesaje",
            options=[ft.dropdown.Option(tipo_vehiculo) for tipo_vehiculo in self.Proceso_opciones],
            border_color=ft.Colors.GREY_400,
            border_radius=8,
            enable_filter=True,
            filled=True,
            bgcolor=ft.Colors.WHITE70,
            fill_color=ft.Colors.WHITE54   
        )

        self.overlay_imprimir = ft.Container(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Mensaje", size=20, weight="bold", color=self.color_principal,),
                    ft.Text("Imprimiendo..."),
                    
                    ft.Row([
                        ft.TextButton("OK", on_click=self.close_overlay_imprimir)
                    ], alignment=ft.MainAxisAlignment.END)
                ], tight=True),
                width=300,
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=15,
                    color=ft.Colors.BLACK45,
                )
            ),
            width=page.width,
            height=page.height,
            # bgcolor=ft.Colors.BLACK54,  # Negro semi-transparente
            alignment=ft.alignment.center,
        )
        # Crear la vista
        self.view = self.create_tab_view()

    
    def update_tab_enturnados(self):
        if not self.pagination or not self.vehicle_data:
            return
            
        # Obtener todos los datos actuales
        all_data = self.vehicle_data.data
        
        # Filtrar por estados específicos
        estados_a_mostrar = ["En proceso", "Finalizado", "Transito entrando", "Autorizado"]
        filtered_data = [item for item in all_data if item['Estado'] in estados_a_mostrar]
        
        # Si no hay datos después del filtro, mostrar mensaje
        if not filtered_data:
            empty_table = ft.DataTable(
                columns=[ft.DataColumn(ft.Text("Sin datos"))],
                rows=[ft.DataRow(cells=[ft.DataCell(ft.Text("No hay datos con los estados seleccionados"))])],
            )
            self._update_table_in_tab(empty_table)
            return
        
        # Calcular índices para la numeración
        start_index = 1
            
        # Crear una tabla personalizada (sin las 2 últimas columnas)
        custom_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("#", size=13, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("CONDUCTOR", size=13)),
                ft.DataColumn(ft.Text("PLACA", size=13)),
                ft.DataColumn(ft.Text("PRODUCTO", size=13)),
                ft.DataColumn(ft.Text("EJES", size=13)),
                ft.DataColumn(ft.Text("PROCESO", size=13)),
                ft.DataColumn(ft.Text("CLIENTE", size=13)),
                ft.DataColumn(ft.Text('ESTADO', size=11)),
                # Omitimos  EDIT
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=6,
            vertical_lines=ft.border.BorderSide(1, ft.Colors.GREY_300),
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_300),
            sort_column_index=0,
            column_spacing=8,
            heading_row_height=30,
            data_row_min_height=25,
            data_row_max_height=35,
        )
        
        for i, item in enumerate(filtered_data):
            row_number = start_index + i
            estado = item['Estado']
            estado_color = self.ui_components.get_estado_color(estado)
            custom_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row_number), size=12, weight=ft.FontWeight.BOLD, color=self.color_principal)),
                        ft.DataCell(ft.Text(item['NombreConductor'], size=11)),
                        ft.DataCell(ft.Text(item['Placa'], size=12, weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(item['Producto'], size=11)),
                        ft.DataCell(ft.Text(item['Ejes'], size=11)),
                        ft.DataCell(ft.Text(item['Proceso'], size=11)),
                        ft.DataCell(ft.Text(item['Cliente'], size=11)),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(estado,
                                    weight=ft.FontWeight.BOLD,
                                    color = (
                                        ft.Colors.GREEN_600 if estado in ["Transito entrando"]
                                        else ft.Colors.RED_700 if estado == "En inspeccion"
                                        else ft.Colors.YELLOW_900 if estado == "Autorizado"
                                        else ft.Colors.BLACK87 if estado in ["En proceso", "Autorizado"]
                                        else ft.Colors.WHITE
                                    ),
                                size=11),
                                bgcolor=estado_color,
                                border_radius=6,
                                padding=1,
                                height=25,
                                width=120,
                                alignment=ft.alignment.center
                            )
                        ),
                    ]
                )
            )
        
        # Reemplazar la tabla actual en el contenido de la pestaña
        tab_content = self.tabs_content[0]
        container = tab_content.content.controls[1]  # El Container que contiene ListView
        container.content.controls = [custom_table]
        
        self.page.update()

#################################################################

    def update_tab_containers(self):
        # Verificar si existe el gestor de pesajes, si no, crearlo
        if not hasattr(self, 'pesajes_manager'):
            self.pesajes_manager = PesajesManager()
        
        # Obtener el folio actual (basado en la fecha seleccionada)
        folio_actual = self.pesajes_manager.get_current_folio()
        
        # Obtener los datos resumidos de pesajes
        pesajes_data = self.pesajes_manager.get_pesajes_resumen(folio_actual)
        
        # Si no hay datos, mostrar mensaje
        if not pesajes_data:
            empty_table = ft.DataTable(
                columns=[ft.DataColumn(ft.Text("Sin datos"))],
                rows=[ft.DataRow(cells=[ft.DataCell(ft.Text("No hay datos de pesajes para esta fecha"))])],
            )
            # Reemplazar la tabla actual en el contenido de la pestaña
            tab_content = self.tabs_content[1]
            container = tab_content.content.controls[1]  # El Container que contiene ListView
            container.content.controls = [empty_table]
            self.page.update()
            return
        
        custom_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("PROCESO", size=13, weight=ft.FontWeight.BOLD), numeric=True),
                ft.DataColumn(ft.Text("PLACA", size=13)),
                ft.DataColumn(ft.Text("TT / DESTINO", size=13)),
                ft.DataColumn(ft.Text("PESO INICIAL", size=13), numeric=True),
                ft.DataColumn(ft.Text("PESO FINAL", size=13), numeric=True),
                ft.DataColumn(ft.Text("PESO BRUTO", size=13), numeric=True),
                ft.DataColumn(ft.Text("", size=13 )),
            ],
            heading_row_color=ft.Colors.PURPLE_100,
            horizontal_margin= 12,
            rows=[],
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=6,
            vertical_lines=ft.border.BorderSide(1, ft.Colors.GREY_300),
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_300),
            sort_column_index=0,
            column_spacing=8,
            heading_row_height=30,
            data_row_min_height=25,
            data_row_max_height=35,
        )
        
        for item in pesajes_data:
            # Movemos la definición de vehicle_id aquí, dentro del bucle donde 'item' está definido
            vehicle_id = item.get('ID', None)  # Uso .get() para evitar KeyError si no existe la clave
            
            edit_button = ft.IconButton(
                icon=ft.Icons.EDIT_NOTE,  # Icono de edición de notas, más sutil
                icon_color=self.color_principal,
                tooltip="Editar vehículo.",
                icon_size=20,  # Tamaño más pequeño
                on_click=lambda e, id=vehicle_id: self.on_edit_click(id) if self.on_edit_click else None
            )
            
            custom_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(item["Proceso"]), size=12, weight=ft.FontWeight.BOLD, color=self.color_principal)),
                        ft.DataCell(ft.Text(str(item["Contenedor"]) if item["Contenedor"] else "", size=11)),
                        ft.DataCell(ft.Text(str(item["TerminalTractor"]) if item["TerminalTractor"] else "", size=11)),
                        ft.DataCell(ft.Text(str(item["Peso Inicial"]) if item["Peso Inicial"] else "0", size=11)),
                        ft.DataCell(ft.Text(str(item["Peso Final"]) if item["Peso Final"] else "0", size=11)),
                        ft.DataCell(ft.Text(str(item["Bruto"]) if item["Bruto"] else "0", size=11, 
                                        weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700)),
                        ft.DataCell(edit_button),
                    ]
                )
            )
        
        # Reemplazar la tabla actual en el contenido de la pestaña
        tab_content = self.tabs_content[1]
        container = tab_content.content.controls[1]  # El Container que contiene ListView
        container.content.controls = [custom_table]
        
        # Actualizar la fecha en el botón (si existe)
        if hasattr(self, 'fecha_button'):
            self.fecha_button.text = self.pesajes_manager.fecha_seleccionada.strftime('%d/%m/%Y')
        
        print("Actualizando Vh externos")

        self.page.update()
    

    def update_tab_externos(self):
        # Lógica para actualizar la pestaña de Externos
        # Similar a update_tab_enturnados pero con la lógica específica para Externos
        print("Actualizando pestaña Externos")
        # Crear una nueva tabla con los datos de Externos
        # ...
        
    def page_resize(self, e):
        if hasattr(self, 'overlay_imprimir') and self.overlay_imprimir in self.page.overlay:
            self.overlay_imprimir.width = self.page.width
            self.overlay_imprimir.height = self.page.height
            self.page.update()

    # Asignar el manejador de eventos
        self.page.on_resize = self.page_resize

    def show_overlay_imprimir(self):
        print("Mostrando mensaje de impresión...")
        # Añadir el overlay a la página
        self.page.overlay.append(self.overlay_imprimir)
        self.page.update()
        
        # Crear temporizador para cerrar automáticamente después de 3 segundos
        self.auto_close_timer = threading.Timer(2.0, self.close_overlay_timeout)
        self.auto_close_timer.daemon = True  # El timer se cancelará si la aplicación termina
        self.auto_close_timer.start()

    def close_overlay_timeout(self):
        print("Cerrando mensaje automáticamente después de 3 segundos...")
        # Usamos update directo en lugar de invoke_async
        if hasattr(self, 'overlay_imprimir') and self.overlay_imprimir in self.page.overlay:
            self.page.overlay.remove(self.overlay_imprimir)
            self.page.update()

    def close_overlay_imprimir(self, e):
        print("Cerrando mensaje de impresión manualmente...")
        # Cancelar el temporizador si existe
        if hasattr(self, 'auto_close_timer') and self.auto_close_timer.is_alive():
            self.auto_close_timer.cancel()
        
        # Remover el overlay de la página
        self.page.overlay.remove(self.overlay_imprimir)
        self.page.update()

    def imprimir_pesaje(self, e):
        print("Botón de imprimir presionado")
        # Usar el método de overlay con cierre automático
        self.show_overlay_imprimir()

    def create_stat_cards(self):
        return {
            'total': StatCard(
                title="Peso Actual (kg)", 
                color=self.color_secundario,
                page=self.page,
                serial_manager=self.serial_manager,
                parent_view=self  # Pasar referencia a self (BasculaView)
            )
        }
    
    def create_port_dropdown(self):
        return ft.Dropdown(
            label="Puerto Serial",
            hint_text="Seleccionar puerto",
            width=200,
            options=[
                ft.dropdown.Option(port) for port in self.available_ports
            ],
            border_color=ft.Colors.GREY_400,
            border_radius=8
        )
    
    def create_tab_view(self):
        # Definir el método para cambiar de pestaña
        def on_tab_change(e):
            self.tabs_container.content = self.tabs_content[e.control.selected_index]
            
            # Ejecutar la función correspondiente según la pestaña seleccionada
            if e.control.selected_index == 0:
                self.update_tab_enturnados()
            elif e.control.selected_index == 1:
                self.update_tab_containers()  # Función para la segunda pestaña
            elif e.control.selected_index == 2:
                self.update_tab_externos()    # Función para la tercera pestaña
                
            self.page.update()
        
        # Crear tabla vacía inicialmente
        initial_table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text("Presione actualizar..."))],
            rows=[]
        )
        
        # Definir el contenido de cada pestaña
        tab1_content = ft.Container(
            content=ft.Column([
                ft.Row(
                    [
                        ft.Text("Total Vehículos", size=15, weight=ft.FontWeight.BOLD, color=self.color_principal),
                                    ft.ElevatedButton(
                                        "Actualizar", 
                                        on_click=lambda e: self.update_data_callback(), #update_tab_enturnados
                                        icon=ft.Icons.REFRESH
                                    ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(
                    content=ft.ListView(
                        controls=[initial_table],  # Comienza con una tabla vacía
                        expand=True,
                        auto_scroll=True
                    ),
                    padding=ft.padding.only(left=0, right=0, bottom=0, top=0),
                    bgcolor=ft.colors,
                    border_radius=10,
                    expand=True,
                    height=300,
                ),
                # Añadir paginación
                #self.pagination.get_controls() if self.pagination else ft.Text(""),
            ]),
            padding=10,
            bgcolor=ft.colors.WHITE,
            border_radius=5,
            border=ft.border.all(1, ft.Colors.GREY_300),
            expand=True,
        )
        
        tab2_content = ft.Container(
            content=ft.Column([
                ft.Row(
                    [
                        ft.Text("Total Vehículos", size=15, weight=ft.FontWeight.BOLD, color=self.color_principal),
                                    ft.ElevatedButton(
                                        "Actualizar", 
                                        on_click=lambda e: self.update_tab_containers(), 
                                        icon=ft.Icons.REFRESH
                                    ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(
                    content=ft.ListView(
                        controls=[initial_table],  # Comienza con una tabla vacía
                        expand=True,
                        auto_scroll=True
                    ),
                    padding=ft.padding.only(left=0, right=0, bottom=0, top=0),
                    bgcolor=ft.colors,
                    border_radius=10,
                    expand=True,
                    height=300,
                ),

            ]),
            padding=10,
            bgcolor=ft.colors.WHITE,
            border_radius=5,
            border=ft.border.all(1, ft.Colors.GREY_300),
            expand=True,
        )
        
        tab3_content = ft.Container(
            content=ft.Column([
                ft.Row(
                    [
                        ft.Text("Total Vehículos", size=15, weight=ft.FontWeight.BOLD, color=self.color_principal),
                                    ft.ElevatedButton(
                                        "Actualizar", 
                                        on_click=lambda e: self.update_tab_externos(), 
                                        icon=ft.Icons.REFRESH
                                    ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(
                    content=ft.ListView(
                        controls=[initial_table],  # Comienza con una tabla vacía
                        expand=True,
                        auto_scroll=True
                    ),
                    padding=ft.padding.only(left=0, right=0, bottom=0, top=0),
                    bgcolor=ft.colors,
                    border_radius=10,
                    expand=True,
                    height=300,
                ),

            ]),
            padding=10,
            bgcolor=ft.colors.WHITE,
            border_radius=5,
            border=ft.border.all(1, ft.Colors.GREY_300),
            expand=True,
        )
        
        self.tabs_content = [tab1_content, tab2_content, tab3_content] # Guardamos el contenido de las pestañas en una lista
        
        # Contenedor para el contenido de las pestañas (inicialmente muestra la primera pestaña)
        self.tabs_container = ft.Container(
            content=self.tabs_content[0],  # Por defecto mostramos la primera pestaña
            expand=True,
        )
        
        tabs = ft.Tabs( # Primero define las pestañas
            selected_index=0,
            animation_duration=200,
            tabs=[
                ft.Tab(
                    tab_content=ft.Text(
                        "Enturnados",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=self.color_principal,
                    ),
                    icon=ft.icons.BUS_ALERT_OUTLINED,
                ),
                ft.Tab(
                    tab_content=ft.Text(
                        "Externos",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=self.color_principal,
                    ),
                    icon=ft.icons.DELIVERY_DINING,
                ),
                ft.Tab(
                    tab_content=ft.Text(
                        "Containers",
                        size=16,
                        #bgcolor=ft.Colors.BLACK12,
                        weight=ft.FontWeight.BOLD,
                        color=self.color_principal,
                    ),
                    icon=ft.icons.DELIVERY_DINING,
                )
            ],
            on_change=on_tab_change,
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Container(
                                        content=ft.Column(
                                            [
                                                ft.Row(
                                                    [
                                                        ft.Text(
                                                            "Control de Báscula",
                                                            size=24,
                                                            weight=ft.FontWeight.BOLD,
                                                            color=self.color_principal
                                                        ),
                                                    ],
                                                ),
                                                
                                                ft.Row(
                                                    [
                                                        self.Proceso_bascula,
                                                        self.placa_field,
                                                        self.ejes_field,
                                                        self.date_field
                                                    ],
                                                ),
                                                ft.Row(
                                                    [
                                                        self.conductor_field,
                                                        self.cliente_field,
                                                    ],
                                                    expand=True,
                                                    width=('inf'),
                                                ),
                                            ],  
                                            alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                            spacing=5,
                                            expand=True,
                                            width=700,
                                        ),
                                        border=None,
                                        border_radius=8,
                                        margin=ft.margin.only(left=0, right=0, bottom=0, top=0),
                                        padding=ft.padding.only(left=0, right=10, bottom=0, top=0),
                                    ),
                                ],
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        # Contenedor con Stack y dimensiones explícitas
                                        ft.Container(
                                            content=ft.Stack(
                                                controls=[
                                                    # Fondo transparente para dar dimensión al Stack
                                                    ft.Container(
                                                        height=150,
                                                        width=500,
                                                        bgcolor=ft.colors.TRANSPARENT,
                                                    ),
                                                    # Tarjeta de estadística con posición absoluta
                                                    ft.Container(
                                                        content=self.stat_cards['total'].get_card(),
                                                        left=10,
                                                        right=15,
                                                        top=10,
                                                    )
                                                ],
                                                width=500,
                                                height=150
                                            ),
                                            # Aseguramos que el contenedor del Stack tenga dimensiones
                                            width=500,
                                            height=150
                                        ),
                                        ft.Row(
                                            [
                                                self.cancelar_button,
                                                self.register_button,
                                                self.print_button,
                                            ],
                                            alignment=ft.MainAxisAlignment.SPACE_EVENLY
                                        ),
                                    ],
                                    expand=True,   
                                ),
                                margin=ft.margin.only(top=0),
                                padding=ft.padding.only(right=5),
                                width=500,
                                expand=True,
                            ),
                        ],        
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        spacing=5,
                    ),
                    # Formulario principal
                    ft.Container(
                        content=ft.Column(
                            [
                                # Fila de botones de configuración
                                # ft.Row(
                                    # [
                                        # self.port_dropdown,
                                        # self.refresh_ports_button,
                                        # self.config_button,
                                        # self.connect_button,
                                        # self.connection_status
                                    # ],
                                    # alignment=ft.MainAxisAlignment.START,
                                    # spacing=10
                                #),
                                # Sección de historial y eventos
                                ft.Row(
                                    [
                                        ft.Column(
                                            [
                                                ft.Text(
                                                    "Historial de pesos",
                                                    weight=ft.FontWeight.BOLD,
                                                    color=self.color_principal,
                                                    size=15
                                                ),
                                                ft.Container(
                                                    content=self.weight_history_list,
                                                    border=ft.border.all(1, ft.Colors.GREY_300),
                                                    bgcolor=ft.Colors.WHITE,
                                                    border_radius=5,
                                                    padding=5,
                                                    expand=True
                                                )
                                            ],
                                            spacing=5
                                        ),
                                        # Registro de eventos
                                        ft.Column(
                                            [
                                                ft.Text(
                                                    "Registro de eventos",
                                                    weight=ft.FontWeight.BOLD,
                                                    color=self.color_principal,
                                                    size=15
                                                ),
                                                ft.Container(
                                                    content=self.event_log_list,
                                                    border=ft.border.all(1, ft.Colors.GREY_300),
                                                    bgcolor=ft.Colors.WHITE,
                                                    border_radius=5,
                                                    padding=5,
                                                    expand=True
                                                )
                                            ],
                                            spacing=5,
                                            expand=True
                                        )
                                    ],
                                    spacing=10,
                                    
                                    expand=True,
                                ),
                                # Sistema de pestañas mejorado
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            tabs,
                                            # Contenedor para mostrar el contenido de la pestaña seleccionada
                                            self.tabs_container,
                                        ],
                                        spacing=0,
                                        height=480,
                                        expand=True,
                                    ),
                                    bgcolor=ft.Colors.TRANSPARENT
                                ),
                                
                            ],
                            spacing=10,
                        ),
                        padding=10,
                        bgcolor=ft.Colors.TRANSPARENT,
                        border_radius=10,
                        margin=ft.margin.only(top=0),
                        border=None,
                    ),
                ],
                spacing=10,
            ),
            padding=ft.padding.only(left=20, right=20),
            margin=ft.margin.only(top=1),
            expand=True,
            #bgcolor=self.color_secundario,
            #border_radius=10,
            #border=ft.border.all(1, ft.Colors.GREY_300),
        )
    #########################################################

    def refresh_ports(self, e=None):
        """Actualizar lista de puertos disponibles"""
        self.available_ports = self.serial_manager.get_available_ports()
        
        # Actualizar dropdown con los puertos disponibles
        self.port_dropdown.options.clear()
        for port in self.available_ports:
            self.port_dropdown.options.append(ft.dropdown.Option(port))
        
        self.page.update()
    
    def toggle_connection(self, e):
        """Conectar o desconectar del puerto serial"""
        if not self.serial_manager.is_connected:
            # Si no hay puerto seleccionado, mostrar error
            if not self.port_dropdown.value:
                error_msg = "Por favor seleccione un puerto"
                self.add_event_log(error_msg, is_error=True)
                
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(error_msg),
                    bgcolor=ft.Colors.RED
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            # Obtener la configuración actual para el registro
            settings = self.serial_manager.get_connection_settings()
            self.add_event_log(f"Intentando conectar a {self.port_dropdown.value} con {settings['baudrate']} baudios")
            
            # Intentar conectar
            if self.serial_manager.connect(self.port_dropdown.value):
                # Conexión exitosa
                connect_msg = f"Conectado a {self.port_dropdown.value}"
                self.add_event_log(connect_msg)
                
                self.connection_status.value = "Conectado"
                self.connection_status.color = ft.Colors.GREEN
                self.connect_button.text = "Desconectar"
                self.connect_button.bgcolor = ft.Colors.RED
                
                # Registrar callback para datos recibidos
                self.serial_manager.set_data_callback(self.on_data_received)
                
                # Deshabilitar selección de puerto y configuración mientras está conectado
                self.port_dropdown.disabled = True
                self.refresh_ports_button.disabled = True
                self.config_button.disabled = True
            else:
                # Error de conexión
                error_msg = f"Error al conectar a {self.port_dropdown.value}. Verifique el puerto."
                self.add_event_log(error_msg, is_error=True)
                
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(error_msg),
                    bgcolor=ft.Colors.RED
                )
                self.page.snack_bar.open = True
        else:
            # Desconectar
            port_name = self.port_dropdown.value
            self.serial_manager.disconnect()
            
            disconnect_msg = f"Desconectado de {port_name}"
            self.add_event_log(disconnect_msg)
            
            self.connection_status.value = "Desconectado"
            self.connection_status.color = ft.Colors.RED
            self.connect_button.text = "Conectar"
            self.connect_button.bgcolor = ft.Colors.GREEN
            
            # Habilitar selección de puerto y configuración nuevamente
            self.port_dropdown.disabled = False
            self.refresh_ports_button.disabled = False
            self.config_button.disabled = False
        
        self.page.update()
    
    def on_data_received(self, data):
        """Callback para cuando se recibe datos del puerto serial"""
        try:
            # Procesar el dato
            clean_data = data.strip() if isinstance(data, str) else str(data)
            
            try:
                weight_value = float(clean_data)
                
                # AQUÍ ES DONDE SE CONFIGURA EL NÚMERO DE DECIMALES
                # Cambia el .2f por .0f para ningún decimal, .1f para 1 decimal,
                # .3f para 3 decimales, etc.
                decimal_places = 0  # Puedes cambiar esto a 0, 1, 3, etc.
                format_string = f"{{:.{decimal_places}f}}"
                self.current_weight = format_string.format(weight_value)
                
                # Añadir al historial con timestamp
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.add_to_weight_history(f"{timestamp} - {self.current_weight} kg")
            except ValueError:
                # Si no es un número, mostramos el texto tal cual
                self.current_weight = clean_data
                
                # Registrar como evento
                self.add_event_log(f"Mensaje del dispositivo: {clean_data}")
            
            # Actualizar la tarjeta de peso
            self.stat_cards['total'].set_value(self.current_weight)
            
            # Actualizar la UI desde el hilo principal
            self.page.update()

        except Exception as e:
            error_msg = f"Error procesando datos: {e}"
            print(error_msg)
            self.add_event_log(error_msg, is_error=True)
    
    def register_weight(self, e):
        """Registrar el peso actual en la base de datos"""
        if not self.placa_field.value:
            error_msg = "Por favor ingrese la placa del vehículo"
            self.add_event_log(error_msg, is_error=True)
            
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(error_msg),
                bgcolor=ft.Colors.RED
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        if not self.serial_manager.is_connected:
            error_msg = "No hay conexión con báscula. Conecte primero."
            self.add_event_log(error_msg, is_error=True)
            
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(error_msg),
                bgcolor=ft.Colors.RED
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
            
        # Actualizar fecha/hora actual
        current_time = datetime.now()
        self.date_field.value = current_time.strftime("%d/%m/%Y %H:%M")
        
        # Registrar el peso 
        success_msg = f"REGISTRO - Placa: {self.placa_field.value} - Peso: {self.current_weight} kg - Proceso: {self.Proceso_bascula.value} - Ejes: {self.ejes_field.value} - Cliente: {self.cliente_field.value}"
        self.add_event_log(success_msg)
        
        # Añadir al historial en formato especial (puede ser útil para reportes)
        timestamp = current_time.strftime("%d/%m/%Y %H:%M:%S")
        history_entry = f"{timestamp} | {self.placa_field.value} | {self.current_weight} kg"
        self.add_to_weight_history(history_entry)
        
        # Aquí iría la lógica para guardar en la base de datos
        # Por ahora solo mostramos un mensaje
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(success_msg),
            bgcolor=ft.Colors.GREEN
        )
        self.page.snack_bar.open = True
        self.page.update()
    

    def show_config_modal(self, e=None):
        """Mostrar el modal de configuración del puerto serial"""
        try:
            print("Botón de configuración presionado")
            
            # Importar el modal
            from views.serial_config_modal import SerialConfigModal
            
            # Crear instancia del modal, pasando la referencia a BasculaView
            config_modal = SerialConfigModal(
                page=self.page,
                serial_manager=self.serial_manager,  
                on_config_saved=self.on_config_saved,
                parent_view=self  # Esta es la clave: pasar self como parent_view
            )
            
            config_modal.show()
            
        except Exception as e:
            print(f"ERROR al mostrar el modal de configuración: {e}")
            import traceback
            traceback.print_exc()


        
    def update_connection_status(self, is_connected, port_name):
        """
        Actualiza el estado de conexión en la UI
        Esta función es llamada desde SerialConfigModal cuando se conecta/desconecta
        """
        if is_connected:
            # Actualizar estado de conexión
            self.connection_status.value = "Conectado"
            self.connection_status.color = ft.Colors.GREEN
            self.connect_button.text = "Desconectar"
            self.connect_button.bgcolor = ft.Colors.RED
            
            # Registrar callback para datos recibidos
            self.serial_manager.set_data_callback(self.on_data_received)
            
            # Deshabilitar selección de puerto y configuración mientras está conectado
            self.port_dropdown.disabled = True
            self.refresh_ports_button.disabled = True
            self.config_button.disabled = True
        else:
            # Actualizar estado de desconexión
            self.connection_status.value = "Desconectado"
            self.connection_status.color = ft.Colors.RED
            self.connect_button.text = "Conectar"
            self.connect_button.bgcolor = ft.Colors.GREEN
            
            # Habilitar selección de puerto y configuración nuevamente
            self.port_dropdown.disabled = False
            self.refresh_ports_button.disabled = False
            self.config_button.disabled = False
        
        self.page.update()

    def on_serial_connect(self, port_name):
        """Llamado cuando el puerto serial se conecta desde el modal"""
        connect_msg = f"Conectado a {port_name}"
        self.add_event_log(connect_msg)
        # Actualizar otros elementos de la UI según sea necesario
        self.page.update()

    def close_modal(self, e, modal):
        modal.open = False
        self.page.update()

    def save_config(self, e, modal):
        # Obtener el nuevo valor del campo de texto (primer control en la columna)
        new_value = modal.content.controls[0].value
        self.set_value(new_value)
        
        # Cerrar el modal
        modal.open = False
        self.page.update()
    
    def add_to_weight_history(self, weight_entry):
        """Añadir un peso al historial"""
        # Limitar tamaño del historial
        if len(self.weight_history) >= self.MAX_HISTORY_SIZE:
            self.weight_history.pop(0)  # Eliminar el más antiguo
            
        # Añadir nueva entrada
        self.weight_history.append(weight_entry)
        
        # Actualizar ListView
        self.weight_history_list.controls.clear()
        for entry in self.weight_history:
            self.weight_history_list.controls.append(
                ft.ListTile(
                    title=ft.Text(entry, size=12),
                    dense=True,
                    leading=ft.Icon(ft.Icons.SCALE, color=self.color_principal, size=16)
                )
            )
    
    def add_event_log(self, message, is_error=False):
        """Añadir un evento al registro"""
        # Limitar tamaño del registro
        if len(self.event_log) >= self.MAX_LOG_SIZE:
            self.event_log.pop(0)  # Eliminar el más antiguo
            
        # Añadir nueva entrada
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"{timestamp} - {message}"
        self.event_log.append(entry)
        
        # Actualizar ListView
        self.event_log_list.controls.clear()
        for log_entry in self.event_log:
            self.event_log_list.controls.append(
                ft.ListTile(
                    title=ft.Text(
                        log_entry, 
                        size=12,
                        color=ft.Colors.RED if is_error else None
                    ),
                    dense=True,
                    leading=ft.Icon(
                        ft.Icons.ERROR if is_error else ft.Icons.INFO,
                        color=ft.Colors.RED if is_error else ft.Colors.BLUE,
                        size=16
                    )
                )
            )
        # Forzar actualización de la interfaz
        self.page.update()
    
    def on_config_saved(self):
        """Callback para cuando se guarda la configuración"""
        # Mostrar mensaje con la nueva configuración
        settings = self.serial_manager.get_connection_settings()
        config_msg = f"Nueva configuración: {settings['baudrate']} baudios"
        
        # Registrar en el log de eventos
        self.add_event_log(config_msg)
        
        # Mostrar notificación
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(config_msg),
            bgcolor=ft.Colors.GREEN
        )
        self.page.snack_bar.open = True
        self.page.update()
        
    def get_view(self):
        return self.view


class StatCard:
    """Clase para representar una tarjeta de estadísticas"""
    
    def __init__(self, title, color, icon=None, page=None, serial_manager=None, parent_view=None):
        self.title = title
        self.color = color
        self.icon = icon
        self.value = "00.0"  # Valor inicial
        self.page = page
        self.serial_manager = serial_manager  # Usar el serial_manager pasado como argumento
        self.parent_view = parent_view  # Referencia a BasculaView
        self.card_content = self.create_card_content()

    def create_card_content(self):
        return ft.Row(
            [
                ft.Column(
                    [
                        ft.Text(
                            self.value,
                            size=45,
                            weight=ft.FontWeight.BOLD,
                            color="#4df0dd"
                        ),
                        ft.Text(
                            self.title,
                            size=15,
                            color=ft.Colors.WHITE
                        ),
                    ],
                    spacing=5,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Icon(
                    self.icon if self.icon else ft.Icons.SCALE,
                    size=40,
                    color="#4df0dd"
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            expand=True,
        )
    
    def on_hover(self, e):
        self.card_content.opacity = 0.9 if e.data == "true" else 1
        if self.page:
            self.page.update()
    
# Modifica el método show_config_modal en la clase StatCard

    def show_config_modal(self, e):
        try:
            print("Botón de configuración presionado")
            
            # Importar el modal
            from views.serial_config_modal import SerialConfigModal
            
            # Crear el modal pasando la referencia a BasculaView
            config_modal = SerialConfigModal(
                page=self.page,
                serial_manager=self.serial_manager,
                on_config_saved=self.update_config,
                parent_view=self.parent_view  # Pasar la referencia a BasculaView
            )
            
            config_modal.show()
            
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    def update_config(self):
        """Esta función se llama cuando se guarda la configuración"""
        print("Configuración actualizada")

    def get_card(self):
        return ft.Card(
            content=ft.Container(
                content=self.card_content,
                padding=ft.padding.only(left=20, right=20, bottom=10, top=10),
                border_radius=10,
                expand=True,
                bgcolor=ft.Colors.PURPLE,
                on_click=self.show_config_modal,
                on_hover=self.on_hover
            ),
            elevation=50,
            width=300
        )
    
    def set_value(self, value):
        self.value = value
        self.card_content.controls[0].controls[0].value = value
        if self.page:
            self.page.update()

    def on_data_received(self, data):
        """Función que se llama cuando se reciben datos del puerto serial"""
        # print(f"Datos recibidos: {data}")
        # Procesa los datos según tus necesidades
        # Por ejemplo, actualizar el valor de la tarjeta
        self.set_value(data)