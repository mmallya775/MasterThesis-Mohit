"""
A python library to generate RAPID program from the points generated using an object of the Geometry class.

"""
import numpy as np


class RAPIDGenerator:

    def __init__(self):
        self.ModuleStart = 'MODULE Module1 \n'
        self.RobTargets = ''
        self.ProcMain = 'PROC main() \n'
        self.CallProc = 'Path; \n'
        self.EndProc = 'ENDPROC \n'
        self.PathProc = 'PROC Path() \n'
        self.EndModule = 'ENDMODULE \n'

    def MoveL(self, translation, rotation=np.array([0, 0, 1, 0]), configuration=np.array([0, 0, 0, 0]),
              externalaxes=np.array([9E+09, 9E+09, 9E+09, 9E+09, 9E+09, 9E+09])):
        print(self.ModuleStart + self.RobTargets + self.ProcMain + self.CallProc + self.EndProc + self.PathProc +
              self.EndProc + self.EndModule)
