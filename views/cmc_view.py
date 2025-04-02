import flet as ft

class CMCView:
    def __init__(self, page, color_principal, stat_cards, data_table, pagination, update_data_callback):
        self.page = page
        self.color_principal = color_principal
        self.stat_cards = stat_cards
        self.data_table = data_table
        self.pagination = pagination
        self.update_data_callback = update_data_callback
        self.view = self.create_view()
        
    def create_view(self):
        return ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [
                            self.stat_cards['total'].get_card(),
                            self.stat_cards['entrando'].get_card(),
                            self.stat_cards['proceso'].get_card(),
                            self.stat_cards['finalizado'].get_card(),
                            self.stat_cards['pendiente'].get_card()
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.only(left=30, right=30, bottom=0, top=0),
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text("Enturnados", size=20, weight=ft.FontWeight.BOLD, color=self.color_principal),
                                    ft.ElevatedButton(
                                        "Actualizar", 
                                        on_click=self.update_data_callback, 
                                        icon=ft.Icons.REFRESH
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Container(
                                content=ft.ListView(
                                    controls=[self.data_table],
                                    expand=True,
                                    auto_scroll=True
                                ),
                                padding=ft.padding.only(left=0, right=0, bottom=0, top=0),
                                bgcolor=ft.colors,
                                border_radius=10,
                                expand=True,
                                height=730,
                            ),
                            self.pagination.get_controls(),
                        ],
                        spacing=5,
                    ),
                    padding=ft.padding.only(left=35, right=35, bottom=5, top=5),
                    expand=True,
                ),
            ],
            expand=True,
            visible=True,
        )
    
    def get_view(self):
        return self.view