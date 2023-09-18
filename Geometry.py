"""
A python library to that uses trimesh library to import a stl part, samples a set number of points on the surface
of the part and carries out operations so that a sequential set of points according to the path planning strategy
are generated which can be used to develop RAPID codes for ABB robots.
"""

import trimesh
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from scipy.spatial import ConvexHull


class GeometryImport:

    def __init__(self, filepath) -> None:
        """
        Initializes an GeometryImport object.

        Parameters
        ----------
            filepath : str
                The path of the stl file stored on the computer.
        """
        self.filename = filepath

    def get_points(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        When the filepath as a string is passed on as an input to the class object, this function imports the .stl file,
        samples 100,000 points onto the surface using sample_surface_even of trimesh package, extracts x,y,z
        coordinates of the imported file and shifts all the points in the geometry such that its center moves to (0,0,0)
        .

        Parameters
        ----------


        Returns
        -------
                x : ndarray
                 x coordinates of all the points of the imported part.
                y : ndarray
                 y coordinates of all the points of the imported part.
                z : ndarray
                 z coordinates of all the points of the imported part.
        """
        mesh = trimesh.load_mesh(self.filename)

        number_sampling_points = 100000
        pointcloud, _ = trimesh.sample.sample_surface_even(mesh, number_sampling_points)

        x = np.asarray(pointcloud[:, 0])
        y = np.asarray(pointcloud[:, 1])
        z = np.asarray(pointcloud[:, 2])

        x_shifted, y_shifted, z_shifted = self.shift_center(x, y, z)
        return x_shifted, y_shifted, z_shifted

    @staticmethod
    def shift_center(x, y, z) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        This function of the GeometryImport class calculates the mean of the array of x,y,z coordinates and subtracts
        the mean value from the x,y,z array. The resulting arrays are x,y,z arrays adjusted to have its center at
        (0,0,0).

        Parameters
        ----------
            x: ndarray
             x-coordinates array of the imported geometry.
            y: ndarray
             y-coordinates array of the imported geometry.
            z: ndarray
             z-coordinates array of the imported geometry.

        Returns
        -------
            x: ndarray
             x-coordinates array shifted to origin.
            y: ndarray
             y-coordinates array shifted to origin.
            z: ndarray
             z-coordinates array shifted to origin.

        """

        x = np.array(x)
        y = np.array(y)
        z = np.array(z)

        mid_x = (max(x) + min(x)) / 2
        mid_y = (max(y) + min(y)) / 2
        mid_z = (max(z) + min(z)) / 2

        x = x - mid_x
        y = y - mid_y
        z = z - mid_z

        return x, y, z

    def layer_part(self, method='Convex-Hull') -> np.ndarray:
        """
        This function layers the imported geometry in the z direction specified by a layer height, projects the x,y
        points of neighboring region of +/- 0.5mm on current z_layer height onto the current z-plane and then applied
        the KMeans clustering machine learning algorithm of the scikit-learn library to get a specified numer of points
        in the current z plane.

        Parameters
        ----------

        Returns
        -------
            layered_array: ndarray
                A ndarray consisting of the x,y,z coordinates of the layered part.
        """
        if method == 'KMeans':
            x, y, z = self.get_points()
            height_each_layer = 1
            number_of_layers = (max(z) - min(z)) / height_each_layer

            z_int = np.linspace(min(z), max(z), math.ceil(number_of_layers))
            global_selected_points = []
            for z_lay in z_int:
                x_r, y_r, z_r = [], [], []
                for i in range(len(x)):
                    if z[i] - 0.001 < z_lay < z[i] + 0.001:
                        x_r.append(x[i])
                        y_r.append(y[i])
                        z_r.append(z_lay)
                data = np.vstack((x_r, y_r)).T
                num_resampled_points = 40
                kmeans = KMeans(n_clusters=num_resampled_points, random_state=0, n_init='auto', algorithm='lloyd')
                kmeans.fit(data)
                resampled = kmeans.cluster_centers_

                x_resampled, y_resampled = resampled[:, 0], resampled[:, 1]
                z_resampled = np.full((num_resampled_points, 1), z_lay)
                x_arranged, y_arranged = self.sequence_points(x_resampled, y_resampled)
                selected_points = np.column_stack((x_arranged, y_arranged, z_resampled))
                global_selected_points.extend(selected_points)

            layered_array = np.asarray(global_selected_points)

            return layered_array
        else:
            x, y, z = self.get_points()
            height_each_layer = 1
            number_of_layers = (max(z) - min(z)) / height_each_layer

            z_int = np.linspace(min(z), max(z), math.ceil(number_of_layers))
            global_selected_points = []
            for z_lay in z_int:
                x_r, y_r, z_r = [], [], []
                for i in range(len(x)):
                    if z[i] - 0.2 < z_lay < z[i] + 0.2:
                        x_r.append(x[i])
                        y_r.append(y[i])
                        z_r.append(z_lay)
                data = np.vstack((x_r, y_r)).T
                hull = ConvexHull(data)
                resampled = data[hull.vertices]
                x_resampled, y_resampled = resampled[:, 0], resampled[:, 1]
                z_resampled = np.ones(resampled.shape[0]) * z_lay

                x_arranged, y_arranged = self.sequence_points(x_resampled, y_resampled)
                selected_points = np.column_stack((x_arranged, y_arranged, z_resampled))
                global_selected_points.extend(selected_points)

            layered_array = np.asarray(global_selected_points)

            df = pd.DataFrame(layered_array, columns=['X', 'Y', 'Z'])
            # df.to_excel("data.xlsx", index=False)

            return layered_array

    def points_visualization(self) -> None:
        """
        This function of the GeometryImport class extracts the ndarray of the layered part by calling the function
        layer_part and plots a 3 dimensional plot of the imported geometry using matplotlib library.

        Parameters
        ----------

        Returns
        -------
        """
        common_array = self.layer_part()
        fig = plt.figure(figsize=(16, 9))
        ax1 = plt.axes(projection='3d')
        ax1.scatter(common_array[:, 0], common_array[:, 1], common_array[:, 2], marker='o', c='r')
        plt.show()

    @staticmethod
    def sequence_points(x, y) -> tuple[np.ndarray, np.ndarray]:
        """
        This static function takes in the set of points x,y for the current layer in layer_part method and then returns
        two arrays x_arranged and y_arranged of these points re-arranged to trace the outer contour of the part by
        dividing them into 4 quadrants of the graph and arranging the according to their specific strategy. For moving
        from first quadrant to the fourth quadrant, we have used the following strategy:
            - In the first quadrant, the x value is constantly decreasing and the y value is constantly increasing.
            - In the second quadrant, the x value as well as the y value is constantly decreasing.
            - In the third quadrant, the x value is constantly increasing and the y value is constantly decreasing.
            - In the fourth quadrant, the x value as well as the y value is constantly increasing.
        Each quadrant array is sorted according to the above strategy and all the four quadrant arrays are then split
        into separate x_arranged and y_arranged arrays which are returned as ndarray.

        Parameters
        ----------
        x: ndarray
            An array consisting of the x-coordinates of the current layer.
        y: ndarray
            An array consisting of the y-coordinates of the current layer.

        Returns
        -------
        x_arranged: ndarray
            An array consisting of x-coordinates arranged in sequential order.
        y_arranged: ndarray
            An array consisting of y-coordinates arranged in sequential order
        """

        points = np.column_stack((x, y))

        quadrant1, quadrant2, quadrant3, quadrant4 = [], [], [], []

        for x_coor, y_coor in points:
            if x_coor >= 0 and y_coor >= 0:
                quadrant1.append((x_coor, y_coor))
            elif x_coor < 0 <= y_coor:
                quadrant2.append((x_coor, y_coor))
            elif x_coor < 0 and y_coor < 0:
                quadrant3.append((x_coor, y_coor))
            else:
                quadrant4.append((x_coor, y_coor))

        quadrant1, quadrant2, quadrant3, quadrant4 = (np.array(quadrant1), np.array(quadrant2), np.array(quadrant3),
                                                      np.array(quadrant4))

        sorted_quadrant1 = quadrant1[np.lexsort((quadrant1[:, 1], -quadrant1[:, 0]))]
        sorted_quadrant2 = quadrant2[np.lexsort((-quadrant2[:, 1], -quadrant2[:, 0]))]
        sorted_quadrant3 = quadrant3[np.lexsort((-quadrant3[:, 1], quadrant3[:, 0]))]
        sorted_quadrant4 = quadrant4[np.lexsort((quadrant4[:, 1], quadrant4[:, 0]))]

        sequential_points = np.concatenate((sorted_quadrant1, sorted_quadrant2, sorted_quadrant3, sorted_quadrant4))
        x_arranged = sequential_points[:, 0]
        y_arranged = sequential_points[:, 1]

        return x_arranged, y_arranged

    @staticmethod
    def plot_contours(data) -> None:

        """
        Plot outer contours with changing colors for each unique z value along with a color bar.

        Parameters
        ----------
        data : numpy.ndarray
        An ndarray of shape (n, 3) where each row represents (x, y, z) coordinates.

        Returns
        -------
        None
        """

        # Extract x, y, and z columns
        x = data[:, 0]
        y = data[:, 1]
        z = data[:, 2]

        # Create a figure and 3D axis
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Get unique z values and assign a color to each
        unique_z = np.unique(z)
        colors = plt.cm.viridis(np.linspace(0, 1, len(unique_z)))

        # Plot the lines with changing colors
        for i, z_val in enumerate(unique_z):
            mask = (z == z_val)
            x_level = x[mask]
            y_level = y[mask]
            z_level = z[mask]

            # Connect the last and first points to form a closed contour
            x_level = np.append(x_level, x_level[0])
            y_level = np.append(y_level, y_level[0])
            z_level = np.append(z_level, z_level[0])

            ax.plot(x_level, y_level, z_level, color=colors[i])

        # Add labels and legend
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        ax.grid(False)
        # Show the plot
        plt.show()
