import flet as ft
from datetime import datetime
from DatabaseConnections import DatabaseManager
from SerialComunications import SerialPortManager

class WeightTrackingApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Weight Tracking System"
        self.page.window_width = 600
        self.page.window_height = 600

        # Initialize managers
        self.db_manager = DatabaseManager()
        self.serial_manager = SerialPortManager()

        # Create UI components
        self.setup_ui()

    def setup_ui(self):
        # Port selection
        self.port_dropdown = ft.Dropdown(
            label="Select Port",
            options=[ft.dropdown.Option(port) for port in self.serial_manager.get_available_ports()],
            on_change=self.update_port_selection
        )

        # Connection buttons
        self.connect_button = ft.ElevatedButton("Connect", on_click=self.connect_serial)
        self.disconnect_button = ft.ElevatedButton("Disconnect", on_click=self.disconnect_serial, disabled=True)

        # Weight display
        self.weight_display = ft.Text("0.00 kg", size=24)

        # Input fields
        self.plate_input = ft.TextField(label="Vehicle Plate")
        self.tare_input = ft.TextField(label="Tare Weight")
        
        # Dropdowns
        self.process_dropdown = ft.Dropdown(
            label="Process Type",
            options=[
                ft.dropdown.Option("Initial Weighing"),
                ft.dropdown.Option("Final Weighing")
            ]
        )

        self.axes_dropdown = ft.Dropdown(
            label="Number of Axes",
            options=[
                ft.dropdown.Option("2"),
                ft.dropdown.Option("3"),
                ft.dropdown.Option("4")
            ]
        )

        # Buttons
        self.capture_button = ft.ElevatedButton("Capture Weight", on_click=self.capture_weight)
        self.save_button = ft.ElevatedButton("Save Event", on_click=self.save_weight_event)

        # Events table
        self.events_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Date")),
                ft.DataColumn(ft.Text("Plate")),
                ft.DataColumn(ft.Text("Initial Weight")),
                ft.DataColumn(ft.Text("Final Weight")),
                ft.DataColumn(ft.Text("Net Weight"))
            ],
            rows=[]
        )

        # Layout
        self.page.add(
            ft.Row([
                self.port_dropdown,
                self.connect_button,
                self.disconnect_button
            ]),
            ft.Text("Current Weight:", size=20),
            self.weight_display,
            ft.Row([
                self.plate_input,
                self.tare_input
            ]),
            ft.Row([
                self.process_dropdown,
                self.axes_dropdown
            ]),
            ft.Row([
                self.capture_button,
                self.save_button
            ]),
            ft.Text("Recent Events:", size=20),
            self.events_table
        )

        # Set serial data callback
        self.serial_manager.set_data_callback(self.update_weight_display)

    def update_port_selection(self, e):
        self.serial_manager.port = e.control.value

    def connect_serial(self, e):
        if self.port_dropdown.value:
            success = self.serial_manager.connect(self.port_dropdown.value)
            if success:
                self.connect_button.disabled = True
                self.disconnect_button.disabled = False
                self.page.update()

    def disconnect_serial(self, e):
        self.serial_manager.disconnect()
        self.connect_button.disabled = False
        self.disconnect_button.disabled = True
        self.page.update()

    def update_weight_display(self, weight):
        try:
            # Remove any non-numeric characters and convert to float
            numeric_weight = float(''.join(filter(str.isdigit, weight)))
            # Format with 2 decimal places and add 'kg'
            formatted_weight = f"{numeric_weight:.2f} kg"
            self.weight_display.value = formatted_weight
            self.page.update()
        except ValueError:
            print(f"Could not parse weight: {weight}")

    def capture_weight(self, e):
        captured_weight = self.weight_display.value
        self.tare_input.value = captured_weight
        self.page.update()

    def save_weight_event(self, e):
        try:
            # Remove 'kg' and any whitespace, then convert to float
            current_weight = float(self.weight_display.value.replace('kg', '').strip())
            tare_weight = float(self.tare_input.value.replace('kg', '').strip() or '0')

            event_data = {
                'date': datetime.now().strftime("%Y-%m-%d"),
                'time': datetime.now().strftime("%H:%M:%S"),
                'plate': self.plate_input.value,
                'axes': self.axes_dropdown.value,
                'initial_weight': str(current_weight),
                'final_weight': '0',  # Implement final weighing logic
                'tare': str(tare_weight),
                'net_weight': str(current_weight - tare_weight)
            }

            rows_affected = self.db_manager.add_weight_event(**event_data)
            
            if rows_affected:
                self.refresh_events_table()
                self.clear_inputs()
        except ValueError as ve:
            # Add error handling to show user a message
            print(f"Error parsing weight: {ve}")
            # Optionally, you can add a dialog or toast message
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error parsing weight: {ve}"),
                bgcolor=ft.colors.RED
            )
            self.page.snack_bar.open = True
            self.page.update()

    def refresh_events_table(self):
        events = self.db_manager.get_weight_events()
        rows = [
            ft.DataRow([
                ft.DataCell(ft.Text(str(event[1]))),  # Date
                ft.DataCell(ft.Text(str(event[3]))),  # Plate
                ft.DataCell(ft.Text(str(event[4]))),  # Initial Weight
                ft.DataCell(ft.Text(str(event[5]))),  # Final Weight
                ft.DataCell(ft.Text(str(event[7])))   # Net Weight
            ]) for event in events[:10]  # Limit to last 10 events
        ]
        self.events_table.rows = rows
        self.page.update()

    def clear_inputs(self):
        self.plate_input.value = ""
        self.tare_input.value = ""
        self.process_dropdown.value = None
        self.axes_dropdown.value = None
        self.page.update()

def main(page: ft.Page):
    app = WeightTrackingApp(page)

ft.app(target=main)