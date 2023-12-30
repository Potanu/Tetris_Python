import pygame
from enum import Enum
from enum import IntEnum

# シーンの種別
class SceneType(Enum):
    TITLE = 0,
    GAME = 1

# オブジェクトの種別
class ObjectType(IntEnum):
    BG = 0,     # 背景
    OBJECT = 1, # オブジェクト
    EFFECT = 2, # エフェクト
    UI = 3,     # UI
    DEBUG = 4   # デバッグ表示

# 描画の種別
class DrawType(Enum):
    TEXT = 0,       # テキスト
    RECT = 1,       # 矩形
    RECT_ALPHA = 2  # 矩形（α値指定）
    LINE = 3,       # 線
    FILL = 4,       # 塗りつぶし
    
# 描画情報判別用
class DrawData(IntEnum):
    OBJECT_TYPE = 0,# オブジェクトの種別
    Z_ORDER = 1,    # 描画順
    DRAW_TYPE = 2,  # 描画の種別
    IMAGE = 3,      # 画像
    COLOR = 4,      # 色
    RECT = 5,       # 矩形
    START_POS = 6,  # 始点の座標
    END_POS = 7,    # 終点の座標
    WIDTH = 8       # 線の幅

# キーの種別
class KeyType(IntEnum):
    W = pygame.K_w,
    A = pygame.K_a,
    S = pygame.K_s,
    D = pygame.K_d,
    Q = pygame.K_q,
    E = pygame.K_e,
    P = pygame.K_p,
    H = pygame.K_h,
    UP = pygame.K_UP,
    DOWN = pygame.K_DOWN,
    RIGHT = pygame.K_RIGHT,
    LEFT = pygame.K_LEFT,
    DEBUG = pygame.K_F1  # デバッグ用

# ミノの種類
class MinoType(IntEnum):
    NONE = 0,
    I = 1,
    O = 2,
    S = 3,
    Z = 4,
    J = 5,
    L = 6,
    T = 7

# ミノの動き
class MinoMoveType(Enum):
    MOVE_RIGHT = 0,     # 右移動
    MOVE_LEFT = 1,      # 左移動
    ROTATE_RIGHT = 2,   # 右回転
    ROTATE_LEFT = 3,    # 左回転
    FALL = 4,           # 1マス降下

# ゲームの状態
class GameState(Enum):
    READY = 0,
    GAME = 1,
    PAUSE = 2,
    GAME_OVER = 3,
    END = 4
