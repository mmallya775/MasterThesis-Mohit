from abb_robot_client.rws import RWS
import json

c = RWS()

print("================")
ttr = """CONST robtarget Target_1:=[[1449.182064069,600,1345.018020125],[0,0,1,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_2:=[[1999.182064069,200,1000.018020125],[0,0,1,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_3:=[[1449.182064069,-600,1000.018020125],[0,0,1,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS tooldata MyTool:=[TRUE,[[31.792631019,0,229.638935148],[0.945518576,0,0.325568154,0]],[1,[0,0,1],[1,0,0,0],0,0,0]];
"""
print(c.get_robtarget())
module_text_inside2 = f"""MODULE Module1 
    {ttr}

    PROC main()
        Path_1;
    ENDPROC

    PROC Path_1()
        MoveJ Target_1, v1000,fine,MyTool\WObj:=wobj0;
        MoveL Target_2, v100,fine,MyTool\WObj:=wobj0;

        MoveJ Target_1, v100,fine,MyTool\WObj:=wobj0;
        MoveC Target_2, Target_3, v200,fine,MyTool\WObj:=wobj0;

    ENDPROC
ENDMODULE
"""
# module_text_inside2 = """MODULE Module1
#     CONST robtarget Target_10:=[[1449.182064069,600,1345.018020125],[0,0,1,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
#     CONST robtarget Target_20:=[[1699.182064069,200,1000.018020125],[0,0,1,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
#     CONST robtarget Target_30:=[[1449.182064069,-600,1000.018020125],[0,0,1,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
#     PERS tooldata MyTool:=[TRUE,[[31.792631019,0,229.638935148],[0.945518576,0,0.325568154,0]],[1,[0,0,1],[1,0,0,0],0,0,0]];
#
#     PROC main()
#         Path_1;
#     ENDPROC
#
#     PROC Path_1()
#         MoveJ Target_10, v1000,fine,MyTool\WObj:=wobj0;
#         MoveL Target_20, v1000,fine,MyTool\WObj:=wobj0;
#
#         MoveJ Target_10, v1000,fine,MyTool\WObj:=wobj0;
#         MoveC Target_20, Target_30, v1000,fine,MyTool\WObj:=wobj0;
#
#     ENDPROC
# ENDMODULE
# """
module_text_inside = "MODULE Module1 \n     \tCONST robtarget Target_10:=[[1349.182064069,0,1345.018020125],[0,0,1,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];"
df = {
    'text': module_text_inside2
}

# c._do_post("rw/rapid/tasks/T_ROB1/modules/Module1?action=set-module-text", payload=df)
module_path = "rw/rapid/modules/"
c._do_post("rw/rapid/modules/Module1?task=T_ROB1&action=set-module-text", payload=df)
c.resetpp()
# c.start()
