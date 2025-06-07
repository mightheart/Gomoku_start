"""
五子棋人机对战主程序
"""
from frontend_2d.game import GobangGame

def main():
    """主函数"""
    try:
        game = GobangGame()
        game.run()
    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()