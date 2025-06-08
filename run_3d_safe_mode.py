"""
安全模式运行五子棋游戏
"""

from panda3d.core import loadPrcFileData
import sys
import os

# 在任何Panda3D组件初始化前设置
def setup_safe_mode():
    """设置安全模式配置"""
    # 禁用可能导致矩阵问题的功能
    loadPrcFileData("", "basic-shaders-only true")
    loadPrcFileData("", "hardware-animated-vertices false")
    loadPrcFileData("", "matrix-palette false")
    loadPrcFileData("", "vertex-buffers false")
    
    # 强制使用简单渲染路径
    loadPrcFileData("", "gl-force-no-error true")
    loadPrcFileData("", "gl-force-no-flush true")
    loadPrcFileData("", "prefer-parasite-buffer false")
    
    # 设置保守的渲染设置
    loadPrcFileData("", "framebuffer-multisample false")
    loadPrcFileData("", "multisamples 0")
    
    # 数值稳定性
    loadPrcFileData("", "default-near 1.0")
    loadPrcFileData("", "default-far 1000.0")
    
    # 禁用一些高级功能
    loadPrcFileData("", "support-stencil false")
    loadPrcFileData("", "depth-bits 16")
    loadPrcFileData("", "color-bits 16 16 16")
    
    print("安全模式配置已应用")

if __name__ == "__main__":
    setup_safe_mode()
    
    try:
        from frontend_3d.game import Gomoku_Start
        demo = Gomoku_Start()
        demo.run()
    except Exception as e:
        print(f"安全模式启动失败: {e}")
        print("\n请尝试以下解决方案:")
        print("1. 运行 system_diagnosis.py 进行系统诊断")
        print("2. 更新显卡驱动")
        print("3. 以管理员权限运行")
        input("按Enter键退出...")