import flet as ft
from datetime import datetime

class BasculaView:
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
                        "Control de Báscula",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=self.color_principal
                    ),
                    ft.Container(
                        content=ft.Text(
                            "Esta sección permitirá gestionar el pesaje de vehículos.",
                            size=16
                        ),
                        padding=10,
                        bgcolor=self.color_secundario,
                        border_radius=10,
                        margin=ft.margin.only(top=20),
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text("Placa:", weight=ft.FontWeight.BOLD),
                                        ft.TextField(width=200),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.Row(
                                    [
                                        ft.Text("Peso (kg):", weight=ft.FontWeight.BOLD),
                                        ft.TextField(width=200),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.Row(
                                    [
                                        ft.Text("Fecha/Hora:", weight=ft.FontWeight.BOLD),
                                        ft.TextField(width=200, value=datetime.now().strftime("%d/%m/%Y %H:%M"), disabled=True),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
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
            padding=ft.padding.all(30),
            expand=True,
            visible=False,
        )
    
    def get_view(self):
        return self.view