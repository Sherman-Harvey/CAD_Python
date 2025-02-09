import pygame
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import numpy as np

class Sketch:
    def __init__(self):
        self.points = []
        self.lines = []
        self.is_drawing = False
        self.snap_distance = 0.1  # Distancia para snap a puntos existentes

    def add_point(self, point):
        # Intenta hacer snap a un punto existente
        for existing_point in self.points:
            if np.linalg.norm(np.array(existing_point) - np.array(point)) < self.snap_distance:
                return existing_point
        self.points.append(point)
        return point

    def start_line(self, point):
        self.is_drawing = True
        snap_point = self.add_point(point)
        self.current_line_start = snap_point

    def end_line(self, point):
        if self.is_drawing:
            self.is_drawing = False
            snap_point = self.add_point(point)
            self.lines.append((self.current_line_start, snap_point))

    def draw(self):


        # Dibujar puntos
        glPointSize(5.0)
        glBegin(GL_POINTS)
        glColor3f(1, 1, 0)  # Amarillo para los puntos
        for point in self.points:
            glVertex3f(*point, 0)
        glEnd()

        # Dibujar líneas
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glColor3f(0, 1, 0)  # Verde para las líneas
        for line in self.lines:
            glVertex3f(*line[0], 0)
            glVertex3f(*line[1], 0)
        glEnd()

class CADSystem:
    def __init__(self, display_size=(800, 600)):
        # Inicialización previa...
        pygame.init()
        self.display = display_size
        self.screen = pygame.display.set_mode(display_size, pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.display.set_mode(self.display, pygame.DOUBLEBUF | pygame.OPENGL)

        # Configuración de OpenGL
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)


        # Configuración de la cámara
        self.camera_pos = [0, 0, 5]
        self.camera_rot = [0, 0]
        self.move_speed = 0.1
        self.mouse_speed = 0.2

        # Configuración de OpenGL
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


        # Configuración inicial del mouse
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        self.last_mouse_pos = (display_size[0] // 2, display_size[1] // 2)
        pygame.mouse.set_pos(self.last_mouse_pos)

        # Modo de operación
        self.sketch_mode = False
        self.current_sketch = Sketch()

        # Variables de debug
        self.debug = True
        self.last_world_pos = None

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

            # Añadir prints para debug
            print(f"Near point: {near_point}")
            print(f"Far point: {far_point}")

            ray_direction = np.array(far_point) - np.array(near_point)
            ray_direction = ray_direction / np.linalg.norm(ray_direction)

        # Intersección con plano Z=0
            t = -near_point[2] / ray_direction[2]
            intersection = np.array(near_point) + t * ray_direction

        # Añadir print para debug
            print(f"Intersection point: {intersection}")

            return (float(intersection[0]), float(intersection[1]))
        except Exception as e:
            print(f"Error in screen_to_world: {e}")
            return None

    def handle_sketch_input(self, event):
        print(f"Event type: {event.type}, Sketch mode: {self.sketch_mode}")

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            world_pos = self.screen_to_world(*pygame.mouse.get_pos())
            if world_pos:
                if self.debug:
                    print(f"Starting line at: {world_pos}")
                self.current_sketch.start_line(world_pos)
                self.last_world_pos = world_pos

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            world_pos = self.screen_to_world(*pygame.mouse.get_pos())
            if world_pos and self.last_world_pos:
                if self.debug:
                    print(f"Ending line at: {world_pos}")
                self.current_sketch.end_line(world_pos)
                self.last_world_pos = None

    def handle_keyboard(self):

        keys = pygame.key.get_pressed()

        # Movimiento de cámara solo cuando no estamos en modo boceto
        if not self.sketch_mode:
            yaw = math.radians(self.camera_rot[1])
            forward = [math.sin(yaw), 0, math.cos(yaw)]
            right = [math.cos(yaw), 0, -math.sin(yaw)]

            if keys[pygame.K_w]:
                self.camera_pos[0] -= forward[0] * self.move_speed
                self.camera_pos[2] -= forward[2] * self.move_speed
            if keys[pygame.K_s]:
                self.camera_pos[0] += forward[0] * self.move_speed
                self.camera_pos[2] += forward[2] * self.move_speed
            if keys[pygame.K_a]:
                self.camera_pos[0] -= right[0] * self.move_speed
                self.camera_pos[2] -= right[2] * self.move_speed
            if keys[pygame.K_d]:
                self.camera_pos[0] += right[0] * self.move_speed
                self.camera_pos[2] += right[2] * self.move_speed

    def handle_mouse_motion(self):
        if not self.sketch_mode:  # Solo mover la cámara en modo normal
            if pygame.mouse.get_focused():
                current_pos = pygame.mouse.get_pos()
                dx = current_pos[0] - self.last_mouse_pos[0]
                dy = current_pos[1] - self.last_mouse_pos[1]

                self.camera_rot[0] += dy * self.mouse_speed
                self.camera_rot[1] += dx * self.mouse_speed

                 # Permitir rotación completa en X (arriba/abajo)
                if self.camera_rot[0] > 360:
                    self.camera_rot[0] -= 360
                elif self.camera_rot[0] < -360:
                    self.camera_rot[0] += 360

                # Mantener la rotación Y (izquierda/derecha) entre 0 y 360
                if self.camera_rot[1] > 360:
                    self.camera_rot[1] -= 360
                elif self.camera_rot[1] < 0:
                    self.camera_rot[1] += 360

                pygame.mouse.set_pos(self.last_mouse_pos)

    def draw_sketch_plane(self):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(-10, 10, -10, 10)  # Adjust coordinates as needed
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        try:


            glDisable(GL_LIGHTING)

            # Plano base
            glBegin(GL_QUADS)

            try:
                glColor4f(0.2, 0.2, 0.2, 0.3)
                size = 10
                glVertex3f(-size, -size, 0)
                glVertex3f(size, -size, 0)
                glVertex3f(size, size, 0)
                glVertex3f(-size, size, 0)
            finally:
                glEnd()


            # Cuadrícula
            glLineWidth(1.0)
            glBegin(GL_LINES)

            try:
                glColor3f(0.5, 0.5, 0.5)
                size = 10

            # Líneas verticales y horizontales
                for i in range(-size, size + 1):
                    # Vertical
                    glVertex3f(float(i), float(-size), 0.01)
                    glVertex3f(float(i), float(size), 0.01)

                    # Horizontal
                    glVertex3f(float(-size), float(i), 0.01)
                    glVertex3f(float(size), float(i), 0.01)
            finally:
                glEnd()

            # Ejes principales
            glLineWidth(2.0)
            glBegin(GL_LINES)
            try:
                # Eje X en rojo
                glColor3f(1.0, 0.0, 0.0)
                glVertex3f(-size, 0, 0.02)
                glVertex3f(size, 0, 0.02)
                # Eje Y en verde
                glColor3f(0.0, 1.0, 0.0)
                glVertex3f(0, -size, 0.02)
                glVertex3f(0, size, 0.02)
            finally:
                glEnd()

            glEnable(GL_LIGHTING)

        except Exception as e:
            print(f"Error in draw_sketch_plane: {e}")



        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def reset_gl_state(self):
                    """Resetea el estado de OpenGL a valores conocidos"""
                    glLoadIdentity()
                    glEnable(GL_DEPTH_TEST)
                    glEnable(GL_LIGHTING)
                    glEnable(GL_LIGHT0)
                    glEnable(GL_COLOR_MATERIAL)

                    # Asegurarse de que no hay operaciones pendientes
                    try:
                        glEnd()
                    except:
                        pass
    def run(self):

        try:
            #pygame.mouse.set_visible(True)
            # Hacemos visible el cursor para el bocetado

            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        elif event.key == pygame.K_TAB:
                            self.reset_gl_state()  # Resetear estado de OpenGL
                            glLoadIdentity()
                            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

                            self.sketch_mode = not self.sketch_mode
                            print(f"Sketch mode: {self.sketch_mode}")  # Debug
                            if self.sketch_mode:
                                # Configurar vista para bocetado
                                pygame.mouse.set_visible(True)
                                self.camera_pos = [0, 0, 5]
                                self.camera_rot = [0, 0]
                            else:
                                pygame.mouse.set_visible(False)
                                pygame.mouse.set_pos(self.last_mouse_pos)

                    # Manejar eventos de boceto independientemente del modo
                    if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
                        self.handle_sketch_input(event)


                self.handle_keyboard()
                self.handle_mouse_motion()  # Llamar siempre al manejo del mouse

                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

                # Actualizar vista
                glLoadIdentity()
                glRotatef(self.camera_rot[0], 1, 0, 0)
                glRotatef(self.camera_rot[1], 0, 1, 0)
                glTranslatef(-self.camera_pos[0], -self.camera_pos[1], -self.camera_pos[2])

                # Dibujar elementos
                self.draw_sketch_plane()
                self.current_sketch.draw()

                pygame.display.flip()
                pygame.time.wait(10)



        except Exception as e:
            print(f"Error in run: {e}")
        finally:
            pygame.quit()



if __name__ == "__main__":
    cad = CADSystem()
    cad.run()