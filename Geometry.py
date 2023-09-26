"""
A python library to that uses trimesh library to import a stl part, samples a set number of points on the surface
of the part and carries out operations so that a sequential set of points according to the path planning strategy
are generated which can be used to develop RAPID codes for ABB robots.
"""

import math

import matplotlib.pyplot as plt
import numpy as np
import trimesh
from scipy.spatial import distance
from sklearn.cluster import KMeans


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
        pointcloud, _ = trimesh.sample.sample_surface(mesh, number_sampling_points)

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

    def layer_part(self) -> np.ndarray:
        """
        This function layers the imported geometry in the z direction specified by a layer height, projects the x,y
        points of neighboring region of +/- 0.2mm on current z_layer height onto the current z-plane and then applies
        the ConvexHull algorithm of the SciPy library to get a outer contour of the current layer. The coordinates of
        the outer contour along with the current layer height can sequenced and then sent to the RAPID Code generator.

        Parameters
        ----------

        Returns
        -------
            layered_array: ndarray
                A ndarray consisting of the x,y,z coordinates of the layered part.
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
            # data = np.vstack((x_r, y_r)).T
            # hull = ConvexHull(data)
            # resampled = data[hull.vertices]
            # x_resampled, y_resampled = resampled[:, 0], resampled[:, 1]
            # z_resampled = np.ones(resampled.shape[0]) * z_lay
            x_resampled, y_resampled = resampled[:, 0], resampled[:, 1]

            x_arranged, y_arranged = self.sequence_points(x_resampled, y_resampled)
            z_resampled = np.full((len(x_arranged), 1), z_lay)
            selected_points = np.column_stack((x_arranged, y_arranged, z_resampled))
            global_selected_points.extend(selected_points)

        layered_array = np.asarray(global_selected_points)

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
        # df = pd.DataFrame(data=common_array)
        # df.to_excel("points_data.xlsx")

        fig = plt.figure(figsize=(16, 9))
        ax1 = plt.axes(projection='3d')
        ax1.plot(common_array[:, 0], common_array[:, 1], common_array[:, 2], marker='o', c='r')
        ax1.set_xlim(-70, 70)
        ax1.set_ylim(-70, 70)
        ax1.set_zlim(-70, 70)

        plt.show()


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

    @staticmethod
    def conf_T_ROB1(coordinates) -> np.ndarray:
        """
        A function to determine the robot axes positions for robot 1 based on the total available workspace on the
        workpiece blank. For the robot ABB IRB IRB 4600-60kg / 2,05m M2004 four values of axis values are used to
        specify a configuration. These axes are:
        - cf1 : the quadrant number for axis 1.
        - cf4 : the quadrant number for axis 4.
        - cf6 : the quadrant number for axis 6.
        - cfx : one of the eight possible robot configurations numbered from 0 through 7.

        For more details refer to RAPID Instructions manual.

        Parameters
        ----------
        coordinates : np.ndarray
            A ndarray consisting of columns of x, y and z coordinates of the robot path.

        Returns
        -------
        confdata : np.ndarray
            A ndarray consisting of the configuration data for T_ROB1.
        """

        y = coordinates[:, 1]

        confdata = []
        cf1, cf4, cf6, cfx = [], [], [], []

        for y_c in y:

            if y_c >= 0:
                cf1.append(0)
                cf4.append(-1)
                cf6.append(0)
                cfx.append(0)

            else:
                cf1.append(-1)
                cf4.append(0)
                cf6.append(-1)
                cfx.append(0)

            confdata = np.column_stack((cf1, cf4, cf6, cfx))

        print(confdata)

        return confdata

    @staticmethod
    def rot_T_ROB1(coordinates):
        """
        Determines rotation array for the end effector
        :param coordinates:
        :return:
        """

        leng = len(coordinates[:, 0])

        q1 = np.full((leng, 1), 0)
        q2 = np.full((leng, 1), 0)
        q3 = np.full((leng, 1), 1)
        q4 = np.full((leng, 1), 0)
        q = np.column_stack((q1, q2, q3, q4))

        print(q)

    @staticmethod
    def sequence_points(x, y) -> tuple[np.ndarray, np.ndarray]:
        """
        This function is used to sequence a given set of points from the first point in the quadrant 1 of the current
        set of points whose coordinates are shifted to have origin at the center of the pointcloud.

        Parameters
        ----------
        x: ndarray
            An array consisting of the x-coordinates of the current layer.
        y: ndarray
            An array consisting of the y-coordinates of the current layer.

        Returns
        -------
        A tuple containing a ndarray of x and y coordinates.
        """
        x = np.array(x)
        y = np.array(y)
        coordinates = np.vstack((x, y)).T
        first = coordinates[(coordinates[:, 0] > 0) & (coordinates[:, 1] > 0)]

        if len(first) > 0:
            # Find the coordinate in the first quadrant closest to y=0
            nearest_coordinate = first[np.argmin(np.abs(first[:, 1]))]

        start_point = nearest_coordinate

        current_point = start_point
        connected_points = [start_point]  # Include the start point at the beginning
        remaining_points = list(coordinates)  # Keep all points in the remaining_points list

        while len(remaining_points) > 0:  # At least 2 points are needed for the loop
            distances = [distance.euclidean(current_point, point) for point in remaining_points]
            nearest_index = np.argmin(distances)
            nearest_point = remaining_points[nearest_index]
            remaining_points.pop(nearest_index)
            connected_points.append(nearest_point)
            current_point = nearest_point

        # Convert the connected points to a NumPy array
        connected_points = np.array(connected_points)

        # Create a scatter plot of the points
        x_arranged = connected_points[:, 0]
        y_arranged = connected_points[:, 1]

        return x_arranged, y_arranged
