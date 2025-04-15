import flet as ft
from datetime import datetime, timedelta
import os
import csv
import tempfile
import json

class WeightReportDialog:
    """Diálogo para generar reportes de pesaje simples"""
    def __init__(self, page, db_manager=None):
        self.page = page
        self.db_manager = db_manager

        # Definir primero los métodos que serán usados como callbacks
        self.generate_report = self._generate_report
        self.export_to_csv = self._export_to_csv
        self.close_dialog = self._close_dialog
        self.on_date_change = self._on_date_change
        
        # Fecha por defecto (hoy)
        self.default_date = datetime.now()
        
        # Controles del formulario
        self.date_picker = ft.DatePicker(
            first_date=datetime(2022, 1, 1),
            last_date=datetime.now(),
            current_date=self.default_date,
            on_change=self.on_date_change
        )
        
        self.date_button = ft.OutlinedButton(
            text=self.default_date.strftime("%d/%m/%Y"),
            icon=ft.icons.CALENDAR_TODAY,
            on_click=lambda _: self.page.overlay.append(self.date_picker)
        )
        
        self.placa_field = ft.TextField(
            label="Placa (opcional)",
            hint_text="Filtrar por placa",
            width=200
        )
        
        # Simulamos algunos registros de ejemplo para la demo
        self.sample_data = self._generate_sample_data()
        
        # Botones de acciones
        self.generate_button = ft.ElevatedButton(
            "Mostrar registros",
            icon=ft.icons.SUMMARIZE,
            on_click=self.generate_report,
            bgcolor="#8c4191",
            color=ft.Colors.WHITE
        )
        
        self.export_button = ft.OutlinedButton(
            "Exportar a CSV",
            icon=ft.icons.DOWNLOAD,
            on_click=self.export_to_csv
        )
        
        self.close_button = ft.TextButton(
            "Cerrar",
            on_click=self.close_dialog
        )
        
        # Crear el diálogo
        self.dialog = ft.AlertDialog(
            title=ft.Text("Reportes de Pesaje"),
            content=self.create_dialog_content(),
            actions=[self.close_button, self.export_button, self.generate_button],
            actions_alignment=ft.MainAxisAlignment.END
        )
    def _generate_sample_data(self):
        """Generar datos de muestra para la demo"""
        data = []
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        # Datos para hoy
        for i in range(5):
            time = today.replace(hour=9+i, minute=15)
            data.append({
                "id": i+1,
                "placa": f"ABC{100+i}",
                "peso": 1000 + i*100,
                "proceso": "Cargue" if i % 2 == 0 else "Descargue",
                "fecha": time,
                "estable": True
            })
        
        # Datos para ayer
        for i in range(3):
            time = yesterday.replace(hour=10+i, minute=30)
            data.append({
                "id": i+6,
                "placa": f"XYZ{200+i}",
                "peso": 2000 + i*150,
                "proceso": "Control" if i % 2 == 0 else "Cargue",
                "fecha": time,
                "estable": True
            })
            
        return data
    
    def create_dialog_content(self):
        """Crear el contenido del diálogo"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Generar reporte de pesajes", size=16, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    
                    # Filtros
                    ft.Text("Filtros", size=14, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text("Fecha:"),
                                    self.date_button
                                ],
                                spacing=5
                            ),
                            ft.Column(
                                [
                                    ft.Text("Placa:"),
                                    self.placa_field
                                ],
                                spacing=5
                            )
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=20
                    ),
                    
                    ft.Divider(),
                    
                    # Nota explicativa
                    ft.Container(
                        content=ft.Text(
                            "Este módulo permite generar reportes de pesajes filtrados por fecha y placa. "
                            "Seleccione los criterios y presione 'Mostrar registros' para ver los datos, "
                            "o 'Exportar a CSV' para descargar un archivo con los resultados.",
                            size=12,
                            italic=True
                        ),
                        padding=10,
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=5
                    )
                ],
                spacing=10,
                scroll=ft.ScrollMode.AUTO
            ),
            width=500,
            height=300,
            padding=20
        )
    
    def on_date_change(self, e):
        """Manejar cambio de fecha"""
        selected_date = e.control.value
        if selected_date:
            # Actualizar el texto del botón
            date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
            self.date_button.text = date_obj.strftime("%d/%m/%Y")
            self.page.update()
        def generate_report(self, e):
            """Generar reporte completo"""
        try:
            # Obtener fecha seleccionada
            date_str = self.date_button.text
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
            
            # Obtener placa si se ingresó
            placa_filter = self.placa_field.value.upper() if self.placa_field.value else None
            
            # Filtrar datos de muestra
            filtered_data = []
            for record in self.sample_data:
                record_date = record["fecha"].date()
                if record_date == date_obj.date():
                    if placa_filter is None or placa_filter in record["placa"]:
                        filtered_data.append(record)
            
            # Crear ventana con resultados
            if filtered_data:
                # Crear DataTable con los registros
                table = ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("ID")),
                        ft.DataColumn(ft.Text("Placa")),
                        ft.DataColumn(ft.Text("Peso (kg)")),
                        ft.DataColumn(ft.Text("Proceso")),
                        ft.DataColumn(ft.Text("Fecha/Hora")),
                        ft.DataColumn(ft.Text("Estado"))
                    ],
                    rows=[],
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    vertical_lines=ft.border.BorderSide(1, ft.Colors.GREY_300),
                    horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_300)
                )
                
                # Agregar filas con los registros
                for record in filtered_data:
                    table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(record["id"]))),
                                ft.DataCell(ft.Text(record["placa"])),
                                ft.DataCell(ft.Text(f"{record['peso']:.2f}")),
                                ft.DataCell(ft.Text(record["proceso"] or "")),
                                ft.DataCell(ft.Text(record["fecha"].strftime("%d/%m/%Y %H:%M"))),
                                ft.DataCell(
                                    ft.Container(
                                        content=ft.Text(
                                            "Estable" if record["estable"] else "Inestable",
                                            color=ft.Colors.WHITE,
                                            size=12
                                        ),
                                        bgcolor=ft.Colors.GREEN if record["estable"] else ft.Colors.ORANGE,
                                        border_radius=5,
                                        padding=5,
                                        width=80,
                                        height=25,
                                        alignment=ft.alignment.center
                                    )
                                )
                            ]
                        )
                    )
                
                # Crear ventana con resultados
                report_dialog = ft.AlertDialog(
                    title=ft.Text(f"Reporte de pesajes - {date_str}"),
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(f"Filtros: Placa={placa_filter or 'Todas'}"),
                                ft.Divider(),
                                ft.Container(
                                    content=table,
                                    height=400,
                                    border=ft.border.all(1, ft.colors.GREY_300),
                                    border_radius=5,
                                    padding=10
                                )
                            ],
                            scroll=ft.ScrollMode.AUTO
                        ),
                        width=700,
                        height=500,
                        padding=20
                    ),
                    actions=[
                        ft.TextButton("Cerrar", on_click=lambda e: setattr(report_dialog, "open", False))
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                    on_dismiss=lambda e: self.page.update()
                )
                
                self.page.dialog = report_dialog
                report_dialog.open = True
                self.page.update()
            else:
                # No hay registros
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("No se encontraron registros con los filtros seleccionados"),
                    bgcolor=ft.Colors.ORANGE
                )
                self.page.snack_bar.open = True
                self.page.update()
        except Exception as e:
            print(f"Error al generar reporte: {e}")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error al generar reporte: {str(e)}"),
                bgcolor=ft.Colors.RED
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def export_to_csv(self, e):
        """Exportar datos a archivo CSV"""
        try:
            # Obtener fecha seleccionada
            date_str = self.date_button.text
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
            
            # Obtener placa si se ingresó
            placa_filter = self.placa_field.value.upper() if self.placa_field.value else None
            
            # Filtrar datos de muestra
            filtered_data = []
            for record in self.sample_data:
                record_date = record["fecha"].date()
                if record_date == date_obj.date():
                    if placa_filter is None or placa_filter in record["placa"]:
                        filtered_data.append(record)
            
            if not filtered_data:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("No hay datos para exportar"),
                    bgcolor=ft.Colors.ORANGE
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            # Crear un directorio temporal para guardar el archivo
            temp_dir = tempfile.gettempdir()
            file_name = f"reporte_pesajes_{date_str.replace('/', '_')}.csv"
            file_path = os.path.join(temp_dir, file_name)
            
            # Escribir datos al archivo CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['ID', 'Placa', 'Peso', 'Proceso', 'Fecha', 'Estable']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for record in filtered_data:
                    writer.writerow({
                        'ID': record['id'],
                        'Placa': record['placa'],
                        'Peso': record['peso'],
                        'Proceso': record['proceso'],
                        'Fecha': record['fecha'].strftime("%d/%m/%Y %H:%M"),
                        'Estable': 'Sí' if record['estable'] else 'No'
                    })
            
            # Mostrar mensaje de éxito
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Archivo exportado: {file_path}"),
                bgcolor=ft.Colors.GREEN
            )
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as e:
            print(f"Error al exportar a CSV: {e}")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error al exportar: {str(e)}"),
                bgcolor=ft.Colors.RED
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def show(self):
        """Mostrar diálogo de reportes"""
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()
    
    def close_dialog(self, e=None):
        """Cerrar diálogo"""
        self.dialog.open = False
        self.page.update()