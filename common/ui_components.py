import flet as ft

import flet as ft
import subprocess
import os
import sys

from datetime import datetime

class UIComponents:
    def __init__(self, page, fecha_button):
        self.page = page
        self.color_principal ="#9C5BAC" # color_principal #8c4191
        self.color_secundario = "#f1ffff"
        self.fecha_button = None  # Referencia al botón de fecha
        self.on_edit_click = None  # Callback para el evento de edición
    
    def set_edit_callback(self, callback):
        self.on_edit_click = callback
    
    def get_estado_color(self, estado):
        if estado == "Finalizado":
            return "#0b8d36"  # Verde
        elif estado == "En proceso":
            return "#fbff12"  # Amarillo
        elif estado == "Enturnado":
            return "#910c0c"  # Rojo
        elif estado == "No enturnado":
            return "#0aacf2"  # azul
        elif estado == "Anunciado":
            return "#6b16ba"  # Morado
        elif estado == "Autorizado":
            return "#ffffa3"  # Crema
        elif estado == "En inspeccion":
            return "#ddafaf"  # ROJO claro
        elif estado == "Revision documental":
            return "#6fada6"  # Aguamarina
        elif estado == "Transito entrando":
            return "#acfab9"  # Verde claro
        elif estado == "Transito saliendo":
            return "#8c8c8c"  # Gris claro
        elif estado == "Ingresó":
            return "#b0abae"  # Gris
        else:
            return "#777777"  # Gris oscuro
    
    def create_loading_indicator(self, visible=False):
        return ft.Container(
            content=ft.ProgressRing(width=40, height=40, color=self.color_principal, visible=visible)
        )
    
    def create_data_table(self):
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("#", size=13, weight=ft.FontWeight.BOLD, color=self.color_principal)),
                ft.DataColumn(ft.Text("CONDUCTOR", size=13, color=self.color_principal)),
                ft.DataColumn(ft.Text("PLACA", size=13, color=self.color_principal)),
                ft.DataColumn(ft.Text("PRODUCTO", size=13, color=self.color_principal)),
                ft.DataColumn(ft.Text("EJES", size=13, color=self.color_principal)),
                ft.DataColumn(ft.Text("PROCESO", size=13, color=self.color_principal)),
                ft.DataColumn(ft.Text("CLIENTE", size=13, color=self.color_principal)),
                ft.DataColumn(ft.Text("ESTADO", size=13, color=self.color_principal)),
                ft.DataColumn(ft.Text("", size=13 )),
                
            ],
            
            rows=[],
            heading_row_color=ft.colors.BLUE_GREY_50,
            border=ft.border.all(1, ft.Colors.GREY_200),
            border_radius=6,
            vertical_lines=ft.border.BorderSide(1, ft.Colors.GREY_200),
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_200),
            sort_column_index=0,
            column_spacing=6,
            width=100,
            divider_thickness=0,
            heading_row_height=30,
            data_row_min_height=25,
            data_row_max_height=35,
        )
    
    def update_data_table(self, data_table, data, start_index=1):
        # Limpiar la tabla actual
        data_table.rows.clear()
        
        # Agregar las filas con los datos
        for i, item in enumerate(data):
            # Calcular el número de fila teniendo en cuenta la paginación
            row_number = start_index + i
            
            estado = item['Estado']
            color_estado = self.get_estado_color(estado)
            
            # Obtener el ID del vehículo
            vehicle_id = item['ID']
            
            edit_button = ft.IconButton(
                icon=ft.Icons.EDIT_NOTE,  # Icono de edición de notas, más sutil
                icon_color=self.color_principal,
                tooltip="Editar vehículo.",
                icon_size=20,  # Tamaño más pequeño
                on_click=lambda e, id=vehicle_id: self.on_edit_click(id) if self.on_edit_click else None
            )
            
            data_table.rows.append(
                ft.DataRow(
                    cells=[
                        # Celda de numeración
                        ft.DataCell(ft.Text(str(row_number), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.DEEP_PURPLE_900)),
                        ft.DataCell(ft.Text(item['NombreConductor'], size=11)),
                        ft.DataCell(ft.Text(item['Placa'], size=12, weight=ft.FontWeight.BOLD, color=self.color_principal)),
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
                                bgcolor=color_estado,
                                border_radius=6,
                                padding=1,
                                height=25,
                                width=120,
                                alignment=ft.alignment.center
                            )
                        ),
                        ft.DataCell(edit_button),
                    ]
                )
            )
        self.page.update()

    def create_navigation_rail(self, on_date_change, fecha_seleccionada, on_navigation_change=None):
        # Crear el botón de fecha
        self.fecha_button = ft.ElevatedButton(
            text=f"{fecha_seleccionada.strftime('%d/%m/%Y')}",
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda e: self.show_date_picker(e, on_date_change, fecha_seleccionada),
            style=ft.ButtonStyle(
                bgcolor=self.color_secundario,
            ),
        )
        
        # Crear el menú de navegación
        nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=70,
            bgcolor=self.color_principal,
            min_extended_width=220,
            extended=True,
            
            # Agregar header con el botón de fecha
            leading=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Fecha de Folio:", 
                        color=self.color_secundario,
                        size=14,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(
                        content=self.fecha_button,
                        padding=ft.padding.only(top=10),
                    ),
                ]),
                padding=ft.padding.only(top=5, bottom=20 ,left=10, right=10),
                alignment=ft.alignment.center,
            ),
            
            destinations=[
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(ft.Icons.DASHBOARD_OUTLINED, color=self.color_secundario, size=20),
                    selected_icon_content=ft.Icon(ft.Icons.DASHBOARD_SHARP, color=self.color_principal, size=20),
                    label_content=(
                        ft.Text(
                            "C . M . C",
                            color=self.color_secundario,
                            size=14,
                            weight=ft.FontWeight.BOLD,
                        )
                    ),
                ),
                
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(ft.Icons.DEPARTURE_BOARD_OUTLINED, color=self.color_secundario, size=20),
                    selected_icon_content=ft.Icon(ft.Icons.DEPARTURE_BOARD, color=self.color_principal, size=20),
                    label_content=(
                        ft.Text(
                            "Enturne",
                            color=self.color_secundario,
                            size=14,
                            weight=ft.FontWeight.BOLD,
                        )
                    ),
                ),

                ft.NavigationRailDestination(
                    icon_content=ft.Icon(ft.Icons.SCALE_OUTLINED, color=self.color_secundario, size=20),
                    selected_icon_content=ft.Icon(ft.Icons.SCALE, color=self.color_principal, size=20),
                    label_content=(
                        ft.Text(
                            "Báscula",
                            color=self.color_secundario,
                            size=14,
                            weight=ft.FontWeight.BOLD,
                        )
                    ),
                ),
            ],
            on_change=on_navigation_change,
        )
        
        return nav_rail
    
    def update_date_button(self, fecha):
        if self.fecha_button:
            self.fecha_button.text = f"{fecha.strftime('%d/%m/%Y')}"
            self.page.update()
    
    def show_date_picker(self, e, on_date_change, fecha_actual):
        self.page.open(
            ft.DatePicker(
                first_date=datetime(year=2022, month=1, day=1),
                last_date=datetime.now(),
                current_date=fecha_actual,
                on_change=on_date_change,
            )
        )
    
    def create_top_bar(self, menu_toggle_func, search_container, notification_click_handler):
        return ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.MENU,
                        icon_color=ft.Colors.BLACK,
                        on_click=menu_toggle_func,
                        icon_size=25,
                    ),
                    search_container,
                    ft.IconButton(
                        icon=ft.Icons.HELP_SHARP, 
                        icon_color=ft.Colors.GREY_600, 
                        alignment=ft.alignment.top_right,
                        on_click=notification_click_handler,  # Agregar el manejador de eventos
                        tooltip="Abrir documentación"  # Tooltip informativo
                    ),
                    #ft.IconButton(icon=ft.Icons.ACCOUNT_CIRCLE, icon_color=ft.Colors.GREY_600),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.only(left=20, right=20, bottom=5, top=15),
            bgcolor=ft.Colors
        )