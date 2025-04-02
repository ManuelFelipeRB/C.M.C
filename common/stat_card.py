import flet as ft

class StatCard:
    def __init__(self, page, icon, title, color, on_click_handler):
        self.page = page
        self.icon = icon
        self.title = title
        self.color = color
        self.on_click_handler = on_click_handler
        self.is_active = False
        self.is_hovered = False
        self.card = self.create_card()
        
    def create_card(self):
        return ft.Card(
            content=ft.Container(
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text("", size=30, weight=ft.FontWeight.BOLD, color=self.color),
                                ft.Text(self.title, size=15, color="#424242"),
                            ],
                            spacing=5,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Icon(self.icon, size=40, color=self.color),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    expand=True,
                ),
                padding=ft.padding.only(left=20, right=20, bottom=5, top=5),
                border_radius=10,
                on_hover=self.on_hover,
                on_click=self.on_click,
                opacity=1,
                animate_opacity=100,
            ),
            elevation=4,
        )
    
    def update_value(self, value):
        self.card.content.content.controls[0].controls[0].value = str(value)
        self.page.update()
        
    def set_active(self, is_active):
        self.is_active = is_active
        if is_active:
            self.card.border = ft.border.all(3, ft.Colors.BLUE)
            self.apply_color_inversion()
        else:
            self.card.border = None
            self.restore_original_colors()
        self.page.update()
    
    def on_hover(self, e):
        self.is_hovered = e.data == "true"
        
        if self.is_hovered:
            self.card.content.opacity = 0.5
        else:
            self.card.content.opacity = 1
            
        self.page.update()
    
    def on_click(self, e):
        self.on_click_handler(e)
           
    def apply_color_inversion(self):
        container = self.card.content
        row = container.content
        
        container.bgcolor = self.color
        
        column = row.controls[0]
        value_text = column.controls[0]
        title_text = column.controls[1]
        icon = row.controls[1]
        
        value_text.color = ft.Colors.WHITE
        title_text.color = ft.Colors.WHITE
        icon.color = ft.Colors.WHITE
        
        self.page.update()
    
    def restore_original_colors(self):
        container = self.card.content
        row = container.content
        
        container.bgcolor = "#edffff"
        
        column = row.controls[0]
        value_text = column.controls[0]
        title_text = column.controls[1]
        icon = row.controls[1]
        
        value_text.color = self.color
        title_text.color = "#424242"
        icon.color = self.color
        
        self.page.update()
    
    def get_card(self):
        return self.card