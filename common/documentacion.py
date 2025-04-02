import flet as ft
from flet import icons, Page, Markdown

class ResponsiveMenuPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Informacion Proyecto Enturne"
        
        # Responsive page configuration
        self.page.window_min_width = 600  # Minimum width
        self.page.window_min_height = 400  # Minimum height
        self.page.padding = 0  # Remove default padding
        
        # Enable window resizing and responsiveness
        self.page.window_resizable = True

        # Responsive header text
        self.header_text = ft.Text(
            "Guía al usuario", 
            size=20,  # Responsive font size
            weight=ft.FontWeight.BOLD,
        )
        
        # Initial page selection
        self.selected_index = 0
        
        # Create navigation rail destinations
        self.navigation_destinations = [
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.Icons.HOME_OUTLINED, color=ft.Colors.WHITE),
                selected_icon_content=ft.Icon(ft.Icons.HOME, color=ft.Colors.PURPLE_400),
                label_content=ft.Text("Inicio", size=14, color=ft.Colors.WHITE),
            ),
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.Icons.BOOK_OUTLINED,color=ft.Colors.WHITE),
                selected_icon_content=ft.Icon(ft.Icons.BOOK, color=ft.Colors.PURPLE_400),
                label_content=ft.Text("Modelo Actual", size=14, color=ft.Colors.WHITE),
            )
        ]
        
        # Create navigation rail
        self.navigation_rail = self._create_fixed_navigation_rail()

        # Create pages
        self.pages = self._create_menu_pages()
        
        # Current page content container with responsive properties
        self.current_page_content = ft.Container(
            expand=True,
            padding=10,
            alignment=ft.alignment.top_left,
            width=None,  # Allow dynamic width
        )
        
        # Add responsive scaling
        self.page.on_resize = self._handle_page_resize

        # Setup layout
        self._setup_page_layout()

    def _handle_page_resize(self, e):
        """Handle page resize events for responsive design."""
        # Dynamically adjust navigation rail height
        rail_height = max(self.page.height, 400)  # Minimum height of 400
        
        # Adjust navigation rail width based on window size
        if self.page.width < 800:  # Mobile or narrow view
            self.navigation_rail.width = 80  # Narrow rail
            self.navigation_rail.height = rail_height
            self.header_text.size = 16  # Smaller header
        else:  # Desktop view
            self.navigation_rail.width = 150  # Standard rail
            self.navigation_rail.height = rail_height
            self.header_text.size = 20  # Standard header
        
        self.page.update()

    def _create_fixed_navigation_rail(self) -> ft.NavigationRail:
        return ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            width=150,  # Match container width
            height=900,  # Fixed height
            leading=ft.Column([
                ft.Container(
                    content=ft.Text("Menú General", size=18, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    alignment=ft.alignment.center,
                    width=150  # Match NavigationRail width
                ),
                ft.Divider(color=ft.Colors.WHITE54),
            ]),
            destinations=self.navigation_destinations,
            on_change=self._handle_rail_change,
            bgcolor=ft.Colors.PURPLE_600
        )

    def _create_menu_pages(self):
        pages = [
            {
                "config": self.navigation_destinations[0],
                "content": self._create_page(
                    alignment=ft.alignment.top_left,
                    md1 = """
                    
                   
# **Estado inicial:**
### Control Entrune

```
Como opción mejora continua al procedimiento de pesaje de Vehículos & Unidades de Carga se realiza el diseño del módulo adicional para repesaje de Contenedores e Isotanques, en el cual se desarrolla una herramienta para el control del cargue de los isotanques de aromáticos, mediante la implementación de un formulario de Windows que permite Verificar y obtener la información correspondiente a los pesajes requeridos para el llenado de las unidades de carga tipo isotanque,  el cual incorpora las recientes mejoras al Archivo de Control de enturne con el manejo del pesaje automático, realizadas con la integración de los indicadores de peso mediante una conexión directa a través del protocolo de comunicación serial RS232 con los equipos PC de cada báscula del área de canopy. Dicha solución aprovecha estas mejoras realizadas y aumenta la confiabilidad en el proceso de pesaje ya que los datos de pesaje no son digitados por el operador si no que son tomados directamente desde el instrumento, evitando el error humano en la digitación de los valores correspondientes al peso de los vehículos.

El desarrollo está soportado en una base datos local bajo el ambiente de Access, que es alimentada inicialmente con los datos generados desde el módulo de Anuncios creado para que el equipo comercial realice de manera más dinámica la entrega de información de las unidades de carga que ingresan vía terrestre, de éste anuncio se obtienen los datos iniciales para alimentar la base local del Archivo Control Enturne con Numero de contenedor, Tara, Fabricante, Consecutivo, mediante el formulario principal, para el control de los repesajes se crea una tabla que lleva la trazabilidad de los eventos realizados con fecha, hora, tara de vehículo vacío, peso bruto, peso neto, usuario, placa de vehículo.

Igualmente de éste mismo formulario se obtienen los tiquetes de báscula parciales los cuales se generan automáticamente, se imprimen y se adhieren al formato de orden de cargue, de la misma manera se genera el tiquete de báscula final que se obtiene en formato PDF, dicho tiquete se rediseñó para poder visualizar además de la información de la carga y pesos, la información metrológica del instrumento fecha de calibración y código de verificación en SIMEL que brinde al cliente la seguridad en la transparencia de la información entregada y la confiabilidad del proceso.
```
                    """
                )
            },

            
            {
                "config": self.navigation_destinations[1],
                "content": self._create_page(
                    alignment=ft.alignment.top_left,
                    md1 = """

# Resumen del Modelo Actual

## Introducción al Sistema

Desarrollo basado en base de datos local con Access, diseñado para optimizar el proceso de registro de unidades de carga.

## Funcionalidades Clave

- Registro dinámico de información de carga
- Seguimiento de unidades terrestres y fluviales
- Control de trazabilidad de eventos

## Proceso de Registro

1. Captura inicial de datos mediante módulo de Anuncios
2. Alimentación de base de datos local
3. Generación de tiquetes de báscula
4. Registro detallado de información de carga

## Características de Seguridad

- Información metrológica del instrumento
- Fecha de calibración
- Código de verificación SIMEL
                    """
                )
            },
        ]
        return pages

    def _create_page(self, alignment=ft.alignment.top_center, md1: str = "") -> ft.Container:
        """Create a page using Markdown content with strict top alignment."""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Markdown(
                        md1,
                        selectable=True,
                        extension_set="gitHubWeb",
                        width=None,  # Allow full width
                        expand=True,  # Allow expansion
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,  # Stretch to full width
                spacing=10,
                expand=True,
            ),
            bgcolor=ft.Colors.BLUE_GREY_50,
            padding=10,
            expand=True,
            alignment=alignment,
        )

    def _setup_page_layout(self):
        """Set up the overall page layout with fixed navigation rail height."""
        # Initial page content
        self.current_page_content.content = self.pages[0]['content']

        # Main layout with fixed height navigation and content
        main_content = ft.Row(
            controls=[
                # Navigation Rail with Fixed Height
                ft.Container(
                    content=self.navigation_rail,
                    width=150,  # Fixed width
                    height=900,  # Fixed height
                ),
                # Vertical Divider
                ft.VerticalDivider(width=1),
                # Page Content
                ft.Column(
                    controls=[
                        ft.Container(
                            content=self.header_text,
                            padding=10,
                            height=50,  # Fixed header height
                        ),
                        self.current_page_content
                    ],
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                    alignment=ft.MainAxisAlignment.START,
                    spacing=10
                )
            ],
            expand=True,
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        # Clear previous content and add new layout
        self.page.controls.clear()
        self.page.add(main_content)
        self.page.update()

    def _handle_rail_change(self, e):
        """Handle navigation rail selection change."""
        self.selected_index = e.control.selected_index
        self.current_page_content.content = self.pages[self.selected_index]['content']
        self.page.update()

def main(page: Page):
    """Main application entry point with responsive settings."""
    page.padding = 0
    page.window_min_width = 600
    page.window_min_height = 400
    page.window_resizable = True
    page.scroll= "Auto"  # Enable scrolling if content overflows
    
    # Set responsive themes and color scheme
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.bgcolor = ft.Colors.WHITE
    
    ResponsiveMenuPage(page)

# Run the application with additional parameters
ft.app(target=main)  # Optional: open in web browser for testing