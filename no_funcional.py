import sys
import pygame
print(sys.executable)
import numpy as np
from pygame.math import Vector3
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap

#import pygame_ce as pygame
#print(pygame.__file__)
import sys
print(sys.path)


print(sys.executable)
class Sketch:
    def __init__(self):
        self.lines = []  # Lista para almacenar las líneas del croquis
        self.visible = False  # Estado de visibilidad del croquis

    def add_line(self, start_point, end_point):
        self.lines.append((start_point, end_point))  # Agregar una nueva línea

    def finish_sketch(self):
        self.visible = True  # Hacer el croquis visible

    def draw(self, screen, camera_pos):
        if not self.visible:
            return  # No dibujar si el croquis no es visible

        for start_point, end_point in self.lines:
            # Ajustar las posiciones de los puntos según la posición de la cámara
            adjusted_start = (start_point.x * 100 + 400, -start_point.y * 100 + 300)
            adjusted_end = (end_point.x * 100 + 400, -end_point.y * 100 + 300)

            # Dibujar la línea en la pantalla
            pygame.draw.line(screen, (255, 255, 255), adjusted_start, adjusted_end, 2)  # Color blanco y grosor 2

    def extrude(self, height):
        if not self.visible:
            raise ValueError("El croquis no es visible. Asegúrate de hacer clic en 'finish sketch'.")

        if not self.lines:
            raise ValueError("No hay líneas para extruir.")

        # Crear un perfil 2D a partir de las líneas
        profile = self.create_profile_from_lines()

        # Extruir el perfil
        extruded_shape = self.perform_extrusion(profile, height)
        return extruded_shape

    def create_profile_from_lines(self):
        # Crear un conjunto de puntos a partir de las líneas
        points = []
        for start_point, end_point in self.lines:
            points.append((start_point.x, start_point.y))  # Asumiendo que start_point y end_point son objetos Vector3
            points.append((end_point.x, end_point.y))

        # Eliminar duplicados y crear un perfil cerrado
        unique_points = list(set(points))
        profile = np.array(unique_points)

        # Asegurarse de que el perfil esté cerrado (opcional)
        if not np.array_equal(profile[0], profile[-1]):
            profile = np.vstack([profile, profile[0]])  # Cerrar el perfil

        return profile

    def perform_extrusion(self, profile, height):
        # Crear una lista para almacenar los vértices de la extrusión
        extruded_shape = []

        # Extruir el perfil hacia arriba
        for point in profile:
            # Añadir el punto original (base)
            extruded_shape.append((point[0], point[1], 0))  # Base
            # Añadir el punto extruido (altura)
            extruded_shape.append((point[0], point[1], height))  # Altura

        return extruded_shape


class Renderer(QWidget):
    def __init__(self, parent=None):
        super(Renderer, self).__init__(parent)
        self.setMinimumSize(800, 600)
        self.objects = []  # Lista de objetos a dibujar
        self.drawing = False
        self.current_sketch = None  # Croquis actual
        self.start_point = None
        self.end_point = None
        self.screen = pygame.Surface((800, 600))
        self.clock = pygame.time.Clock()
        self.camera_pos = Vector3(0, 0, -5)
        self.label = QLabel(self)
        self.label.setGeometry(0, 0, 800, 600)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_render)
        self.timer.start(33)  # ~30 FPS

    def update_render(self):
        self.screen.fill((30, 30, 30))  # Limpiar la pantalla
        for obj in self.objects:
            obj.draw(self.screen, self.camera_pos)  # Dibujar objetos existentes

        # Dibujar la línea en proceso
        if self.drawing and self.start_point and self.end_point:
            pygame.draw.line(self.screen, (255, 255, 255),
                             (self.start_point.x * 100 + 400, -self.start_point.y * 100 + 300),
                             (self.end_point.x * 100 + 400, -self.end_point.y * 100 + 300), 2)

        pygame_image = pygame.image.tostring(self.screen, "RGB")
        qt_image = QImage(pygame_image, 800, 600, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(qt_image))

    def start_drawing(self):
        self.drawing = True
        self.current_sketch = Sketch()  # Crear un nuevo croquis
        self.start_point = None
        self.end_point = None

    def stop_drawing(self):
        self.drawing = False
        if self.current_sketch:
            self.current_sketch.finish_sketch()  # Finalizar el croquis
            self.objects.append(self.current_sketch)  # Agregar el croquis a la lista de objetos
        self.current_sketch = None  # Reiniciar el croquis actual

    def add_line_to_sketch(self, start_point, end_point):
        if self.current_sketch:
            self.current_sketch.add_line(start_point, end_point)

    def mousePressEvent(self, event):
        if self.drawing:
            self.start_point = Vector3((event.x() - 400) / 100, (300 - event.y()) / 100, 0)
            self.end_point = self.start_point  # Inicializar el punto final

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.end_point = Vector3((event.x() - 400) / 100, (300 - event.y()) / 100, 0)

    def mouseReleaseEvent(self, event):
        if self.drawing:
            self.end_point = Vector3((event.x() - 400) / 100, (300 - event.y()) / 100, 0)
            # Agregar la línea al croquis actual
            self.add_line_to_sketch(self.start_point, self.end_point)
            # Actualizar el punto de inicio para la próxima línea
            self.start_point = self.end_point  # El nuevo inicio es el final de la línea actual
            self.update_render()  # Actualizar la pantalla

    def finish_sketch(self):
        """Finaliza el croquis actual y lo agrega a la lista de objetos."""
        if self.current_sketch:
            self.current_sketch.finish_sketch()  # Asegurarse de que el croquis sea visible
            self.objects.append(self.current_sketch)  # Agregar el croquis a la lista de objetos
            self.current_sketch = None  # Reiniciar el croquis actual
            self.stop_drawing()  # Detener el modo de dibujo

    def add_object(self, obj):
        """Agregar un objeto a la lista de objetos."""
        self.objects.append(obj)


class ExtrudedShape:
    def __init__(self, vertices):
        self.vertices = vertices
        self.edges = self.create_edges()
        self.faces = self.create_faces()

    def create_edges(self):
        edges = []
        num_points = len(self.vertices) // 2
        for i in range(num_points):
            edges.append((i, (i + 1) % num_points))  # Base
            edges.append((i + num_points, (i + 1) % num_points + num_points))  # Top
            edges.append((i, i + num_points))  # Conectar base y parte superior
        return edges

    def create_faces(self):
        num_points = len(self.vertices) // 2
        faces = []
        for i in range(num_points):
            # Cara lateral
            faces.append((i, (i + 1) % num_points, (i + 1) % num_points + num_points, i + num_points))
            # Cara base
            faces.append(tuple(range(num_points)))
            # Cara superior
            faces.append(tuple(range(num_points, 2 * num_points)))
        return faces

    def draw(self, screen, camera_pos):
        for face in self.faces:
            # Calcular los puntos de la cara
            points = [self.vertices[i] - camera_pos for i in face]
            # Dibujar la cara
            pygame.draw.polygon(screen, (0, 255, 255, 128),  # Color cian con transparencia
                               [(400 + point[0] * 100, 300 - point[1] * 100) for point in points])
        for edge in self.edges:
            start = self.vertices[edge[0]] - camera_pos
            end = self.vertices[edge[1]] - camera_pos
            pygame.draw.line(screen, (0, 255, 255),  # Color cian para los bordes
                             (400 + start[0] * 100, 300 - start[1] * 100),
                             (400 + end[0] * 100, 300 - end[1] * 100), 2)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("2D CAD Application")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        self.renderer = Renderer()
        main_layout.addWidget(self.renderer, 1)

        button_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)

        draw_button = QPushButton("Start Drawing")
        extrude_button = QPushButton("Extrude")
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Enter extrusion height")

        draw_button.clicked.connect(self.renderer.start_drawing)
        extrude_button.clicked.connect(self.extrude_sketch)

        button_layout.addWidget(draw_button)
        button_layout.addWidget(QLabel("Extrusion Height:"))
        button_layout.addWidget(self.height_input)
        button_layout.addWidget(extrude_button)

        # Agregar un botón para finalizar el croquis
        finish_button = QPushButton("Finish Sketch")
        finish_button.clicked.connect(self.renderer.finish_sketch)
        button_layout.addWidget(finish_button)

    def extrude_sketch(self):
        height_text = self.height_input.text()
        if height_text:
            try:
                height = float(height_text)
                if self.renderer.objects:
                    sketch = self.renderer.objects[-1]  # Obtener el último croquis
                    extruded_vertices = sketch.extrude(height)
                    extruded_shape = ExtrudedShape(extruded_vertices)
                    self.renderer.add_object(extruded_shape)  # Agregar el objeto extruido al renderer
            except ValueError:
                print("Por favor, ingresa una altura válida.")  # Manejo de errores para entrada no válida

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
