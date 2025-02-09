# cad_system.py
import pygame
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from sketch import Sketch
from ui.cad_ui import CADUserInterface
import math
import numpy as np


class CADSystem:
    def __init__(self, display_size=(1600, 1000)):
        # Inicialización de pygame y OpenGL
        pygame.init()
        self.display = display_size
        # Create both OpenGL and standard surfaces
        pygame.display.set_mode(display_size, pygame.OPENGL | pygame.DOUBLEBUF)
        self.ui_surface = pygame.Surface(display_size, pygame.SRCALPHA)

        #self.screen = pygame.display.set_mode(display_size, pygame.OPENGL | pygame.DOUBLEBUF)

        # Configuración de OpenGL
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)

        # Configuración de la cámara
        self.camera_pos = [0, 0, 5]
        self.camera_rot = [0, 0]
        self.move_speed = 0.1
        self.mouse_speed = 0.2
        self.sketch_zoom = 5.0
        self.sketch_zoom_speed = 0.3

        # Configuración inicial de OpenGL
        self.setup_opengl()

        # Estado del sistema
        self.sketch_mode = False
        self.current_sketch = Sketch()
        self.last_mouse_pos = (display_size[0] // 2, display_size[1] // 2)
        self.drawing = False  # Add flag for line drawing

        # Inicializar UI
        self.ui = CADUserInterface(self, display_size)

        # Variables de debug
        self.debug = True
        self.last_world_pos = None

        # Ajustar valores iniciales para mejor control de zoom
        self.sketch_zoom = 5.0  # Distancia inicial de la cámara en modo sketch
        self.sketch_zoom_speed = 0.5  # Velocidad del zoom
        self.min_zoom = 2.0  # Zoom mínimo (más cerca)
        self.max_zoom = 20.0  # Zoom máximo (más lejos)




    def setup_opengl(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        # Configurar luz
        glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1])

        # Configuración de la perspectiva
        self.setup_perspective()

    def setup_perspective(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.display[0] / self.display[1]), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)

    def screen_to_world(self, screen_x, screen_y):
        # Añadir print para debug
        print(f"Screen coordinates: {screen_x}, {screen_y}")
        viewport = glGetIntegerv(GL_VIEWPORT)
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)

        win_y = viewport[3] - screen_y

        try:
            near_point = gluUnProject(float(screen_x), float(win_y), 0.0,
                                modelview, projection, viewport)
            far_point = gluUnProject(float(screen_x), float(win_y), 1.0,
                                modelview, projection, viewport)

            ray_direction = np.array(far_point) - np.array(near_point)
            ray_direction = ray_direction / np.linalg.norm(ray_direction)

            # Calculate intersection with sketch plane (z = 0)
            if abs(ray_direction[2]) > 1e-6:  # Avoid division by zero
                t = -near_point[2] / ray_direction[2]
                intersection = np.array(near_point) + t * ray_direction
                return (float(intersection[0]), float(intersection[1]))
            return None

            """plane_distance = self.sketch_zoom
            t = -(near_point[2] - plane_distance) / ray_direction[2]
            intersection = np.array(near_point) + t * ray_direction
            return (float(intersection[0]), float(intersection[1]))"""

        except Exception as e:
            print(f"Error in screen_to_world: {e}")
            return None

    def handle_sketch_input(self, event):
        if not self.sketch_mode:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.ui.handle_event(event):  # Only draw if not interacting with UI
                world_pos = self.screen_to_world(*event.pos)
                if world_pos:
                    self.drawing = True
                    self.current_sketch.start_line(world_pos)
                    self.last_world_pos = world_pos

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.drawing:
                world_pos = self.screen_to_world(*event.pos)
                if world_pos and self.last_world_pos:
                    self.current_sketch.end_line(world_pos)
                self.drawing = False
                self.last_world_pos = None

        elif event.type == pygame.MOUSEMOTION and self.drawing:
            world_pos = self.screen_to_world(*event.pos)
            if world_pos:
                self.current_sketch.update_current_line(world_pos)
        """if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            world_pos = self.screen_to_world(*pygame.mouse.get_pos())
            if world_pos:
                self.current_sketch.start_line(world_pos)
                self.last_world_pos = world_pos

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            world_pos = self.screen_to_world(*pygame.mouse.get_pos())

            if world_pos and self.last_world_pos:
                self.current_sketch.end_line(world_pos)
                self.last_world_pos = None"""

    def handle_keyboard(self):
        keys = pygame.key.get_pressed()

        if self.sketch_mode:
            # Manejar zoom en modo sketch
            if keys[pygame.K_w]:  # Acercar
                self.sketch_zoom = max(self.min_zoom, self.sketch_zoom - self.sketch_zoom_speed)
                self.update_sketch_camera()
            elif keys[pygame.K_s]:  # Alejar
                self.sketch_zoom = min(self.max_zoom, self.sketch_zoom + self.sketch_zoom_speed)
                self.update_sketch_camera()

            # También podemos usar las teclas + y - para zoom
            elif keys[pygame.K_PLUS] or keys[pygame.K_KP_PLUS]:  # Acercar
                self.sketch_zoom = max(self.min_zoom, self.sketch_zoom - self.sketch_zoom_speed)
                self.update_sketch_camera()
            elif keys[pygame.K_MINUS] or keys[pygame.K_KP_MINUS]:  # Alejar
                self.sketch_zoom = min(self.max_zoom, self.sketch_zoom + self.sketch_zoom_speed)
                self.update_sketch_camera()


        else:
            # Movimiento normal de cámara en modo 3D
            self.handle_camera_movement(keys)

    def handle_camera_movement(self, keys):
        yaw = math.radians(self.camera_rot[1])
        forward = [math.sin(yaw), 0, math.cos(yaw)]
        right = [math.cos(yaw), 0, -math.sin(yaw)]

        if keys[pygame.K_w]: self.move_camera(forward)
        if keys[pygame.K_s]: self.move_camera([-x for x in forward])
        if keys[pygame.K_a]: self.move_camera([-x for x in right])
        if keys[pygame.K_d]: self.move_camera(right)

    def move_camera(self, direction):
        self.camera_pos[0] += direction[0] * self.move_speed
        self.camera_pos[2] += direction[2] * self.move_speed

    def handle_mouse_motion(self):
        if not self.sketch_mode and pygame.mouse.get_focused():
            current_pos = pygame.mouse.get_pos()
            dx = current_pos[0] - self.last_mouse_pos[0]
            dy = current_pos[1] - self.last_mouse_pos[1]

            self.camera_rot[0] = (self.camera_rot[0] + dy * self.mouse_speed) % 360
            self.camera_rot[1] = (self.camera_rot[1] + dx * self.mouse_speed) % 360

            pygame.mouse.set_pos(self.last_mouse_pos)

    def draw_sketch_plane(self):
        glDisable(GL_LIGHTING)

         # Dibujar el plano base con transparencia
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        if self.sketch_mode:
            # En modo sketch, hacer el plano más sutil
            glColor4f(0.3, 0.3, 0.3, 0.1)
        else:
            # En modo normal, plano más visible
            glColor4f(0.2, 0.2, 0.2, 0.3)


        # Plano base

        glBegin(GL_QUADS)
        glColor4f(0.2, 0.2, 0.2, 0.3)
        size = 10
        glVertex3f(-size, -size, 0)
        glVertex3f(size, -size, 0)
        glVertex3f(size, size, 0)
        glVertex3f(-size, size, 0)
        glEnd()

        # Cuadrícula

        glLineWidth(1.0)
        glBegin(GL_LINES)

        if self.sketch_mode:
            glColor3f(0.4, 0.4, 0.4)  # Gris más claro para modo sketch
        else:
            glColor3f(0.3, 0.3, 0.3)  # Gris normal para modo 3D

        for i in range(-size, size + 1):
            # Vertical
            glVertex3f(float(i), float(-size), 0.01)
            glVertex3f(float(i), float(size), 0.01)
            # Horizontal
            glVertex3f(float(-size), float(i), 0.01)
            glVertex3f(float(size), float(i), 0.01)
        glEnd()

         # Ejes principales
        glLineWidth(2.0)
        glBegin(GL_LINES)

        # Eje X en rojo
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(-size, 0, 0.02)
        glVertex3f(size, 0, 0.02)
        # Eje Y en verde
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0, -size, 0.02)
        glVertex3f(0, size, 0.02)
        glEnd()

        glDisable(GL_BLEND)

        if not self.sketch_mode:
            glEnable(GL_LIGHTING)

    def reset_gl_state(self):
        glLoadIdentity()
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)

    def toggle_sketch_mode(self):
        self.sketch_mode = not self.sketch_mode
        if self.sketch_mode:
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
            self.update_sketch_camera()
        else:
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)
            pygame.mouse.set_pos(self.last_mouse_pos)


    def run(self):
        try:
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        elif event.key == pygame.K_TAB:
                            self.toggle_sketch_mode()

                    # Manejar zoom con rueda del mouse
                    elif event.type == pygame.MOUSEWHEEL:
                        self.handle_mouse_wheel(event)

                    # Manejar eventos UI en modo sketch
                    if self.sketch_mode:
                        if self.ui.handle_event(event):
                            continue
                        self.handle_sketch_input(event)

                self.handle_keyboard()
                self.handle_mouse_motion()

                # Renderizado
                self.render_scene()

                pygame.display.flip()
                pygame.time.wait(10)

        except Exception as e:
            print(f"Error in run: {e}")
            print("Cerrando aplicación...")
        finally:
            pygame.quit()

    def render_scene(self):
        # Limpiar el buffer con un color de fondo adecuado
        glClearColor(0.2, 0.2, 0.2, 1.0)  # Gris oscuro
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Update view
        glLoadIdentity()
        glRotatef(self.camera_rot[0], 1, 0, 0)
        glRotatef(self.camera_rot[1], 0, 1, 0)
        glTranslatef(-self.camera_pos[0], -self.camera_pos[1], -self.camera_pos[2])

        # Draw 3D elements
        self.draw_sketch_plane()
        self.current_sketch.draw()

        # Switch to 2D mode for UI
        if self.sketch_mode:
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            glOrtho(0, self.display[0], self.display[1], 0, -1, 1)
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()

            # Clear the UI surface
            self.ui_surface.fill((0, 0, 0, 0))
            # Dibujar el plano de sketch
            self.draw_sketch_plane()
            # Dibujar el sketch actual
            self.current_sketch.draw()

            # Draw UI to separate surface
            self.ui.draw(self.ui_surface)

            # Convert surface to texture and render
            self.render_ui_texture()

            # Restore 3D mode
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
            glPopMatrix()

    def render_ui_texture(self):
        # Disable 3D features
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)

        # Create texture from UI surface
        texture_data = pygame.image.tostring(self.ui_surface, "RGBA", True)
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.display[0], self.display[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)

        # Draw textured quad
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(0, 0)
        glTexCoord2f(1, 0); glVertex2f(self.display[0], 0)
        glTexCoord2f(1, 1); glVertex2f(self.display[0], self.display[1])
        glTexCoord2f(0, 1); glVertex2f(0, self.display[1])
        glEnd()

        # Cleanup
        glDeleteTextures([texture])
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)


    def perform_extrusion(self, height):

        """
        Método para realizar la extrusión del sketch actual
        """
        # Aquí irá la implementación de la extrusión
        print(f"Performing extrusion with height: {height}")
        self.current_sketch.extrude(height)

    def update_sketch_camera(self):
        # Actualizar la posición de la cámara manteniendo la vista frontal
        if self.sketch_mode:
            self.camera_pos[2] = self.sketch_zoom
            # Mantener la vista centrada
            self.camera_pos[0] = 0
            self.camera_pos[1] = 0
            self.camera_rot = [0, 0]

    def handle_mouse_wheel(self, event):
    # Maneja el zoom con la rueda del mouse

        if self.sketch_mode and event.type == pygame.MOUSEWHEEL:
            # Zoom con la rueda del mouse
            zoom_change = -event.y * self.sketch_zoom_speed  # Invertir dirección si es necesario
            self.sketch_zoom = max(self.min_zoom, min(self.max_zoom, self.sketch_zoom + zoom_change))
            self.update_sketch_camera()