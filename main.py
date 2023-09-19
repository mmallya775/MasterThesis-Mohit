import Geometry
import RAPIDCodeGenerator


filepath = "NewConeCirc.STL"

g = Geometry.GeometryImport(filepath)
layer_data = g.layer_part()
# print(layer_data)
g.points_visualization()
g.plot_contours(layer_data)

# r = RAPIDCodeGenerator.RAPIDGenerator()
# r.MoveL()
