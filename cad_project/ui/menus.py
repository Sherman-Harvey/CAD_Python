#ui/menus
import pygame
from .components import UIComponent, Button, InputBox
# Aquí van las clases Submenu y UIManager
class Submenu:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.components = []
        self.visible = False
        self.background_color = (80, 80, 80)

    def add_component(self, component):
        self.components.append(component)

    def draw(self, surface):
        if not self.visible:
            return

        pygame.draw.rect(surface, self.background_color, self.rect)
        for component in self.components:
            component.draw(surface)

    def handle_event(self, event):
        if not self.visible:
            return False

        for component in self.components:
            if component.handle_event(event):
                return True
        return False

class UIManager:
    def __init__(self, width, height):
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.components = []
        self.active_submenu = None

    def add_component(self, component):
        self.components.append(component)

    def draw(self, screen):
        self.surface.fill((0, 0, 0, 0))
        for component in self.components:
            component.draw(self.surface)
        if self.active_submenu:
            self.active_submenu.draw(self.surface)
        screen.blit(self.surface, (0, 0))

    def handle_event(self, event):
        if self.active_submenu and self.active_submenu.handle_event(event):
            return True
        for component in self.components:
            if component.handle_event(event):
                return True
        return False