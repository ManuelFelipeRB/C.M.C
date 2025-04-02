import flet as ft

class FilterManager:
    def __init__(self, page, vehicle_data, on_filter_change):
        self.page = page
        self.vehicle_data = vehicle_data
        self.on_filter_change = on_filter_change
        self.current_filter = "todos"
        self.search_text = ""
        
        # Añadir el botón de limpieza
        self.clear_button = ft.IconButton(
            icon=ft.Icons.CLEAR,
            on_click=self.clear_search,
            icon_size=18,
            height=30,
            width=30,
            bgcolor=ft.Colors.TRANSPARENT,
        )
        # Componentes UI de búsqueda
        self.search_field = ft.TextField(
            hint_text="Buscar aquí...",
            prefix_icon=ft.Icons.SEARCH,
            suffix_icon=self.clear_button,  # Agregar el botón como sufijo
            border_radius=20,
            border_color=ft.Colors.GREY_400,
            height=30,
            width=400,
            on_change=self.on_search_change
        )
        
        # Crear contenedor para la barra de búsqueda
        self.search_container = ft.Container(
            content=self.search_field,
            margin=ft.margin.only(left=20),
        )
    
    def clear_search(self, e):
        self.search_field.value = ""
        self.search_text = ""
        self.apply_filter_and_search()
        self.page.update()

    def get_search_container(self):
        return self.search_container
    
    def on_search_change(self, e):
        self.search_text = e.control.value
        self.apply_filter_and_search()
        
    def apply_filter(self, filter_name):
        self.current_filter = filter_name
        self.apply_filter_and_search()
            
    def apply_filter_and_search(self):
        # Primero aplicar el filtro
        self.vehicle_data.apply_filter(self.current_filter)
        
        # Luego aplicar la búsqueda si hay texto
        if self.search_text:
            filtered_data = self.vehicle_data.search_data(self.search_text)
        else:
            filtered_data = self.vehicle_data.filtered_data
            
        # Notificar el cambio
        self.on_filter_change(filtered_data)