import Geometry
import RAPIDCodeGenerator
from Geometry2 import GeometryImport

filepath = "Design Funnnel Type Inside.stl"
#
# g = Geometry.GeometryImport(filepath)
# layer_data = g.layer_part()
# # print(layer_data)
# print("Size =", len(layer_data[:, 0]))
# # print(g.conf_T_ROB1(layer_data))
# # g.rot_T_ROB1(layer_data)
# g.points_visualization()
# g.plot_contours(layer_data)

# r = RAPIDCodeGenerator.RAPIDGenerator()
# r.MoveL()

g2 = GeometryImport(filepath=filepath)
pointcloud = g2.generate_sequential_contour_points(layer_height=1.6)
g2.plot_contours(pointcloud)
