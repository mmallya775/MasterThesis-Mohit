# import numpy as np
# import matplotlib.pyplot as plt

# Given coordinates
# coordinates = np.array([
#     [70.0437927, 12.88599616],
#     [70.07708794, 23.02577285],
#     [70.10046902, 32.97296503],
#     [70.06076727, 40.84457273],
#     [70.07140696, 49.10596848],
#     [70.07607828, 55.78395393],
#     [70.08666118, 63.39261649],
#     [68.78069174, 69.32106706],
#     [52.79118295, 70.04754376],
#     [45.51745512, 70.04859794],
#     [8.34975211, 70.06047023],
#     [60.95281657, 70.0615642],
#     [26.09805376, 70.07143242],
#     [14.49138324, 70.08360033],
#     [35.78580842, 70.08716856],
#     [-52.37129377, 70.07994999],
#     [-41.11047037, 70.07977347],
#     [-10.08863848, 70.07210613],
#     [-21.69074247, 70.07163418],
#     [-30.92534569, 70.05823379],
#     [-66.2902759, 69.15289513],
#     [-70.07770264, 59.75545503],
#     [-70.04536109, 48.22995495],
#     [-70.06331432, 37.03650391],
#     [-70.07408107, 23.44248405],
#     [-70.04126752, 16.1506022],
#     [-70.06246422, 7.540169551],
#     [-70.08851617, -13.20051944],
#     [-70.0843573, -2.848029731],
#     [-70.07545044, -31.92001708],
#     [-70.0712191, -22.32481017],
#     [-70.06568468, -42.26225747],
#     [-70.06427722, -53.89950072],
#     [-67.00173721, -69.43852245],
#     [-59.79603374, -70.05735924],
#     [-49.01829075, -70.06794763],
#     [-40.55391547, -70.06244365],
#     [-28.62808306, -70.05598519],
#     [-20.5235214, -70.05881948],
#     [-11.65446994, -70.08000326],
#     [-4.731044018, -70.10271411],
#     [21.45442194, -70.09952254],
#     [61.48234846, -70.09341012],
#     [38.91841918, -70.08262046],
#     [2.316239534, -70.07337496],
#     [30.38005273, -70.06902452],
#     [50.2006423, -70.06628706],
#     [12.88606497, -70.06196107],
#     [70.05309574, -64.92346636],
#     [70.04657732, -54.00804821],
#     [70.07464553, -41.45829343],
#     [70.04689666, -30.86640521],
#     [70.08603898, -19.71816283],
#     [70.06595873, -12.13725114],
#     [70.0528856, -5.598874539]
# ])

# # Start from the first point
# start_point = coordinates[0]
# current_point = start_point
# visited = set()
# connected_points = [start_point]

# while len(visited) < len(coordinates) - 1:
#     nearest_distance = float("inf")
#     nearest_point = None

#     for point in coordinates:
#         if tuple(point) not in visited and not np.array_equal(point, current_point):
#             distance = np.linalg.norm(current_point - point)
#             if distance < nearest_distance:
#                 nearest_distance = distance
#                 nearest_point = point

#     if nearest_point is not None:
#         visited.add(tuple(nearest_point))
#         connected_points.append(nearest_point)
#         current_point = nearest_point
#     else:
#         break

# # Convert the connected points to a NumPy array
# connected_points = np.array(connected_points)

# # Create a scatter plot of the points
# plt.scatter(coordinates[:, 0], coordinates[:, 1], label="Original Points", color='blue', marker='o')
# plt.scatter(connected_points[:, 0], connected_points[:, 1], label="Connected Points", color='red', marker='x')

# # Plot lines connecting the connected points
# for i in range(len(connected_points) - 1):
#     plt.plot([connected_points[i, 0], connected_points[i + 1, 0]],
#              [connected_points[i, 1], connected_points[i + 1, 1]], color='green')

# # Set labels and legend
# plt.xlabel('X-coordinate')
# plt.ylabel('Y-coordinate')
# plt.title('Connected Points Visualization')
# plt.legend()

# # Show the plot
# plt.show()

# import numpy as np
# import matplotlib.pyplot as plt
# import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import distance_matrix
from scipy.spatial import distance

# Given coordinates
coordinates = np.array([
    [70.0437927, 12.88599616],
    [70.07708794, 23.02577285],
    [70.10046902, 32.97296503],
    [70.06076727, 40.84457273],
    [70.07140696, 49.10596848],
    [70.07607828, 55.78395393],
    [70.08666118, 63.39261649],
    [68.78069174, 69.32106706],
    [52.79118295, 70.04754376],
    [45.51745512, 70.04859794],
    [8.34975211, 70.06047023],
    [60.95281657, 70.0615642],
    [26.09805376, 70.07143242],
    [14.49138324, 70.08360033],
    [35.78580842, 70.08716856],
    [-52.37129377, 70.07994999],
    [-41.11047037, 70.07977347],
    [-10.08863848, 70.07210613],
    [-21.69074247, 70.07163418],
    [-30.92534569, 70.05823379],
    [-66.2902759, 69.15289513],
    [-70.07770264, 59.75545503],
    [-70.04536109, 48.22995495],
    [-70.06331432, 37.03650391],
    [-70.07408107, 23.44248405],
    [-70.04126752, 16.1506022],
    [-70.06246422, 7.540169551],
    [-70.08851617, -13.20051944],
    [-70.0843573, -2.848029731],
    [-70.07545044, -31.92001708],
    [-70.0712191, -22.32481017],
    [-70.06568468, -42.26225747],
    [-70.06427722, -53.89950072],
    [-67.00173721, -69.43852245],
    [-59.79603374, -70.05735924],
    [-49.01829075, -70.06794763],
    [-40.55391547, -70.06244365],
    [-28.62808306, -70.05598519],
    [-20.5235214, -70.05881948],
    [-11.65446994, -70.08000326],
    [-4.731044018, -70.10271411],
    [21.45442194, -70.09952254],
    [61.48234846, -70.09341012],
    [38.91841918, -70.08262046],
    [2.316239534, -70.07337496],
    [30.38005273, -70.06902452],
    [50.2006423, -70.06628706],
    [12.88606497, -70.06196107],
    [70.05309574, -64.92346636],
    [70.04657732, -54.00804821],
    [70.07464553, -41.45829343],
    [70.04689666, -30.86640521],
    [70.08603898, -19.71816283],
    [70.06595873, -12.13725114],
    [70.0528856, -5.598874539]
])
coordinates2 = np.array([
    [85.04296403, 9.689866105],
    [85.01945637, 24.1834373],
    [85.00596924, 36.58063406],
    [84.95767044, 51.55812632],
    [84.96232595, 64.82460696],
    [85.02441481, 77.35650812],
    [82.34092921, 84.689937],
    [11.40314244, 84.97519644],
    [46.99750036, 84.97850278],
    [68.47052707, 85.0028451],
    [33.84616172, 85.00796311],
    [3.16567797, 85.0252789],
    [58.19283425, 85.02812112],
    [22.57691856, 85.02888154],
    [-51.97031418, 85.02116037],
    [-9.468338241, 85.01502612],
    [-77.33407805, 85.00979511],
    [-65.2648726, 85.00642218],
    [-28.79958192, 84.99410704],
    [-41.04346174, 84.98125694],
    [-18.12648713, 84.92950357],
    [-84.87377439, 81.55607802],
    [-84.99562525, 63.01052156],
    [-84.97745441, 51.44891472],
    [-84.98822982, 40.11117811],
    [-84.98727734, 29.69494888],
    [-84.98980158, 18.96195435],
    [-84.97390087, 5.291863361],
    [-85.02155891, -71.02991211],
    [-85.00904017, -10.43491277],
    [-85.00343795, -32.9121765],
    [-85.00192395, -42.76451986],
    [-84.99892658, -58.64828568],
    [-84.99195717, -23.52216561],
    [-84.98822774, -51.10418237],
    [-83.98973502, -82.12603146],
    [-70.84223646, -85.01382807],
    [-57.13529991, -85.02660198],
    [-45.74744115, -85.00687935],
    [-34.43535671, -85.03722828],
    [-23.5945731, -85.00094303],
    [-12.77051764, -85.02281825],
    [-0.912591592, -85.00580876],
    [64.14713849, -85.02058685],
    [75.03060844, -85.01663611],
    [35.92095388, -85.01457872],
    [9.974347208, -85.0136508],
    [49.08446517, -84.99397882],
    [25.53278051, -84.98413527],
    [84.99171242, -75.02576615],
    [85.00493725, -56.88783325],
    [84.99217913, -40.0799584],
    [84.98504654, -26.40705641],
    [84.98889505, -15.34368567],
    [85.01266581, -0.986445477]
])
# Create a graph
# G = nx.Graph()

# # Add nodes to the graph
# for i, coord in enumerate(coordinates):
#     G.add_node(i, pos=(coord[0], coord[1]))

# # Calculate distances and add edges to connect nodes
# for u in G.nodes():
#     for v in G.nodes():
#         if u != v:
#             distance = np.linalg.norm(np.array(G.nodes[u]['pos']) - np.array(G.nodes[v]['pos']))
#             G.add_edge(u, v, weight=distance)

# # Find the minimum spanning tree
# T = nx.minimum_spanning_tree(G)

# # Extract the connected points in order
# connected_points = np.array([G.nodes[node]['pos'] for node in nx.dfs_preorder_nodes(T, 0)])

# for point in connected_points:
#     print(point)

# # Create a scatter plot of the points
# plt.scatter(coordinates[:, 0], coordinates[:, 1], label="Original Points", color='blue', marker='o')
# plt.scatter(connected_points[:, 0], connected_points[:, 1], label="Connected Points", color='red', marker='x')

# # Plot lines connecting the connected points
# for i in range(len(connected_points) - 1):
#     plt.plot([connected_points[i, 0], connected_points[i + 1, 0]],
#              [connected_points[i, 1], connected_points[i + 1, 1]], color='green')

# # Set labels and legend
# plt.xlabel('X-coordinate')
# plt.ylabel('Y-coordinate')
# plt.title('Connected Points Visualization')
# plt.legend()

# # Show the plot
# plt.show()
# Start from the first point
print(coordinates)
start_point = coordinates[0]
current_point = start_point
connected_points = [start_point]  # Include the start point at the beginning
remaining_points = list(coordinates[1:])  # Remove the start point

while remaining_points:
    nearest_point = min(remaining_points, key=lambda point: distance.euclidean(current_point, point))
    remaining_points = [point for point in remaining_points if not np.array_equal(point, nearest_point)]
    connected_points.append(nearest_point)
    current_point = nearest_point

# Convert the connected points to a NumPy array
connected_points = np.array(connected_points)

# Create a scatter plot of the points
plt.scatter(coordinates[:, 0], coordinates[:, 1], label="Original Points", color='blue', marker='o')
plt.scatter(connected_points[:, 0], connected_points[:, 1], label="Connected Points", color='red', marker='x')

# Plot lines connecting the connected points
for i in range(len(connected_points) - 1):
    plt.plot([connected_points[i, 0], connected_points[i + 1, 0]],
             [connected_points[i, 1], connected_points[i + 1, 1]], color='green')

# Filter the coordinates in the first quadrant (both x and y positive)
first_quadrant_coordinates = coordinates[(coordinates[:, 0] > 0) & (coordinates[:, 1] > 0)]

if len(first_quadrant_coordinates) > 0:
    # Find the coordinate in the first quadrant closest to y=0
    nearest_coordinate = first_quadrant_coordinates[np.argmin(np.abs(first_quadrant_coordinates[:, 1]))]

    print("Coordinate closest to y=0 in the first quadrant (positive x and y region):", nearest_coordinate)
else:
    print("No coordinates found in the first quadrant with both x and y positive.")

# Set labels and legend
plt.xlabel('X-coordinate')
plt.ylabel('Y-coordinate')
plt.title('Connected Points Visualization')
plt.legend()

# Show the plot
plt.show()
