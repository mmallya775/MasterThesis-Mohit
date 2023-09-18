"""
A python library to generate RAPID program from the points generated using an object of the Geometry class.

"""


class RAPIDGenerator:

    def __init__(self):
        self.ModuleStart = 'MODULE Module1 \n'
        self.RobTargets = ''
        self.ProcMain = 'PROC main() \n'
        self.CallProc = 'Path; \n'
        self.EndProc = 'ENDPROC \n'
        self.PathProc = 'PROC Path() \n'
        self.EndModule = 'ENDMODULE \n'

    def MoveL(self):
        print(self.ModuleStart + self.RobTargets + self.ProcMain + self.CallProc + self.EndProc + self.PathProc + self.EndProc + self.EndModule)
