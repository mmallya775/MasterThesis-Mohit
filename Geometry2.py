import numpy as np
import trimesh
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay, distance
from shapely.geometry import Polygon, MultiPoint
from shapely.ops import unary_union
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans
import math


class GeometryImport:

    def __init__(self, filepath) -> None:
        """
        Initializes an GeometryImport object.

        Parameters:
        filepath (str): The path of the stl file stored on the computer.
        """
        self.filename = filepath

    def get_points(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Imports the .stl file, samples points onto the surface using trimesh, extracts x,y,z
        coordinates of the imported file and shifts all the points in the geometry such that its center is at (0,0,0).

        Returns:
        tuple: A tuple containing three ndarrays representing the x, y, z coordinates of the points, respectively.
        """
        mesh = trimesh.load_mesh(self.filename)
        number_sampling_points = 140000
        pointcloud, _ = trimesh.sample.sample_surface_even(mesh, number_sampling_points)

        x = np.asarray(pointcloud[:, 0])
        y = np.asarray(pointcloud[:, 1])
        z = np.asarray(pointcloud[:, 2])

        x_shifted, y_shifted, z_shifted = self.shift_center(x, y, z)
        return x_shifted, y_shifted, z_shifted

    @staticmethod
    def shift_center(x, y, z) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Shifts the center of a set of 3D points to the origin.

        Parameters:
        x, y, z (ndarray): Arrays representing the x, y, z coordinates.

        Returns:
        tuple: A tuple containing three ndarrays representing the shifted x, y, z coordinates of the points, respectively.
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
        Layers the imported geometry in the z direction specified by a layer height.

        Returns:
        ndarray: A ndarray consisting of the x, y, z coordinates of the layered part.
        """
        x, y, z = self.get_points()
        height_each_layer = 1
        number_of_layers = (max(z) - min(z)) / height_each_layer
        z_int = np.linspace(min(z), max(z), math.floor(number_of_layers))
        global_selected_points = []

        for z_lay in z_int:
            x_r, y_r, z_r = [], [], []
            for i in range(len(x)):
                if z[i] - 0.18 < z_lay < z[i] + 0.18:
                    x_r.append(x[i])
                    y_r.append(y[i])
                    z_r.append(z_lay)

            data = np.vstack((x_r, y_r)).T
            num_resampled_points = 55
            kmeans = KMeans(n_clusters=num_resampled_points, random_state=0, n_init='auto', algorithm='elkan')
            kmeans.fit(data)
            resampled = kmeans.cluster_centers_

            x_resampled, y_resampled = resampled[:, 0], resampled[:, 1]
            x_arranged, y_arranged = self.sequence_points(x_resampled, y_resampled)
            z_resampled = np.full((len(x_arranged), 1), z_lay)
            selected_points = np.column_stack((x_arranged, y_arranged, z_resampled))
            global_selected_points.extend(selected_points)

        layered_array = np.asarray(global_selected_points)
        return layered_array

    def points_visualization(self) -> None:
        """
        Visualizes the layered points in a 3D plot.

        Returns:
        None
        """
        common_array = self.generate_sequential_contour_points()
        fig = plt.figure(figsize=(16, 9))
        ax1 = plt.axes(projection='3d')
        ax1.plot(common_array[:, 0], common_array[:, 1], common_array[:, 2], marker='o', c='r')
        ax1.set_xlim(-70, 70)
        ax1.set_ylim(-70, 70)
        ax1.set_zlim(-70, 70)
        plt.show()

    def alpha_shape(self, points, alpha):
        """
        Generates an alpha shape (concave hull) of a given set of points.

        Parameters:
        points (ndarray): The 2D array of points on which to generate the alpha shape.
        alpha (float): A parameter to control the concavity of the alpha shape.

        Returns:
        object: A Shapely geometry object representing the alpha shape (could be a Polygon or MultiPolygon).
        """
        if len(points) < 4:
            return MultiPoint(list(points)).convex_hull
        tri = Delaunay(points)
        triangles = points[tri.simplices]
        a = ((triangles[:, 0, 0] - triangles[:, 1, 0]) ** 2 + (triangles[:, 0, 1] - triangles[:, 1, 1]) ** 2) ** 0.5
        b = ((triangles[:, 1, 0] - triangles[:, 2, 0]) ** 2 + (triangles[:, 1, 1] - triangles[:, 2, 1]) ** 2) ** 0.5
        c = ((triangles[:, 2, 0] - triangles[:, 0, 0]) ** 2 + (triangles[:, 2, 1] - triangles[:, 0, 1]) ** 2) ** 0.5
        s = (a + b + c) / 2.0
        areas = (s*(s-a)*(s-b)*(s-c)) ** 0.5
        circum_r = a * b * c / (4.0 * areas)
        filter = circum_r < 1.0 / alpha
        triangles = triangles[filter]
        if len(triangles) == 0:
            return MultiPoint(list(points)).convex_hull
        polygons = [Polygon(triangle) for triangle in triangles]
        result = unary_union(polygons)
        return result

    def generate_sequential_contour_points(self, alpha_value=0.5, layer_height=1.0) -> np.ndarray:
        """
        Generates the sequential contour points of the geometry.

        Parameters:
        alpha_value (float): The alpha value for the alpha shape function to generate concave hulls.
        layer_height (float): The height of each layer in the z direction.

        Returns:
        ndarray: An array containing the sequential contour points.
        """
        x, y, z = self.get_points()  # Get points from the get_points method
        points = np.column_stack((x, y, z))  # Combine x, y, z to form points array

        z_min = np.min(points[:, 2])
        z_max = np.max(points[:, 2])
        all_contour_points = []

        for z in np.arange(z_min, z_max, layer_height):
            layer = points[(points[:, 2] >= z) & (points[:, 2] < z + layer_height)]
            if len(layer) == 0:
                continue
            concave_hull = self.alpha_shape(layer[:, :2], alpha=alpha_value)
            if concave_hull.is_empty:
                continue
            z_layer = z + layer_height / 2.0
            if concave_hull.geom_type == 'Polygon':
                x, y = concave_hull.exterior.xy
                x_seq, y_seq = self.sequence_points(x, y)
                layer_points = np.column_stack((x_seq, y_seq, np.full_like(x_seq, z_layer)))
                all_contour_points.append(layer_points)
            elif concave_hull.geom_type == 'MultiPolygon':
                for polygon in concave_hull.geoms:
                    x, y = polygon.exterior.xy
                    x_seq, y_seq = self.sequence_points(x, y)
                    layer_points = np.column_stack((x_seq, y_seq, np.full_like(x_seq, z_layer)))
                    all_contour_points.append(layer_points)

        all_contour_points_array = np.vstack(all_contour_points)

        df = pd.DataFrame(data=all_contour_points_array)
        df.to_excel("layerdata.xlsx")
        return all_contour_points_array

    @staticmethod
    def sequence_points(x, y) -> tuple[np.ndarray, np.ndarray]:
        """
        Sequences a given set of points from the first point in quadrant 1.

        Parameters:
        x, y (ndarray): Arrays representing the x, y coordinates of points.

        Returns:
        tuple: A tuple containing two ndarrays representing the sequenced x, y coordinates of the points, respectively.
        """
        x = np.array(x)
        y = np.array(y)
        coordinates = np.vstack((x, y)).T
        first = coordinates[(coordinates[:, 0] > 0) & (coordinates[:, 1] > 0)]
        if len(first) > 0:
            nearest_coordinate = first[np.argmin(np.abs(first[:, 1]))]
        start_point = nearest_coordinate
        current_point = start_point
        connected_points = [start_point]
        remaining_points = list(coordinates)

        while len(remaining_points) > 0:
            distances = [distance.euclidean(current_point, point) for point in remaining_points]
            nearest_index = np.argmin(distances)
            nearest_point = remaining_points[nearest_index]
            remaining_points.pop(nearest_index)
            connected_points.append(nearest_point)
            current_point = nearest_point
        connected_points = np.array(connected_points)
        x_arranged = connected_points[:, 0]
        y_arranged = connected_points[:, 1]

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

        ax.set_xlim(-70, 70)
        ax.set_ylim(-70, 70)
        ax.set_zlim(-70, 70)

        ax.grid(False)
        # Show the plot
        plt.show()