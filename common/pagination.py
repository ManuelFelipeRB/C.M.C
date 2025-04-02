import flet as ft

class PaginationManager:
    def __init__(self, page, items_per_page=20):
        self.page = page
        self.items_per_page = items_per_page
        self.current_page = 1
        self.data = []
        self.on_page_change_callback = None
        
        # Componentes UI
        self.page_text = ft.Text("Página 0 de 0", size=11)
        self.prev_button = ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            on_click=self.go_previous,
            disabled=True
        )
        self.next_button = ft.IconButton(
            icon=ft.Icons.ARROW_FORWARD,
            on_click=self.go_next,
            disabled=True
        )
        
    def get_controls(self):
        return ft.Row(
            [self.prev_button, self.page_text, self.next_button],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    
    def set_page_change_callback(self, callback):
        self.on_page_change_callback = callback
        
    def update_data(self, new_data):
        self.data = new_data
        self.current_page = 1
        self.update_ui()
        if self.on_page_change_callback:
            self.on_page_change_callback()
        
    def go_previous(self, e):
        if self.current_page > 1:
            self.current_page -= 1
            self.update_ui()
            if self.on_page_change_callback:
                self.on_page_change_callback()

    def go_next(self, e):
        total_pages = self.get_total_pages()
        if self.current_page < total_pages:
            self.current_page += 1
            self.update_ui()
            if self.on_page_change_callback:
                self.on_page_change_callback()
            
    def get_total_pages(self):
        return max(1, (len(self.data) + self.items_per_page - 1) // self.items_per_page)
    
    def get_current_page_data(self):
        start = (self.current_page - 1) * self.items_per_page
        end = start + self.items_per_page
        return self.data[start:end]
    
    def update_ui(self):
        total_pages = self.get_total_pages()
        self.page_text.value = f"Página {self.current_page} de {total_pages}"
        self.prev_button.disabled = self.current_page <= 1
        self.next_button.disabled = self.current_page >= total_pages
        self.page.update()