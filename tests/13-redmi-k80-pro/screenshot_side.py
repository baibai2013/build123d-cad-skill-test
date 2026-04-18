"""
生成手机壳右侧视图截图（按键面）/ Generate right-side view screenshot (button side)
模型 +X 面 = 背面视角左侧 = 按键所在面
"""
from build123d import *
import os, sys, time

sys.path.insert(0, os.path.dirname(__file__))
from redmi_k80_pro_case import v2, output_dir

try:
    from ocp_vscode import show, set_port, Camera, save_screenshot
    from ocp_vscode.comms import port_check
    from ocp_vscode.state import get_ports

    active_port = next((int(p) for p in get_ports() if port_check(int(p))), None)
    if active_port:
        set_port(active_port)

        # Camera.RIGHT: 从 +X 方向看（看到模型右侧 = 按键面）
        # Camera.RIGHT: looking from +X direction (sees model right side = button side)
        show(v2, names=["k80_pro_case_right"], reset_camera=Camera.RIGHT)
        time.sleep(1.0)
        save_screenshot(os.path.join(output_dir, "k80_pro_case_RIGHT.png"))
        print("Screenshot: k80_pro_case_RIGHT.png ✓")

        # Camera.LEFT: 从 -X 方向看（对面）
        show(v2, names=["k80_pro_case_left"], reset_camera=Camera.LEFT)
        time.sleep(1.0)
        save_screenshot(os.path.join(output_dir, "k80_pro_case_LEFT.png"))
        print("Screenshot: k80_pro_case_LEFT.png ✓")

        print("两侧截图已生成，检查哪个有按键开孔 / Both sides saved, check which has buttons")
    else:
        print("OCP Viewer 未检测到")
except Exception as e:
    print(f"Error: {e}")
