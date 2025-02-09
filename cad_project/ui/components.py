#ui/components
import pygame

class UIComponent:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        #self.active = False
        self.visible = True

    def draw(self, surface):
        pass

    def handle_event(self, event):
        return False

class Button(UIComponent):
    def __init__(self, x, y, width, height, text, callback):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font(None, 32)
        self.colors = {
            'normal': (100, 100, 100),
            'hover': (150, 150, 150),
            'text': (255, 255, 255)
        }
        self.state = 'normal'  # Inicializar el estado
        self.submenu = None


    def draw(self, surface):
        if not self.visible:
            return

        # Dibujar el fondo del botón
        color = self.colors[self.state]
        pygame.draw.rect(surface, color, self.rect)

        # Dibujar el texto
        text_surface = self.font.render(self.text, True, self.colors['text'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_hovered(self, pos):
        return self.rect.collidepoint(pos)

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.state = 'hover' if self.rect.collidepoint(event.pos) else 'normal'

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.callback()
                return True
        return False

class InputBox(UIComponent):
    def __init__(self, x, y, width, height, text=''):
        super().__init__(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, 24)

        self.colors = {
            'inactive': (100, 100, 100),
            'active': (150, 150, 150),
            'text': (255, 255, 255)
        }
        self.active = False

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            return self.active

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            return True
        return False

    def draw(self, surface):
        if not self.visible:
            return

        color = self.colors['active'] if self.active else self.colors['inactive']
        pygame.draw.rect(surface, color, self.rect)

        text_surface = self.font.render(self.text, True, self.colors['text'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)