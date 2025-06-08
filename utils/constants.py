"""
常量定义文件
"""
# 设置常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
CELL_SIZE = 40

# 颜色定义 (2D游戏使用)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
LIGHT_BROWN = (205, 133, 63)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
GOLD = (255, 215, 0)  # 用于高亮获胜棋子

# 颜色定义 (3D游戏使用 - RGBA格式)
BLACK_3D = (0, 0, 0, 1)
WHITE_3D = (1, 1, 1, 1)
HIGHLIGHT = (0.92, 0.88, 0.77, 1)     # 高亮颜色
PIECEBLACK = (.15, .15, .15, 1)
WOOD_LIGHT = (0.92, 0.88, 0.77, 1)    # 浅色木材
WOOD_MEDIUM = (0.71, 0.55, 0.35, 1)   # 中等色调木材
WOOD_DARK = (0.54, 0.27, 0.07, 1)     # 深色木材
WOOD_WALNUT = (0.39, 0.26, 0.13, 1)   # 胡桃木色

# 游戏状态
GAME_STATE_MENU = "menu"
GAME_STATE_SELECT_SIZE = "select_size"  # 新增
GAME_STATE_SELECT_SIDE = "select_side"
GAME_STATE_PLAYING = "playing"

# 玩家标识
PLAYER_BLACK = 1
PLAYER_WHITE = 2

# 棋子符号
PIECE_BLACK = 'X'
PIECE_WHITE = 'O'
PIECE_EMPTY = ' '

# 摄像机控制常量
CAMERA_INITIAL_POSITION = (0, -16.5, 11)  # 初始摄像机位置
CAMERA_INITIAL_ANGLES = (0, -35, 0)     # 初始摄像机角度 (Roll-Pitch-Yaw)
CAMERA_ROTATION_SPEED = 30              # 视角旋转速度(度/秒)
CAMERA_MAX_PITCH = -15                  # 最大俯仰角
CAMERA_MIN_PITCH = -52                  # 最小俯仰角

# 摄像机加速度控制常量
CAMERA_ACCELERATION = 2000.0             # 加速度系数（度/秒²）
CAMERA_MAX_SPEED_MULTIPLIER = 10000.0       # 最大速度倍数
CAMERA_ACCELERATION_DELAY = 0.1      # 开始加速前的延迟时间（秒）

# 棋盘常量
BOARD_SIZE = 15                 # 棋盘大小 (15x15)
PIECE_DRAG_HEIGHT = 0.5         # 棋子拖动高度
TOTAL_SQUARES = 225             # 15x15
MAX_PIECES_PER_PLAYER = 100     # 15x15棋盘最多需要的棋子数

# 模型缩放比例
SQUARE_SCALE = 0.65  # 格子缩放比例
PIECE_SCALE = 0.85   # 棋子缩放比例
HIGHLIGHT_INDICATOR_RADIUS = 0.3  # 高亮指示器缩放比例
HIGHLIGHT_INDICATOR_SEGMENT = 32  # 高亮指示器分段数，越多越圆滑
MODEL_SCALE = 0.5  # 模型缩放比例，用于调节模型大小

# 棋盒位置
WHITE_BOX_POS = (0, -6, 0)  # 白棋盒位置
BLACK_BOX_POS = (0, 6, 0)   # 黑棋盒位置
BOX_SIZE = 1              # 棋盒缩放比例

# 背景图片位置常量
BACKGROUND_POSITION = (0, 100, 8)  # 默认位置，便于调整

# 装饰模型的轴向缩放比例
DECORATION_SCALE_X = 0.008  # X轴缩放比例
DECORATION_SCALE_Y = 0.008  # Y轴缩放比例
DECORATION_SCALE_Z = 0.008  # Z轴缩放比例

# 装饰模型的旋转和位置调节参数
DECORATION_ROTATION = (0, 90, 0)  # 默认旋转角度 (X, Y, Z)
DECORATION_POSITION_OFFSET = (0, 0, -0.3)  # 默认位置偏移 (X, Y, Z)

# 棋盘厚度模型的大小和位置调节参数
THICKNESS_SCALE = (0.5, 5.75, 0.2)  # 默认缩放比例 (X, Y, Z)
THICKNESS_POSITION_OFFSET = (0, 0, -0.21)  # 默认位置偏移 (X, Y, Z)

# 对手模型的路径、位置、缩放和旋转参数
OPPONENT_MODEL_PATH = "models/opponent1.obj"  # 对手模型路径
OPPONENT_MODEL_POSITION = (0,20,-10)  # 默认位置 (X, Y, Z)
OPPONENT_MODEL_SCALE = (15,15,15)  # 默认缩放比例 (X, Y, Z)
OPPONENT_MODEL_ROTATION = (0, 0, 0)  # 默认旋转角度 (X, Y, Z)

# 星空相关常量
SKYDOME_MODEL_PATH = "models/misc/sphere"
SKYDOME_SCALE = 1000
SKYDOME_COLOR = (0, 0, 0, 1)
SKYDOME_BIN = "background"
SKYDOME_DEPTHWRITE = False
SKYDOME_LIGHTOFF = 1
SKYDOME_RADIUS = 95
STAR_CONTAINER_NAME = "stars"
STAR_BIN = "background"
STAR_DEPTHWRITE = False
STAR_LIGHTOFF = 1
STAR_POINTS_NODE_NAME = "star_points"
STAR_NUM = 2000
STAR_POINT_SIZE = 3.0
FALLBACK_SKY_FRAME = (-100, 100, -100, 100)
FALLBACK_SKY_P = -90
FALLBACK_SKY_Z = -50
FALLBACK_SKY_BIN = "background"
FALLBACK_SKY_DEPTHWRITE = False
FALLBACK_SKY_LIGHTOFF = 1

# 音频常量
SOUND_CLICK = "sound/place_piece.mp3"  # 下棋
BGM_LIST = ["sound/bgm1.mp3", "sound/bgm3.mp3", 
            "sound/bgm2.wav", 
            "sound/bgm4.flac", "sound/bgm5.flac"]  # BGM列表
WINNER_MUSIC = "sound/winner_music.wav"  # 获胜音乐
LOSER_MUSIC = "sound/loser_music.mp3"  # 失败音乐
SOUND_VOLUME = 0.3  # BGM默认音量