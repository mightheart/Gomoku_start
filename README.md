This is a simple Gomoku_start interface.
Only need pygame and numpy to run.

## 📁 项目结构

```
Gomoku_ai_integrate/
├── main.py              # 主程序入口
├── game.py              # 游戏主类
├── ai.py                # AI相关功能
├── ui.py                # 界面绘制相关
├── utils.py             # 工具函数
├── constants.py         # 常量定义
├── config_4.py          # AI配置
└── data/
    └──  # 资源文件
└── font/
    └──  # 字体文件
```

### 文件说明

- **main.py** - 启动游戏
- **game.py** - 包含游戏主类 `GobangGame`，处理游戏逻辑
- **ai.py** - AI算法实现，包含棋型评估和决策逻辑
- **ui.py** - 用户界面相关功能，负责绘制游戏界面
- **utils.py** - 通用工具函数，如坐标转换、胜负判断等
- **constants.py** - 游戏常量定义，如颜色、尺寸等
- **config_4.py** - AI配置文件，包含棋型评估模型
- **data/** - 资源文件目录
- **font/** - 字体文件目录
