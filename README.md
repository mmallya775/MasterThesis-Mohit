# MasterThesis-Mohit
The Geometry library contains the GeometryImport class. Through this class '.stl' can be imported
from which a pointcloud of 100,000 points on the surface is generated
and the part is layered into multiple layers of user specific layer thickness. Subsequently the points lying on the convex hull
of each layer is determined and these points are sequenced in increasing order of their quadrants. These sequenced points are then sent to RAPID code
generator for generating robotic paths.  
The robot path is directly loaded into the robot controller using Robo Web Services (RWS) Rest API.  
## Geometry Import

## RAPID Code Genertion

## GUI

## RWS using HTTP REST