import numpy as np
import trimesh
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
from shapely.geometry import Polygon, MultiPoint
from shapely.wkb import loads
import pygeos


class GeometryImport:

    def __init__(self, filepath) -> None:
        self.filename = filepath

    def get_points(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:

        mesh = trimesh.load_mesh(self.filename)
        number_sampling_points = 200000
        pointcloud, _ = trimesh.sample.sample_surface(mesh, number_sampling_points)

        x = np.asarray(pointcloud[:, 0])
        y = np.asarray(pointcloud[:, 1])
        z = np.asarray(pointcloud[:, 2])

        x_shifted, y_shifted, z_shifted = self.shift_center(x, y, z)
        return x_shifted, y_shifted, z_shifted

    @staticmethod
    def shift_center(x, y, z) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
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

    def points_visualization(self) -> None:
        common_array = self.generate_sequential_contour_points()
        fig = plt.figure(figsize=(16, 9))
        ax1 = plt.axes(projection='3d')
        ax1.plot(common_array[:, 0], common_array[:, 1], common_array[:, 2], marker='o', c='r')
        ax1.set_xlim(-70, 70)
        ax1.set_ylim(-70, 70)
        ax1.set_zlim(-70, 70)
        plt.show()

    def alpha_shape(self, points: np.ndarray, alpha: float) -> Polygon:
        """
        Computes the alpha shape (concave hull) of a set of points.

        :param points: np.ndarray, array containing the x and y coordinates of points.
        :param alpha: float, alpha value to determine the alpha shape.
        :return: Polygon, the computed alpha shape as a Shapely Polygon object.
        """
        if len(points) < 4:
            return MultiPoint(list(points)).convex_hull
        tri = Delaunay(points)
        triangles = points[tri.simplices]
        a = ((triangles[:, 0, 0] - triangles[:, 1, 0]) ** 2 + (triangles[:, 0, 1] - triangles[:, 1, 1]) ** 2) ** 0.5
        b = ((triangles[:, 1, 0] - triangles[:, 2, 0]) ** 2 + (triangles[:, 1, 1] - triangles[:, 2, 1]) ** 2) ** 0.5
        c = ((triangles[:, 2, 0] - triangles[:, 0, 0]) ** 2 + (triangles[:, 2, 1] - triangles[:, 0, 1]) ** 2) ** 0.5
        s = (a + b + c) / 2.0
        areas = (s * (s - a) * (s - b) * (s - c)) ** 0.5
        circum_r = a * b * c / (4.0 * areas)
        filter = circum_r < 1.0 / alpha
        triangles = triangles[filter]
        if len(triangles) == 0:
            return MultiPoint(list(points)).convex_hull
        polygons = [pygeos.polygons(triangle) for triangle in triangles]

        # Using pygeos for union operation
        result = pygeos.union_all(polygons)

        # Convert the result back to a Shapely geometry
        result = loads(pygeos.to_wkb(result))

        return result

        return result

    def generate_sequential_contour_points(self, alpha_value=0.5, layer_height=1.0) -> np.ndarray:
        x, y, z = self.get_points()
        points = np.column_stack((x, y, z))

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
                contour_points = np.column_stack((x, y, np.full_like(x, z_layer)))
                all_contour_points.append(contour_points)
            elif concave_hull.geom_type == 'MultiPolygon':
                for polygon in concave_hull:
                    x, y = polygon.exterior.xy
                    contour_points = np.column_stack((x, y, np.full_like(x, z_layer)))
                    all_contour_points.append(contour_points)

        common_array = np.vstack(all_contour_points)
        return common_array

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

        ax.set_xlim(-120, 120)
        ax.set_ylim(-120, 120)
        ax.set_zlim(-120, 120)

        ax.grid(False)
        # Show the plot
        plt.show()
