from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt, QPoint
from PIL import Image
import os
import numpy as np

class MapEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("D&D Map Editor")
        self.setGeometry(100, 100, 800, 600)  # Set initial window size

        # Create and set up the QLabel
        self.map_label = QLabel(self)
        self.map_label.setGeometry(0, 0, 800, 600)  # Set the label size

        # Initialize pixmap for performance
        self.pixmap_size = (200, 150)  # Smaller resolution
        self.scaled_pixmap_size = (800, 600)  # Display size
        self.original_pixmap = QPixmap(self.pixmap_size[0], self.pixmap_size[1])
        self.original_pixmap.fill(Qt.white)  # Start with a white background
        self.pixmap = self.original_pixmap.scaled(*self.scaled_pixmap_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.map_label.setPixmap(self.pixmap)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.map_label)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Initialize variables
        self.elevation_map = {}     # To store elevation data
        self.raise_mode = True      # Toggle between raising and lowering
        self.radius = 5             # Set radius



        # Generate a white image if it doesn't already exist
        image_path = 'map.png'
        if not os.path.exists(image_path):
            self.makeImage(700, 500, image_path)

        # Load the map image
        self.map_label = QLabel(self)
        self.original_pixmap = QPixmap(image_path)

        if self.original_pixmap.isNull():
            print("Failed to load the map image.")
            return
        
        self.pixmap = self.original_pixmap.copy()  # Create a copy for drawing
        self.map_label.setPixmap(self.pixmap)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.map_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Initialize variables
        self.elevation_map = {}     # To store elevation data
        self.raise_mode = True      # Toggle between raising and lowering
        self.radius = 1000             # Set radius

    def makeImage(self, width, height, nameString):
        # Create a new image with white background
        image = Image.new('RGB', (width, height), color='white')

        # Save the image to a file
        image.save(nameString)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Convert click coordinates to map coordinates
            label_pos = self.map_label.mapFromGlobal(event.globalPos())
            self.modify_terrain(label_pos, delta=1)
        elif event.button() == Qt.RightButton:
            # Convert click coordinates to map coordinates
            label_pos = self.map_label.mapFromGlobal(event.globalPos())
            self.modify_terrain(label_pos, delta=-1)


    def modify_terrain(self, position,delta):
        # Get click position relative to the map
        x = position.x()
        y = position.y()

        # Determine if we're raising or lowering the land
        delta2 = 1 if self.raise_mode else -1

        # Draw a circular brush
        brush_radius = self.radius
        for dx in range(-brush_radius, brush_radius + 1):
            for dy in range(-brush_radius, brush_radius + 1):
                rSquared = dx**2 + dy**2
                if rSquared <= brush_radius**2:  # Circle equation
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.pixmap.width() and 0 <= ny < self.pixmap.height():
                        key = (nx, ny)
                        if key in self.elevation_map:
                            self.elevation_map[key] += 10000*delta*np.exp(-np.sqrt(rSquared))
                        else:
                            self.elevation_map[key] = 10000*delta*np.exp(-np.sqrt(rSquared))

        # Update the display
        self.update_map()

    def update_map(self):
        # Reset pixmap to original before redrawing
        self.pixmap = self.original_pixmap.copy()
        
        painter = QPainter(self.pixmap)
        if not painter.isActive():
            print("Failed to activate QPainter.")
            return

        for (x, y), elevation in self.elevation_map.items():
            mu = 255 * np.tanh(elevation/10)
            # Ensure mu is within the valid range [0, 255]
            # Convert mu to integer
            mu = int(mu)
            nu = 255 - mu
            color = QColor(nu, 255, nu) if elevation > 0 else QColor(255+mu, 255+mu, 255)
            painter.setPen(color)
            painter.drawPoint(QPoint(x, y))

        painter.end()
        self.map_label.setPixmap(self.pixmap)

if __name__ == "__main__":
    app = QApplication([])
    editor = MapEditor()
    editor.show()
    app.exec_()
