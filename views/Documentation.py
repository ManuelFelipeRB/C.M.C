import flet as ft
import os

# Crear una clase DocumentationView similar a tus otras vistas

class DocumentationView:
    def __init__(self, page, color_principal, color_secundario):
        self.page = page
        self.color_principal = color_principal
        self.color_secundario = color_secundario
        self.view = self.create_view()
        
    def create_view(self):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Documentación del Sistema",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=self.color_principal
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                self.create_doc_section(
                                    "Estado inicial",
                                    """Como opción mejora continua al procedimiento de pesaje de Vehículos & Unidades de Carga se realiza el diseño 
                                    del módulo adicional para repesaje de Contenedores e Isotanques, en el cual se desarrolla una herramienta para 
                                    el control del cargue de los isotanques de aromáticos, mediante la implementación de un formulario de Windows 
                                    que permite Verificar y obtener la información correspondiente a los pesajes requeridos para el llenado de las 
                                    unidades de carga tipo isotanque, el cual incorpora las recientes mejoras al Archivo de Control de enturne con 
                                    el manejo del pesaje automático."""
                                ),
                                self.create_doc_section(
                                    "Funcionalidades Clave",
                                    """- Registro dinámico de información de carga
                                    - Seguimiento de unidades terrestres y fluviales
                                    - Control de trazabilidad de eventos
                                    - Generación automática de tiquetes de báscula
                                    - Registro detallado de información de carga"""
                                ),
                                self.create_doc_section(
                                    "Proceso de Registro",
                                    """1. Captura inicial de datos mediante módulo de Anuncios
                                    2. Alimentación de base de datos local
                                    3. Generación de tiquetes de báscula
                                    4. Registro detallado de información de carga"""
                                ),
                                self.create_doc_section(
                                    "Características de Seguridad",
                                    """- Información metrológica del instrumento
                                    - Fecha de calibración
                                    - Código de verificación SIMEL"""
                                ),
                            ],
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        bgcolor=ft.Colors.WHITE,
                        border_radius=10,
                        padding=20,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        expand=True,
                    )
                ],
                spacing=20,
                expand=True,
            ),
            padding=ft.padding.all(30),
            expand=True,
            visible=False,  # Inicialmente oculto
        )
    
    def create_doc_section(self, title, content):
        """Crea una sección de documentación con título y contenido"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=self.color_principal),
                    ft.Container(
                        content=ft.Text(content, size=14),
                        margin=ft.margin.only(left=10),
                    ),
                ],
            ),
            margin=ft.margin.only(bottom=20),
        )
    
    def get_view(self):
        return self.view