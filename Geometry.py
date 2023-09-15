import trimesh
import math
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans


class GeometryImport:

    def __init__(self, filepath) -> None:
        """
        Initializes an GeometryImport object.

        Parameters
        __________
            filepath : str
                The path of the stl file stored on the computer.
        """
        self.filename = filepath

    def get_points(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        When the filepath as a string is passed on as an input to the class object, this function imports the .stl file,
        samples 100,000 points onto the surface using sample_surface_even of trimesh package, extracts x,y,z
        coordinates of the imported file and shifts all the points in the geometry such that its center moves to (0,0,0).

        Parameters
        __________
        None

        Returns
        _______
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
        the mean value from the x,y,z array. The resulting arrays are x,y,z arrays adjusted to have its center at (0,0,0).

        Parameters
        __________
            x: ndarray
             x-coordinates array of the imported geometry.
            y: ndarray
             y-coordinates array of the imported geometry.
            z: ndarray
             z-coordinates array of the imported geometry.

        Returns
        _______
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

    def layer_part(self) -> np.ndarray:
        """
        This fuinction layers the imported geometry in the z direction specified by a layer height, projects the x,y points
        of neighboring region of +/- 0.5mm on current z_layer height onto the current z-plane and then applied the
        KMeans clustering machine learning algorithm of the scikit-learn library to get a specified numer of points
        in the current z plane.

        Parameters
        __________
        None

        Returns
        _______
            common_array: ndarray
                A ndarray consisting of the x,y,z coordinates of the layered part.
        """
        x, y, z = self.get_points()
        x_s, y_s, z_s = [], [], []
        height_each_layer = 5
        number_of_layers = (max(z) - min(z)) / height_each_layer

        z_int = np.linspace(min(z), max(z), math.ceil(number_of_layers))
        global_selected_points = []
        for z_lay in z_int:
            x_r, y_r, z_r = [], [], []
            for i in range(len(x)):
                if z[i] - 0.5 < z_lay < z[i] + 0.5:
                    x_r.append(x[i])
                    y_r.append(y[i])
                    z_r.append(z_lay)
            data = np.vstack((x_r, y_r)).T
            num_resampled_points = 50
            kmeans = KMeans(n_clusters=num_resampled_points, random_state=0, n_init='auto', algorithm='lloyd')
            kmeans.fit(data)
            resampled = kmeans.cluster_centers_

            x_resampled, y_resampled = resampled[:, 0], resampled[:, 1]
            z_resampled = np.full((num_resampled_points, 1), z_lay)
            selected_points2 = np.column_stack((x_resampled, y_resampled, z_resampled))
            global_selected_points.extend(selected_points2)

            x_s.append(x_resampled)
            y_s.append(y_resampled)
            z_s.append(np.asarray(z_lay))
        common_array = np.asarray(global_selected_points)

        return common_array

    def points_visualization(self) -> None:
        """
        This function of the GeometryImport class extracts the ndarray of the layered part by calling the function
        layer_part and plots a 3 dimensional plot of the imported geometry using matplotlib library.

        Returns
        _______
        None
        """
        common_array = self.layer_part()
        fig = plt.figure(figsize=(16, 9))
        # ax = fig.add_subplot(projection='3d')
        ax1 = plt.axes(projection='3d')
        ax1.scatter(common_array[:, 0], common_array[:, 1], common_array[:, 2], marker='o', c='r')
        plt.show()
