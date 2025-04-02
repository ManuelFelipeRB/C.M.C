import flet as ft
from flet import Colors, Icons
import plotly.graph_objs as go
import plotly.io as pio
import pandas as pd
import numpy as np

def main(page: ft.Page):
    page.title = "Modern Dashboard"
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=Colors.BLUE_700,
            secondary=Colors.PURPLE_700,
            tertiary=Colors.ORANGE_700,
        ),
    )
    page.fonts = {
        "Roboto": "https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap"
    }
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.expand = True

    # Updated StatsCard component
    class StatsCard(ft.Container):
        def __init__(self, title, value, icon, color):
            super().__init__(
                width=300,
                height=120,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=[color, Colors.with_opacity(color=color, opacity=0.7)],
                ),
                border_radius=15,
                animate=ft.animation.Animation(300, "easeInOut"),
                padding=20,
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(icon, size=30, color=Colors.WHITE),
                                ft.Text(title, color=Colors.WHITE, weight=ft.FontWeight.BOLD),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Text(value, color=Colors.WHITE, size=24, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=10
                ),
                shadow=ft.BoxShadow(
                    spread_radius=2,
                    blur_radius=10,
                    color=Colors.with_opacity(color=Colors.BLACK, opacity=0.3),
                    offset=ft.Offset(2, 2)
                )
            )
            self.on_hover = self.hover_effect

        def hover_effect(self, e):
            self.scale = 1.02 if e.data == "true" else 1
            self.update()

    # Create Plotly Charts
    def create_sales_chart():
        # Sample sales data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        sales = [12000, 19000, 15000, 22000, 18000, 25000]
        
        # Create bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=months, 
                y=sales, 
                marker_color='rgba(58, 71, 80, 0.6)',
                marker_line_color='rgba(58, 71, 80, 1.0)',
                marker_line_width=1.5
            )
        ])
        
        fig.update_layout(
            title='Monthly Sales Performance',
            xaxis_title='Month',
            yaxis_title='Sales ($)',
            template='plotly_white'
        )
        
        return pio.to_html(fig, full_html=False)

    def create_revenue_breakdown_chart():
        # Sample revenue breakdown
        labels = ['Product A', 'Product B', 'Product C', 'Product D']
        values = [30, 25, 20, 25]
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=labels, 
            values=values, 
            hole=.3,
            marker=dict(colors=['#636EFA', '#EF553B', '#00CC96', '#AB63FA'])
        )])
        
        fig.update_layout(
            title='Revenue Breakdown by Product',
            template='plotly_white'
        )
        
        return pio.to_html(fig, full_html=False)

    # Updated sidebar
    sidebar = ft.Container(
        width=250,
        bgcolor=Colors.BLUE_700,
        padding=ft.padding.only(top=40, left=20, right=20),
        content=ft.Column(
            controls=[
                ft.Text("Dashboard Pro", color=Colors.WHITE, size=24),
                ft.Divider(color=Colors.WHITE54),
                ft.ListTile(
                    title=ft.Text("Inicio", color=Colors.WHITE),
                    leading=ft.Icon(Icons.HOME, color=Colors.WHITE),
                ),
                ft.ListTile(
                    title=ft.Text("Analíticas", color=Colors.WHITE),
                    leading=ft.Icon(Icons.ANALYTICS, color=Colors.WHITE),
                ),
                ft.ListTile(
                    title=ft.Text("Usuarios", color=Colors.WHITE),
                    leading=ft.Icon(Icons.PEOPLE, color=Colors.WHITE),
                ),
            ],
            spacing=20
        )
    )

    # Main content header
    header = ft.Container(
        height=60,
        padding=ft.padding.symmetric(horizontal=30),
        content=ft.Row(
            controls=[
                ft.Text("Resumen General", size=20, weight=ft.FontWeight.BOLD),
                ft.Row(
                    controls=[
                        ft.IconButton(icon=Icons.NOTIFICATIONS, icon_color=Colors.GREY_600),
                        ft.IconButton(icon=Icons.ACCOUNT_CIRCLE, icon_color=Colors.GREY_600),
                    ]
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
    )

    # Stats grid
    stats_grid = ft.ResponsiveRow(
        controls=[
            ft.Container(width=4, content=StatsCard("Ventas", "$24.5k", Icons.ATTACH_MONEY, Colors.BLUE_700)),
            ft.Container(width=4, content=StatsCard("Usuarios", "1.2k", Icons.PEOPLE, Colors.PURPLE_700)),
            ft.Container(width=4, content=StatsCard("Rendimiento", "89%", Icons.SPEED, Colors.ORANGE_700)),
        ],
        spacing=20,
        run_spacing=20,
    )

    # Charts section
    charts_section = ft.ResponsiveRow(
        controls=[
            ft.Container(
                width=6,
                content=ft.Column(
                    controls=[
                        ft.Text("Ventas Mensuales", size=16, weight=ft.FontWeight.BOLD),
                        ft.Markdown(create_sales_chart(), extension_set="gitHub")
                    ]
                ),
                padding=20
            ),
            ft.Container(
                width=6,
                content=ft.Column(
                    controls=[
                        ft.Text("Distribución de Ingresos", size=16, weight=ft.FontWeight.BOLD),
                        ft.Markdown(create_revenue_breakdown_chart(), extension_set="gitHub")
                    ]
                ),
                padding=20
            )
        ],
        spacing=20,
        run_spacing=20,
    )

    # Final layout
    main_content = ft.Container(
        expand=True,
        padding=30,
        content=ft.Column(
            controls=[
                header,
                stats_grid,
                charts_section
            ],
            spacing=30
        )
    )

    page.add(
        ft.Row(
            controls=[sidebar, main_content],
            spacing=0,
            expand=True
        )
    )

ft.app(target=main)