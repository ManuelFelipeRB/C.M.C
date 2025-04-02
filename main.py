import flet as ft

from datetime import datetime
from common.database_manager import DatabaseManager
from EditVehicle_modal import EditVehicleModal
from EditVehicle_modal import VehicleData

# Importar las clases
from common.pagination import PaginationManager
from common.filter import FilterManager
from common.ui_components import UIComponents
from common.stat_card import StatCard
from views.cmc_view import CMCView
from views.enturne_view import EnturneView
from views.bascula_view import BasculaView

class ControlCargaApp:
    def __init__(self, page):
        self.page = page
        self.setup_page()
        
        # Colores personalizados
        self.color_principal = "#8c4191"  # Morado
        self.color_secundario = "#f1ffff"  # Azul claro
        
        # Estado actual
        self.fecha_seleccionada = datetime.now()
        self.fecha_numerica_excel = (self.fecha_seleccionada - datetime(1900, 1, 1)).days + 2
        self.current_view = "cmc"  # Vista actual (cmc, enturne, bascula)
        
        # Inicializar componentes
        self.ui_components = UIComponents(page, self.color_principal)
        self.vehicle_data = VehicleData()
        self.pagination = PaginationManager(page)
        self.filter_manager = FilterManager(page, self.vehicle_data, self.on_filter_change)
        
        # Crear el modal de edición
        self.edit_modal = EditVehicleModal(
            page, 
            self.vehicle_data.db_manager, 
            self.on_vehicle_updated
        )
        
        # Configurar callbacks
        self.ui_components.set_edit_callback(self.show_edit_modal)
        self.pagination.set_page_change_callback(self.update_data_table)
        
        # Crear componentes UI
        self.menu_navegacion = self.ui_components.create_navigation_rail(
            self.handle_date_change, 
            self.fecha_seleccionada,
            self.handle_navigation_change
        )
        self.top_bar = self.ui_components.create_top_bar(
            self.toggle_menu,
            self.filter_manager.get_search_container()
        )
        self.data_table = self.ui_components.create_data_table()
        self.stat_cards = self.create_stat_cards()
        
        # Inicializar vistas
        self.cmc_view = CMCView(
            page, 
            self.color_principal, 
            self.stat_cards, 
            self.data_table, 
            self.pagination,
            self.update_data
        )
        self.enturne_view = EnturneView(page, self.color_principal)
        self.bascula_view = BasculaView(page, self.color_principal, self.color_secundario)
        
        # Obtener referencias a las vistas
        self.view_cmc = self.cmc_view.get_view()
        self.view_enturne = self.enturne_view.get_view()
        self.view_bascula = self.bascula_view.get_view()
        
        # Construir la interfaz de usuario
        self.build_ui()
        
        # Cargar datos iniciales
        self.refresh_data()
    
    def setup_page(self):
        self.page.title = "Control de Movimientos de Carga"
        self.page.padding = 0
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window.maximizable = True
        self.page.window.maximized = True
    
    def create_stat_cards(self):
        # Crear tarjetas estadísticas y mantener referencia a ellas
        cards = {
            'total': StatCard(
                self.page,
                ft.Icons.VISIBILITY_OUTLINED,
                "Total Enturnados",
                self.color_principal,
                lambda e: self.handle_card_click('todos')
            ),
            'entrando': StatCard(
                self.page,
                ft.Icons.DIRECTIONS_BUS_OUTLINED,
                "Transito Entrando",
                self.color_principal,
                lambda e: self.handle_card_click('entrando')
            ),
            'proceso': StatCard(
                self.page,
                ft.Icons.COMPARE_ARROWS_OUTLINED,
                "Proceso",
                self.color_principal,
                lambda e: self.handle_card_click('en_proceso')
            ),
            'finalizado': StatCard(
                self.page,
                ft.Icons.VERIFIED_OUTLINED,
                "Finalizado",
                self.color_principal,
                lambda e: self.handle_card_click('finalizado')
            ),
            'pendiente': StatCard(
                self.page,
                ft.Icons.WARNING_AMBER_OUTLINED,
                "Pendientes",
                self.color_principal,
                lambda e: self.handle_card_click('pendiente')
            )
        }
        
        # Marcar la tarjeta de total como activa inicialmente
        cards['total'].set_active(True)
        
        return cards
    
    def handle_card_click(self, filter_name):
        self.filter_manager.apply_filter(filter_name)
        self.page.update()
    
    def update_data(self, e=None):
        # Limpiar el campo de búsqueda
        self.filter_manager.search_field.value = ""
        self.filter_manager.search_text = ""

        # Establecer el indicador como splash de la página
        self.page.overlay.append(self.progress_container) 
        self.page.update()
        
        # Limpiar los datos actuales
        # Vaciar filas de data_table para que no se vean datos antiguos
        self.data_table.rows.clear()
        self.page.update()
        
        # Recargar datos desde la base de datos
        self.vehicle_data.load_data(self.fecha_numerica_excel)
        
        # Actualizar tarjetas estadísticas
        self.update_stat_cards()
        
        # Aplicar filtro actual y eso actualizará la tabla
        self.filter_manager.apply_filter(self.filter_manager.current_filter)
        
        # Ocultar indicador de carga
        self.page.overlay.remove(self.progress_container)
        self.page.update()
    
    def handle_navigation_change(self, e):
        """Manejar cambios en la navegación"""
        # El índice seleccionado determina qué vista mostrar
        selected_index = e.control.selected_index
        
        if selected_index == 0:
            self.current_view = "cmc"
        elif selected_index == 1:
            self.current_view = "enturne"
        elif selected_index == 2:
            self.current_view = "bascula"
            
        # Actualizar la vista
        self.update_view()
        
    def update_view(self):
        """Actualizar la vista según la opción seleccionada"""
        # Ocultar todas las vistas
        self.view_cmc.visible = False
        self.view_enturne.visible = False
        self.view_bascula.visible = False
        
        # Mostrar solo la vista actual
        if self.current_view == "cmc":
            self.view_cmc.visible = True
        elif self.current_view == "enturne":
            self.view_enturne.visible = True
        elif self.current_view == "bascula":
            self.view_bascula.visible = True
            
        self.page.update()
            
    def build_ui(self):
        # Crear un indicador de progreso circular personalizado
        self.progress_indicator = ft.Column(
            [
                ft.ProgressRing(width=40, height=40, stroke_width=4, color=self.color_principal),
                ft.Text("Actualizando...", style="TextThemeStyle", weight=ft.FontWeight.NORMAL)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        )
        
        # Crear un contenedor para centrar el indicador en la pantalla
        self.progress_container = ft.Container(
            content=self.progress_indicator,
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
            expand=True
        )
        
        # Contenido principal con vistas alternativas
        contenido_principal = ft.Column(
            [
                self.top_bar,
                ft.Stack(
                    [
                        self.view_cmc,      # Vista de CMC
                        self.view_enturne,  # Vista de Enturne
                        self.view_bascula,  # Vista de Báscula
                    ]
                )
            ],
            expand=True,
        )
        
        # Establecer la vista inicial
        self.update_view()
        
        # Estructura de la página con el menú lateral
        self.page.add(
            ft.Row(
                [
                    ft.Container(
                        content=self.menu_navegacion,
                        bgcolor=self.color_principal,
                    ),
                    ft.VerticalDivider(width=1),
                    contenido_principal,
                ],
                spacing=0,
                tight=True,
                expand=True,
            )
        )
    
    def refresh_data(self):
        # Cargar datos desde la base de datos
        self.page.overlay.append(self.progress_container)
        self.page.update()

        self.vehicle_data.load_data(self.fecha_numerica_excel)
        # Aplicar filtro actual
        self.filter_manager.apply_filter(self.filter_manager.current_filter)
        # Actualizar tarjetas estadísticas
        self.update_stat_cards()
        self.page.overlay.remove(self.progress_container)
        self.page.update()

    def toggle_menu(self, e):
        self.menu_navegacion.extended = not self.menu_navegacion.extended
        self.page.update()
    
    def handle_date_change(self, e):
        # Actualizar la fecha seleccionada
        self.fecha_seleccionada = e.control.value
        self.fecha_numerica_excel = (self.fecha_seleccionada - datetime(1900, 1, 1)).days + 2
        
        # Actualizar el texto del botón con la nueva fecha
        self.ui_components.update_date_button(self.fecha_seleccionada)
        
        # Refrescar datos con la nueva fecha
        self.refresh_data()
    
    def on_filter_change(self, filtered_data):
        # Actualizar la paginación con los datos filtrados
        self.pagination.update_data(filtered_data)
        # Actualizar la tabla con los datos de la página actual
        self.update_data_table()
        # Actualizar estado visual de las tarjetas
        self.update_card_states()
        # Asegurar que la página se actualice
        self.page.update()
    
    def update_data_table(self):
        # Obtener datos de la página actual
        current_page_data = self.pagination.get_current_page_data()
        
        # Calcular el índice de inicio para la numeración basado en la página actual
        start_index = (self.pagination.current_page - 1) * self.pagination.items_per_page + 1
        
        # Actualizar la tabla con estos datos y el índice de inicio correcto
        self.ui_components.update_data_table(self.data_table, current_page_data, start_index)
        
    def update_stat_cards(self):
        # Actualizar valores de las tarjetas estadísticas
        totals = self.vehicle_data.totals
        self.stat_cards['total'].update_value(totals['total_pesajes'])
        self.stat_cards['entrando'].update_value(totals['total_entrando'])
        self.stat_cards['proceso'].update_value(totals['total_proceso'])
        self.stat_cards['finalizado'].update_value(totals['total_finalizados'])
        self.stat_cards['pendiente'].update_value(totals['total_pendiente'])
    
    def update_card_states(self):
        # Actualizar el estado visual de cada tarjeta según el filtro activo
        current_filter = self.filter_manager.current_filter
        for card_name, card in self.stat_cards.items():
            is_active = (
                (card_name == 'total' and current_filter == 'todos') or
                (card_name == 'entrando' and current_filter == 'entrando') or
                (card_name == 'proceso' and current_filter == 'en_proceso') or
                (card_name == 'finalizado' and current_filter == 'finalizado') or
                (card_name == 'pendiente' and current_filter == 'pendiente')
            )
            card.set_active(is_active)

    def show_edit_modal(self, vehicle_id):
        """Mostrar el modal de edición con los datos del vehículo seleccionado"""
        # Obtener información del vehículo usando el ID
        vehicle_data = self.vehicle_data.db_manager.get_vehicle_by_id(vehicle_id)
        
        if vehicle_data:
            placa = vehicle_data["Placa"]
            print(f"Modo Edición para vehículo con placa: {placa} (ID: {vehicle_id})")
        else:
            print(f"Modo Edición para ID: {vehicle_id}")
            
        self.edit_modal.show(vehicle_id)

    
    def on_vehicle_updated(self):
        """Callback para cuando un vehículo ha sido actualizado"""
        # Refrescar los datos después de la actualización
        self.refresh_data()

# Función principal para iniciar la aplicación
def main(page: ft.Page):
    app = ControlCargaApp(page)

# Ejecutar la aplicación
if __name__ == "__main__":
    ft.app(target=main)