# 五子棋游戏

一个基于Python的五子棋游戏，支持2D和3D两种游戏模式，包含多种AI算法对战功能。


## 游戏引擎

- **pygame**（2D版本）- 轻量级，性能稳定
- **panda3d**（3D版本）- 3D渲染，沉浸体验

## AI算法

本游戏集成了三种不同的AI算法：

| AI类型 | 算法特点 | 棋力水平 | 思考时间 |
|--------|----------|----------|----------|
| **Classical** | 基于规则的启发式算法 | ⭐⭐⭐⭐⭐ | 中等 |
| **Minimax** | 极小极大算法+α-β剪枝 | ⭐⭐⭐⭐ | 中等 |
| **MCTS** | 蒙特卡洛树搜索 | ⭐⭐⭐⭐ | 慢 |

## 游戏操作说明

### 游玩方式
- **1.移动到棋盘周围**
- **2.按下Space键进入棋局**
- **3.左键棋匣**: 提子
- **4.按住左键，拖动鼠标**: 移动棋子
- **5.松开左键**: 落子

#### 棋局外键位
- **A键**: 向左移动
- **D键**: 向右移动
- **W键**: 向前移动
- **S键**: 向后移动
- **鼠标**: 移动视角
- **Space键**: 进入棋局

#### 棋局内键位
- **按下左键**: 提子
- **按住左键，拖动鼠标**: 移动棋子
- **松开左键**: 落子
- **鼠标滚轮**: 缩放视角
- **A键**: 摄像机向左旋转
- **D键**: 摄像机向右旋转
- **W键**: 摄像机向上俯视
- **S键**: 摄像机向下仰视

#### 游戏功能键
- **R键**: 重新开始游戏
- **U键**: 悔棋
- **ESC键**: 退出游戏
- **TAB键**: 显示/隐藏帮助信息

### 2D版本指南
- **鼠标左键**: 落子
- **ESC键**: 退出游戏

## 项目结构

```
├── run_2d.py              # 2D版本启动文件
├── run_3d.py              # 3D版本启动文件
├── frontend_2d/           # 2D游戏界面
│   ├── game.py            # 2D游戏主逻辑
│   └── ui.py              # 2D界面绘制
├── frontend_3d/           # 3D游戏界面
│   ├── game.py            # 3D下棋模式主逻辑
│   ├── CSGO_mode.py       # 3D漫游模式主逻辑
│   ├── setup_board.py     # 3D棋盘初始化
│   ├── setup_scene.py     # 3D环境初始化
│   ├── camera_controller.py  # 摄像机控制
│   ├── mouse_picker.py    # 鼠标拾取
│   ├── audio_manager.py   # 音频管理
│   ├── ui_manager.py      # UI管理
│   ├── effects_manager.py # 特效管理
│   └── input_manager.py   # 输入管理
├── utils/                 # 工具模块
│   ├── chessboard.py      # 棋盘逻辑
│   ├── gomoku_ai.py       # AI基类
│   └── constants.py       # 游戏常量
│   └── minimax_ai_engine.py  # Minimax引擎
├── Gomoku_ai_classical/   # 经典AI算法
│   └── ai.py              # 启发式AI实现
├── Gomoku_ai_minimax/     # Minimax AI算法
│   ├── ai.py              # Minimax AI实现
├── Gomoku_ai_MCTS/        # MCTS AI算法
│   └── ai.py              # MCTS AI实现
├── pieces/                # 棋子相关
├── sound/                 # 音频相关
└── models/                # 模型相关
```

## 游戏特色

### 核心功能
- ✅ **人机对战**: 三种AI算法可选
- ✅ **强大功能**: 
- ✅ **游戏统计**: 胜负记录和用时统计

### 3D版本特色
- ⚡ **流畅操作**: 响应迅速
- 🎮 **沉浸体验**: 3D立体场景建模
- ✨ **视觉特效**: 粒子效果和动态光照
- 🎵 **环境音效**: 立体声音频体验
- 📹 **自由视角**: 360°旋转观察

## 使用说明

本项目包含部分大体积的3D模型文件，采用 [Git Large File Storage (LFS)](https://git-lfs.github.com/) 进行管理。  
**首次使用或克隆本项目时，请务必按照以下步骤操作：**

1. **安装 Git LFS**
```bash
   git lfs install
```

2. **克隆项目并拉取大文件**
```bash
git clone git clone https://github.com/mightheart/Gomoku_start.git
cd gomoku-game
git lfs pull
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **运行游戏**
```bash
# 运行2D版本
python run_2d.py

# 运行3D版本（推荐）
python run_3d.py

## 开发说明

### AI算法对比

| 特性 | Classical | Minimax | MCTS |
|------|-----------|---------|------|
| **实现复杂度** | 简单 | 中等 | 复杂 |
| **内存占用** | 低 | 中等 | 高 |
| **可扩展性** | 有限 | 良好 | 优秀 |
| **学习能力** | 无 | 无 | 有限 |

### 贡献指南
欢迎提交Issue和Pull Request！

- 🐛 **Bug报告**: 请详细描述复现步骤
- 💡 **功能建议**: 欢迎提出改进想法
- 🔧 **代码贡献**: 请遵循项目代码规范

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 更新日志