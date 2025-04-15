import flet as ft

class App:
    def __init__(self):
        self.main_view()

    def main_view(self):
        ft.app(target=self.main)

    def main(self, page: ft.Page):
        self.page = page
        self.page.title = "Ventana Emergente con Overlay"
        
        # Crear el overlay para la ventana emergente
        self.overlay = ft.Container(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Mensaje Emergente", size=20, weight="bold"),
                    ft.Text("Este es un mensaje de prueba"),
                    ft.Row([
                        ft.TextButton("OK", on_click=self.close_overlay)
                    ], alignment=ft.MainAxisAlignment.END)
                ], tight=True),
                width=300,
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=15,
                    color=ft.Colors.BLACK45,
                )
            ),
            width=page.width,
            height=page.height,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
            alignment=ft.alignment.center,
        )
        
        # Botón para mostrar el overlay
        btn = ft.ElevatedButton("Mostrar Ventana", on_click=self.show_overlay)
        
        # Agregar el botón a la página
        self.page.add(btn)
        
        # Actualizar tamaño del overlay cuando cambie el tamaño de la página
        def page_resize(e):
            if self.overlay in self.page.overlay:
                self.overlay.width = self.page.width
                self.overlay.height = self.page.height
                self.page.update()
        
        self.page.on_resize = page_resize

    def show_overlay(self, e):
        print("Mostrando overlay...")
        # Añadir el overlay a la página
        self.page.overlay.append(self.overlay)
        self.page.update()

    def close_overlay(self, e):
        print("Cerrando overlay...")
        # Remover el overlay de la página
        self.page.overlay.remove(self.overlay)
        self.page.update()

# Iniciar la aplicación
if __name__ == "__main__":
    App()