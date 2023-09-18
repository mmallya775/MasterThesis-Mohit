import Geometry
import RAPIDCodeGenerator


filepath = "Design Funnnel Type Inside.stl"

g = Geometry.GeometryImport(filepath)
layer_data = g.layer_part()
# print(layer_data)
g.points_visualization()
#
# r = RAPIDCodeGenerator.RAPIDGenerator()
# r.MoveL()
