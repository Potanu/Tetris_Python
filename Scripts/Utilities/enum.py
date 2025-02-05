from enum import Enum
from enum import IntEnum

# シーンの種別
class SceneType(Enum):
    SELECT = 0,     # シーン選択
    GAME = 1,       # ゲーム画面
    AI_LEARNING = 2 # AI学習
 
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
    W = 0,
    A = 1,
    S = 2,
    D = 3,
    P = 4,
    RIGHT = 5,
    LEFT = 6,
    SPACE = 7,
    ESC = 8
    F1 = 9

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
    HARD_DROP = 5       # ハードドロップ

# ゲームの状態
class GameState(Enum):
    READY = 0,              # 待機
    FALL = 1,               # ミノの降下中
    PROCESS_LANDING = 2,    # ミノの接地時の処理
    CLEAR_LINE = 3,         # ラインクリア
    CLEAR_LINE_ANIM = 4,    # ラインクリア演出中
    DROP_LINE = 5,          # ラインクリア後、ブロックを下に詰める処理
    PAUSE = 6,              # 一時停止
    GAME_OVER = 7,          # ゲームオーバー
    END = 8,                # 終了

# BGM
class bgmType(IntEnum):
    # BGM
    GAME = 0,               # デフォルトBGM

# SE 
class SeType(IntEnum):
    # SE
    PUT_BLOCK = 0,          # ブロック接地
    CLEAR_LINE = 1,         # ライン消し
    CLEAR_ALL_BLOCK = 2     # ブロック全消し

# 強化学習用のアクション定義
class ACTION_SPACE_TYPE(IntEnum):
    MOVE_RIGHT = 0,     # 右移動
    MOVE_LEFT = 1,      # 左移動
    ROTATE_RIGHT = 2,   # 右回転
    ROTATE_LEFT = 3,    # 左回転
    HARD_DROP = 4       # ハードドロップ
