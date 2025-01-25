# =========================
# 共通
# =========================
SCREEN_SIZE = (1000, 660)
SCREEN_CENTER_POS = [SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2]
FPS = 60
JP_FONT_PASS = "Resources\\NotoSansJP-Medium.ttf"       # 日本語フォントのパス

# =========================
# ゲーム
# =========================
GAME_SCREEN_OFFSET = (320, 0) # ゲームフィールドのオフセット
BOARD_GRID_NUM = (12, 23)     # ボードのマスの数
GAME_GRID_NUM = (10, 21)      # ゲームボードのマスの数
START_MINO_GRID = (4, 0)      # ミノの出現位置（左上のマス）
BLOCK_SIZE = (30, 30)         # ブロックサイズ
READY_FRAME = 90.0            # ゲーム開始までのフレーム
DEFAULT_FALL_SPEED = 48       # 何フレーム間隔で降下するか
FALL_HIGH_SPEED = 1           # 何フレーム間隔で降下するか（降下キー押下時）
LEVEL_UP_COUNT = 10           # 何段ミノを消したらレベルが上がるか
CLEAR_LINE_ANIM_SPEED = 10    # ライン消し演出速度
SPEED_UP_INTERVAL = 1         # レベルアップ時の速度上昇量
GAME_OVER_GRID_Y = 2          # ゲームオーバー判定縦マス数
NEXT_MINO_MAX = 6             # 予告ミノの最大数

# スコア
SCORE_LIST = [
    10, # 1段消し
    20, # 2段消し
    30, # 3段消し
    40  # 4段消し
]

# UI関連
GAME_BG_COLOR = "#111111"               # ゲーム背景の色
GAME_BG_LIMIT_LINE_COLOR = "#FFFFFF"    # リミットラインの色
GAME_BG_FRAME_LINE_COLOR = "#0000B4"    # フレームラインの色
GAME_BG_LIMIT_LINE_WIDTH = 1            # リミットラインの幅
GAME_BG_FRAME_LINE_WIDTH = 2            # フレームラインの幅

NEXT_MINO_SIZE = 10.0                   # 予告ミノのサイズ
NEXT_MINO_INV_Y = 40.0                  # 予告ミノの縦間隔
NEXT_MINO_LINE_LENGTH_X = 94.0          # 予告ミノの表示エリアの横幅
NEXT_MINO_TEXT_COLOR = "#FFFFFF"        # 予告ミノの「NEXT」テキスト色
NEXT_MINO_TEXT_BG_COLOR = "#0000A0"     # 予告ミノの「NEXT」テキスト背景の色
NEXT_MINO_TEXT_SIZE = 30                # 予告ミノの「NEXT」テキストサイズ
NEXT_MINO_TEXT_AREA_Y = 32.0            # 予告ミノの「NEXT」表示エリアの縦幅
NEXT_MINO_TEXT_POS = [20.0, 8.0]        # 予告ミノの「NEXT」テキスト表示位置

READY_SCREEN_BG_COLOR = "#00000020"     # READY画面の背景色
READY_TEXT_COLOR = "#FFFFFF"            # 「3・2・1」テキスト色
READY_TEXT_SIZE = 100                   # 「3・2・1」テキストサイズ

PAUSE_SCREEN_BG_COLOR = "#666666A0"     # PAUSE画面の背景色
PAUSE_TEXT_COLOR = "#FFFFFF"            #「PAUSE」テキスト色
PAUSE_TEXT_SIZE = 80                    #「PAUSE」テキストサイズ

GAME_OVER_SCREEN_BG_COLOR = "#AA0000A0" # GAME_OVER画面の背景色
GAME_OVER_TEXT_COLOR = "#000000"        #「GAME_OVER」テキスト色
GAME_OVER_TEXT_SIZE = 100               #「GAME_OVER」テキストサイズ
GAME_OVER_TEXT_MIDDLE_POS = [SCREEN_CENTER_POS[0], SCREEN_CENTER_POS[1] - 50.0]     #「GAME_OVER」テキスト中央位置

GAME_OVER_GUIDE_TEXT_COLOR = "#FFFFFF"       #「Please Enter SPACE KEY」テキスト色
GAME_OVER_GUIDE_TEXT_SIZE = 60               #「Please Enter SPACE KEY」テキストサイズ
GAME_OVER_GUIDE_TEXT_MIDDLE_POS = [SCREEN_CENTER_POS[0], SCREEN_CENTER_POS[1] + 50.0]    #「Please Enter SPACE KEY」テキスト中央位置

USER_GUIDE_FONT_SIZE = 20               # 操作説明文のテキストサイズ
USER_GUIDE_FONT_INV = 30                # 操作説明文の縦間隔
USER_GUIDE_TEXT_COLOR = "#FFFFFF"       # 操作説明文のテキスト色
USER_GUIDE_TEXT_POS = (120.0, 380.0)    # 操作説明文のテキスト位置
USER_GUIDE_TEXT = [                     # 操作説明文
    "W : ハードドロップ",
    "A : 左移動",
    "S : 下移動",
    "D : 右移動",
    "P : 一時停止",
    "→ : 右回転",
    "← : 左回転",
    "F1 : デバッグ表示"
]

SCORE_COLOR = "#FFFFFF"                 #「スコア」テキスト色
SCORE_TEXT_FONT_SIZE = 20               #「スコア」テキストサイズ
SCORE_TEXT_POS = [60.0, 80.0]           #「スコア」テキスト位置
SCORE_NUM_SIZE = 40                     # スコア点数サイズ
SCORE_NUM_RIGHT_POS = [GAME_SCREEN_OFFSET[0] - SCORE_TEXT_POS[0], 150.0]   # スコア点数右位置

COMBO_COLOR = "#FFFF00"                 # COMBOテキスト色
COMBO_FONT_SIZE = 20                    # COMBOテキストサイズ
COMBO_RIGHT_POS = [SCORE_NUM_RIGHT_POS[0], SCORE_NUM_RIGHT_POS[1] + 30.0]

# -------------------------
# ミノの設定
# -------------------------
GHOST_MINO_ALPHA = "40" # ゴーストミノのα値

# ミノの色
MINO_COLOR_STR = (
    "#000000",  # None
    "#87cefa",  # I 水
    "#ffff00",  # O 黄
    "#7cfc00",  # S 緑
    "#dc143c",  # Z 赤
    "#0000cd",  # J 青
    "#ffa500",  # L オレンジ
    "#9932cc"   # T 紫
)

# I-ミノ
MINO_I_MATRIX = [
                    [[0], [0], [0], [0]],
                    [[1], [1], [1], [1]],
                    [[0], [0], [0], [0]],
                    [[0], [0], [0], [0]]
                ],\
                [
                    [[0], [0], [1], [0]],
                    [[0], [0], [1], [0]],
                    [[0], [0], [1], [0]],
                    [[0], [0], [1], [0]]
                ],\
                [
                    [[0], [0], [0], [0]],
                    [[0], [0], [0], [0]],
                    [[1], [1], [1], [1]],
                    [[0], [0], [0], [0]]
                ],\
                [
                    [[0], [1], [0], [0]],
                    [[0], [1], [0], [0]],
                    [[0], [1], [0], [0]],
                    [[0], [1], [0], [0]]
                ]
# O-ミノ
MINO_O_MATRIX = [
                    [[0], [0], [0], [0]],
                    [[0], [1], [1], [0]],
                    [[0], [1], [1], [0]],
                    [[0], [0], [0], [0]]
                ],\
                [
                    [[0], [0], [0], [0]],
                    [[0], [1], [1], [0]],
                    [[0], [1], [1], [0]],
                    [[0], [0], [0], [0]]
                ]
# S-ミノ
MINO_S_MATRIX = [
                    [[0], [0], [0]],
                    [[0], [1], [1]],
                    [[1], [1], [0]]
                ],\
                [
                    [[1], [0], [0]],
                    [[1], [1], [0]],
                    [[0], [1], [0]]
                ],\
                [
                    [[0], [1], [1]],
                    [[1], [1], [0]],
                    [[0], [0], [0]]
                ],\
                [
                    [[0], [1], [0]],
                    [[0], [1], [1]],
                    [[0], [0], [1]]
                ]
# Z-ミノ
MINO_Z_MATRIX = [
                    [[0], [0], [0]],
                    [[1], [1], [0]],
                    [[0], [1], [1]]
                ],\
                [
                    [[0], [1], [0]],
                    [[1], [1], [0]],
                    [[1], [0], [0]]
                ],\
                [
                    [[1], [1], [0]],
                    [[0], [1], [1]],
                    [[0], [0], [0]]
                ],\
                [
                    [[0], [0], [1]],
                    [[0], [1], [1]],
                    [[0], [1], [0]]
                ]
# J-ミノ
MINO_J_MATRIX = [   
                    [[0], [0], [0]],
                    [[1], [0], [0]],
                    [[1], [1], [1]],
                    [[0], [0], [0]]
                ],\
                [
                    [[0], [0], [0]],
                    [[0], [1], [1]],
                    [[0], [1], [0]],
                    [[0], [1], [0]]
                ],\
                [
                    [[0], [0], [0]],
                    [[0], [0], [0]],
                    [[1], [1], [1]],
                    [[0], [0], [1]]
                ],\
                [
                    [[0], [0], [0]],
                    [[0], [1], [0]],
                    [[0], [1], [0]],
                    [[1], [1], [0]]
                ]
# L-ミノ
MINO_L_MATRIX = [
                    [[0], [0], [0]],
                    [[1], [1], [1]],
                    [[1], [0], [0]]
                ],\
                [
                    [[1], [1], [0]],
                    [[0], [1], [0]],
                    [[0], [1], [0]]
                ],\
                [
                    [[0], [0], [1]],
                    [[1], [1], [1]],
                    [[0], [0], [0]]
                ],\
                [
                    [[0], [1], [0]],
                    [[0], [1], [0]],
                    [[0], [1], [1]]
                ]
# T-ミノ
MINO_T_MATRIX = [   [[0], [0], [0]],
                    [[0], [1], [0]],
                    [[1], [1], [1]],
                    [[0], [0], [0]]
                ],\
                [
                    [[0], [0], [0]],
                    [[0], [1], [0]],
                    [[0], [1], [1]],
                    [[0], [1], [0]]
                ],\
                [
                    [[0], [0], [0]],
                    [[0], [0], [0]],
                    [[1], [1], [1]],
                    [[0], [1], [0]]
                ],\
                [
                    [[0], [0], [0]],
                    [[0], [1], [0]],
                    [[1], [1], [0]],
                    [[0], [1], [0]]
                ]
