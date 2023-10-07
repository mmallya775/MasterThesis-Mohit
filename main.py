"""# import Geometry
# import RAPIDCodeGenerator
"""

import time

from Geometry4 import GeometryImport

# if __name__ == "__main__":
#
#     FILE_PATH = "FromRP.STL"
#     start = time.time()
#
#     g2 = GeometryImport(filepath=FILE_PATH)
#     # g2.points_visualization()
#     pointcloud = g2.generate_sequential_contour_points(layer_height=0.5, alpha_value=0.2)
#     end = time.time()
#
#     g2.plot_contours(pointcloud)
#     print(end-start)


#
# g = Geometry.GeometryImport(filepath)
# layer_data = g.layer_part()
# # print(layer_data)
# print("Size =", len(layer_data[:, 0]))
# # print(g.conf_T_ROB1(layer_data))
# # g.rot_T_ROB1(layer_data)
# g.points_visualization()
# g.plot_contours(layer_data)
#
# r = RAPIDCodeGenerator.RAPIDGenerator()
# r.MoveL()

if __name__ == "__main__":

    FILE_PATH = "FromRP.STL"
    start_time = time.time()
    g2 = GeometryImport(filepath=FILE_PATH)
    pointcloud = g2.parallel_generate_sequential_contour_points(layer_height=0.25, alpha_value=0.2)
    end_time = time.time()
    print("Total Processing Time: ", end_time-start_time)
    g2.plot_contours(pointcloud)
