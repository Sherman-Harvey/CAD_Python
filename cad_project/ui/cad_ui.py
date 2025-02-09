# ui/cad_ui.py
from .components import Button, InputBox
from .menus import UIManager, Submenu

class CADUserInterface:
    def __init__(self, cad_system, display_size):
        self.cad_system = cad_system
        self.ui_manager = UIManager(display_size[0], display_size[1])
        self.setup_extrude_menu()

    def setup_extrude_menu(self):
        # Crear botón de extrusión
        self.extrude_button = Button(10, 10, 100, 30, "Extrude", self.toggle_extrude_menu)
        self.ui_manager.add_component(self.extrude_button)

        # Crear submenu de extrusión
        self.extrude_submenu = Submenu(10, 50, 200, 100)
        self.extrude_input = InputBox(20, 70, 180, 30, "")
        self.extrude_submenu.add_component(self.extrude_input)

        self.extrude_confirm = Button(20, 110, 180, 30, "Confirm", self.perform_extrusion)
        self.extrude_submenu.add_component(self.extrude_confirm)

    def toggle_extrude_menu(self):
        if self.extrude_submenu.visible:
            self.extrude_submenu.visible = False
            self.ui_manager.active_submenu = None
        else:
            self.extrude_submenu.visible = True
            self.ui_manager.active_submenu = self.extrude_submenu

    def perform_extrusion(self):
        try:
            extrude_value = float(self.extrude_input.text)
            self.cad_system.perform_extrusion(extrude_value)
        except ValueError:
            print("Invalid input")

    def handle_event(self, event):
        return self.ui_manager.handle_event(event)

    def draw(self, screen):
        self.ui_manager.draw(screen)