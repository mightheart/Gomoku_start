# 五子棋游戏

一个基于Python的五子棋游戏，支持2D和3D两种游戏模式，包含AI对战功能。

## 运行方式

```bash
# 运行2D版本（推荐）
python run_2d.py

# 运行3D版本
python run_3d.py

# 3D版本遇到问题时使用安全模式
python run_3d_safe_mode.py
```

## 游戏引擎

- pygame（2D版本）
- panda3d（3D版本）

## 项目结构

```
├── run_2d.py           # 2D版本启动文件
├── run_3d.py           # 3D版本启动文件
├── frontend_2d/        # 2D游戏界面
│   ├── game.py         # 2D游戏主逻辑
│   └── ui.py           # 2D界面绘制
├── frontend_3d/        # 3D游戏界面
│   └── game.py         # 3D游戏主逻辑
├── utils/              # 工具模块
│   ├── chessboard.py   # 棋盘逻辑
│   └── gomoku_ai.py    # AI算法
├── Gomoku_ai_classical/# 经典AI算法
└── pieces/             # 棋子相关
```

## 游戏特色

- 支持人机对战
- 多种AI难度
- 2D/3D双模式
- 酷炫游戏界面