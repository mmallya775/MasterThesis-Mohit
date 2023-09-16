"""
Developing a GUI for interacting with the user to get a filename and generate ABB robot paths for double sided
incrementally fomring (DSIF) of a composite sheet.
"""

import sys
import os

os.environ["QT_API"] = "pyqt5"
from qtpy import QtWidgets
import pyvista as pv
from pyvistaqt import QtInteractor, MainWindow


class MyMainWindow(MainWindow):

    def __init__(self, parent=None, show=True):
        QtWidgets.QMainWindow.__init__(self, parent)

        # Set the initial window size (width, height)
        self.resize(1000, 800)

        # create the frame for the 3D plot
        self.plot_frame = QtWidgets.QFrame(self)
        self.plot_frame.setFixedSize(800, 600)  # Set the fixed size of the 3D plot
        vlayout = QtWidgets.QVBoxLayout(self.plot_frame)

        # Add the pyvista interactor object
        self.plotter = QtInteractor(self.plot_frame)
        vlayout.addWidget(self.plotter.interactor)
        self.signal_close.connect(self.plotter.close)

        # Create a button to add the surface
        self.add_surface_button = QtWidgets.QPushButton('Add Surface', self.plot_frame)  # Add button to plot_frame
        self.add_surface_button.clicked.connect(self.add_surface)
        vlayout.addWidget(self.add_surface_button)

        # Set the layout of the main window
        self.setCentralWidget(self.plot_frame)

        if show:
            self.show()

    def add_surface(self):
        """ Add a surface from an STL file to the pyqt frame """
        file_dialog = QtWidgets.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Open STL File', '', 'STL Files (*.stl)')
        if file_path:
            surface = pv.read(file_path)
            self.plotter.add_mesh(surface, color='grey')  # Set the mesh color to grey
            self.plotter.renderer.background_color = [0.7, 0.7, 1.0]  # R, G, B
            self.plotter.add_axes(line_width=3, shaft_length=0.8, cone_radius=0.3, ambient=0.5, tip_length=0.4,
                                  label_size=(0.6, 0.2))

            # self.plotter.add_axes(axis_labels_size=2.0)  # Double the size
            self.plotter.reset_camera()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyMainWindow()
    sys.exit(app.exec_())
