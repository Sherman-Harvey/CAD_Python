# sketch.py
"""
Maneja toda la lógica relacionada con el dibujo 2D
"""
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

class Sketch:
    def __init__(self):
        self.points = []
        self.lines = []
        self.is_drawing = False
        self.snap_distance = 0.1
        self.current_line_start = None
        self.current_line_end = None  # Para el preview de la línea actual


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
        self.current_line_end = snap_point  # Inicializar el punto final

    def update_current_line(self, point):
        """
        Actualiza la posición final de la línea mientras se está dibujando
        """
        if self.is_drawing:
            self.current_line_end = point

    def end_line(self, point):
        if self.is_drawing:
            snap_point = self.add_point(point)
            # Solo añadir la línea si los puntos son diferentes
            if self.current_line_start != snap_point:
                self.lines.append((self.current_line_start, snap_point))
            self.is_drawing = False
            self.current_line_start = None
            self.current_line_end = None

    def draw(self):

        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)

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

        # Dibujar línea en progreso
        if self.is_drawing and self.current_line_start and self.current_line_end:
            glLineWidth(1.0)  # Línea más delgada para el preview
            glBegin(GL_LINES)
            glColor3f(1, 1, 1)  # Blanco para la línea en progreso
            glVertex3f(*self.current_line_start, 0)
            glVertex3f(*self.current_line_end, 0)
            glEnd()

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)


    def get_geometry(self):
        """
        Retorna la geometría actual del sketch para operaciones 3D
        """
        return {
            'points': self.points,
            'lines': self.lines
        }

    def clear(self):
        """
        Limpia el sketch actual
        """
        self.points = []
        self.lines = []
        self.is_drawing = False
        self.current_line_start = None
        self.current_line_end = None