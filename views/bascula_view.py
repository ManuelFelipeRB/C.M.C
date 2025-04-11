import flet as ft
from datetime import datetime

class BasculaView:
    def __init__(self, page, color_principal, color_secundario):
        self.page = page
        self.color_principal = color_principal
        self.color_secundario = color_secundario
        self.stat_cards = self.create_stat_cards()  # Inicializar stat_cards antes de crear la vista
        self.view = self.create_view()

    def create_stat_cards(self):
        # Esta función debe crear y devolver un diccionario con las tarjetas estadísticas
     
        return {
            'total': StatCard(title="Peso Total", color=ft.Colors.BLUE_GREY_200),
        }

    def create_view(self):
        return ft.Container(
                content=ft.Column(
                    [
                        ft.Column(
                            [   
                            ft.Row(
                                [
                                    ft.Text(
                                        "Control de Báscula",
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                        color=self.color_principal,
                                        expand=True
                                    ),
                                ft.Column(
                                [ 
                                    # Este contenedor empujará la tarjeta hacia la derecha
                                    ft.Container(expand=True),  
                                    # La tarjeta aparecerá a la derecha
                                    self.stat_cards['total'].get_card(),

                                 ],
                                 expand=False
                                ),

                                ],
                            # Asegúrate de que la fila ocupe todo el ancho disponible
                            expand=True
                            ),
                        ],

                        ),
                        # Descripción
                        ft.Container(

                            content=ft.Text(
                                "Esta sección permitirá gestionar el pesaje de vehículos.",
                                size=16,
                            ),
                            padding=10,
                            bgcolor=self.color_secundario,
                            border_radius=10,
                            margin=ft.margin.only(top=20),
                        ),
                        
                        # Formulario principal
                        ft.Container(
                            content=ft.Column(
                                [
                                ft.Row(
                                        [
                                            ft.Text("Placa:", weight=ft.FontWeight.BOLD),
                                            ft.TextField(width=200),
                                            ft.Text("Proceso:", weight=ft.FontWeight.BOLD),
                                            ft.TextField(width=350),
                                            ft.Text("Fecha/Hora:", weight=ft.FontWeight.BOLD),
                                                    ft.TextField(
                                                        width=200, 
                                                        value=datetime.now().strftime("%d/%m/%Y %H:%M"), 
                                                        disabled=True,
                                                    ),
                                        ],
                                        alignment=ft.MainAxisAlignment.START,
                                        spacing=10,
                                        expand=True
                                    ),
  
                                # Botón de acción
                                ft.ElevatedButton(
                                    "Registrar Peso",
                                    icon=ft.Icons.SCALE,
                                    bgcolor=self.color_principal,
                                    color=ft.Colors.WHITE,
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
            padding=ft.padding.all(20),
            expand=True,
            visible=False,
        )
    
    def get_view(self):
        return self.view


class StatCard:
    """Clase para representar una tarjeta de estadísticas"""
    def __init__(self, title, color, icon=None):
        self.title = title
        self.color = color
        self.icon = icon
        self.value = ""  # Valor inicial vacío
    
    def get_card(self):
        return ft.Card(
            content=ft.Container(
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(self.value, size=30, weight=ft.FontWeight.BOLD, color=self.color),
                                ft.Text(self.title, size=15, color="#424242"),
                            ],
                            spacing=5,
                            alignment=ft.alignment.top_right,
                        ),
                        # Icono opcional
                        ft.Icon(self.icon, size=35, color=self.color) if self.icon else ft.Container(),
                    ],
                    alignment=ft.alignment.center,
                    expand=True,
                ),
                padding=ft.padding.only(left=20, right=20, bottom=10, top=5),
                border_radius=10,
                expand=True,
                opacity=1,
                bgcolor=self.color,  # Añado transparencia para que sea más sutil
            ),
            elevation=4,
        )
    
    def set_value(self, value):
        """Método para actualizar el valor de la tarjeta"""
        self.value = value