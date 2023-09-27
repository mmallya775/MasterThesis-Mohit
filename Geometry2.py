"""
This code has the solution to problem of outer contour of Geometry class.

!!!! Create a separate class which incorporates these changes and developes a more accurate answer

"""


import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial import Delaunay, distance  # for euclidean distance calculation
from shapely.geometry import Polygon, MultiPoint
from shapely.ops import unary_union
import pandas as pd


def sequence_points(x, y):
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


def alpha_shape(points, alpha):
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


filename = 'FromRP.STL'  # Replace with your STL file name
mesh = trimesh.load_mesh(filename)

points, _ = trimesh.sample.sample_surface_even(mesh, 100000)

z_min = np.min(points[:, 2])
z_max = np.max(points[:, 2])
layer_height = 1.0
alpha_value = 0.5

all_contour_points = []

fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')

cmap = plt.get_cmap('viridis')
layer_count = int((z_max - z_min) / layer_height)
colors = [cmap(i / layer_count) for i in range(layer_count)]

for i, z in enumerate(np.arange(z_min, z_max, layer_height)):
    layer = points[(points[:, 2] >= z) & (points[:, 2] < z + layer_height)]
    if len(layer) == 0:
        continue
    concave_hull = alpha_shape(layer[:, :2], alpha=alpha_value)
    if concave_hull.is_empty:
        continue
    z_layer = z + layer_height / 2.0
    if concave_hull.geom_type == 'Polygon':
        x, y = concave_hull.exterior.xy
        x_seq, y_seq = sequence_points(x, y)
        layer_points = np.column_stack((x_seq, y_seq, np.full_like(x_seq, z_layer)))
        all_contour_points.append(layer_points)
        ax.plot(x_seq, y_seq, zs=z_layer, color=colors[i % layer_count])
    elif concave_hull.geom_type == 'MultiPolygon':
        for polygon in concave_hull.geoms:
            x, y = polygon.exterior.xy
            x_seq, y_seq = sequence_points(x, y)
            layer_points = np.column_stack((x_seq, y_seq, np.full_like(x_seq, z_layer)))
            all_contour_points.append(layer_points)
            ax.plot(x_seq, y_seq, zs=z_layer, color=colors[i % layer_count])

all_contour_points_array = np.vstack(all_contour_points)

# Find unique rows and count how many duplicates were removed
original_count = len(all_contour_points_array)
all_contour_points_array = np.unique(all_contour_points_array, axis=0)
unique_count = len(all_contour_points_array)
duplicates_removed = original_count - unique_count

# Print results
np.set_printoptions(threshold=np.inf)
print(all_contour_points_array)
print(f'Number of duplicate rows removed: {duplicates_removed}')

# np.set_printoptions(threshold=np.inf)
# print(all_contour_points_array)
df = pd.DataFrame(all_contour_points_array)
df.to_excel("layerwise data.xlsx")

ax.set_xlim([0, 175])
ax.set_ylim([0, 175])
ax.set_zlim([0, 175])

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.title('3D Visualization of Sequenced Outer Contours of Layers')
plt.show()
