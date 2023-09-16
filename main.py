import Geometry
import RAPIDCodeGenerator


filepath = "C:/Users/mmall/OneDrive/Desktop/model1.stl"

g = Geometry.GeometryImport(filepath)
layer_data = g.layer_part()
print(layer_data)
g.points_visualization()
