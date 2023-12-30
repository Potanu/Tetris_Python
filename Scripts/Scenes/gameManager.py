import pygame
import numpy as np
import random
from Utilities import enum
from Utilities import define
from Utilities import pygameManager
from Scenes import sceneManager
from Objects import mino

class GameManager:
    def init(self):
        self.active_mino = None     # 降下中のミノ
        self.fall_speed = define.DEFAULT_FALL_SPEED # ミノの降下速度
        self.level = 1  # レベル
        self.board_matrix = self.clean_matrix()
        self.fall_mino_matrix = self.board_matrix.copy()
        self.board_matrix[-1, :] = -1   # 下辺の透明ブロック
        self.board_matrix[:,  0] = -1   # 左辺の透明ブロック
        self.board_matrix[:, -1] = -1   # 右辺の透明ブロック
        self.change_state(enum.GameState.READY)
        
    def update(self):
        self.active_func()
        self.draw()
        # self.draw_debug() # ブロックマスへのデバッグ表記（FPSがかなり落ちるので基本オフにしておく）
    
    def ready(self):
        self.change_state(enum.GameState.GAME)
    
    def game(self):
        self.update_mino()
        
        if False:
            self.change_state(enum.GameState.PAUSE)
            
    def pause(self):
        if pygameManager.PygameManager().is_up(enum.KeyType.P):
            self.change_state(enum.GameState.GAME)
            return
        
        fill_tuple = (enum.ObjectType.UI, 0, enum.DrawType.FILL, -1, "#666666A0", -1, -1, -1, -1)
        sceneManager.SceneManager().add_draw_queue(fill_tuple)
        font = pygame.font.Font(None, 80)
        gTxt = font.render("PAUSE", True, "#FFFFFF")
        start_pos = [406.0, 280.0]
        text_tuple = (enum.ObjectType.UI, 1, enum.DrawType.TEXT, gTxt, -1, -1, start_pos, -1, -1)
        sceneManager.SceneManager().add_draw_queue(text_tuple)
        
    def game_over(self):
        if pygameManager.PygameManager().is_up(enum.KeyType.S):
            self.change_state(enum.GameState.END)
            
    def end(self):
        if pygameManager.PygameManager().is_up(enum.KeyType.S):
            self.change_state(enum.GameState.READY)
    
    def update_mino(self):
        if self.active_mino == None:
            self.create_mino()
            return
        
        self.check_key_input()
        self.fall_mino()
    
    def check_key_input(self):
        if (pygameManager.PygameManager().is_up(enum.KeyType.P)):
            # ゲーム一時停止
            self.change_state(enum.GameState.PAUSE)
            return
        
        if (pygameManager.PygameManager().is_up(enum.KeyType.D)
            or pygameManager.PygameManager().is_up(enum.KeyType.RIGHT)):
            next_mino_grid = (self.active_mino.left_upper_grid[0] + 1, self.active_mino.left_upper_grid[1])
            if self.check_object(self.active_mino.matrix[self.active_mino.index], next_mino_grid):
                # 右移動
                self.active_mino.move_mino(enum.MinoMoveType.MOVE_RIGHT)
                self.update_fall_mino_matrix()
        elif (pygameManager.PygameManager().is_up(enum.KeyType.A)
            or pygameManager.PygameManager().is_up(enum.KeyType.LEFT)):
            next_mino_grid = (self.active_mino.left_upper_grid[0] - 1, self.active_mino.left_upper_grid[1])
            if self.check_object(self.active_mino.matrix[self.active_mino.index], next_mino_grid):
                # 左移動
                self.active_mino.move_mino(enum.MinoMoveType.MOVE_LEFT)
                self.update_fall_mino_matrix()
        elif pygameManager.PygameManager().is_up(enum.KeyType.E):
            if self.check_object(self.active_mino.matrix[self.active_mino.get_next_index(1)], self.active_mino.left_upper_grid):
                # 右回転
                self.active_mino.move_mino(enum.MinoMoveType.ROTATE_RIGHT)
                self.update_fall_mino_matrix()
        elif pygameManager.PygameManager().is_up(enum.KeyType.Q):
            if self.check_object(self.active_mino.matrix[self.active_mino.get_next_index(-1)], self.active_mino.left_upper_grid):
                # 左回転
                self.active_mino.move_mino(enum.MinoMoveType.ROTATE_LEFT)
                self.update_fall_mino_matrix()
    
    # ミノの降下処理
    def fall_mino(self):
        # 降下速度を取得
        is_press_down = pygameManager.PygameManager().is_pressed(enum.KeyType.S) or \
            pygameManager.PygameManager().is_pressed(enum.KeyType.DOWN)
        fall_speed = define.FALL_HIGH_SPEED if is_press_down else self.fall_speed
        
        if not self.active_mino.check_fall(fall_speed):
            # 降下タイミングでは無いので処理を抜ける
            return
        
        # 降下可能かチェック
        next_mino_grid = (self.active_mino.left_upper_grid[0], self.active_mino.left_upper_grid[1] + 1)
        if self.check_object(self.active_mino.matrix[self.active_mino.index], next_mino_grid):
            # 降下
            self.active_mino.move_mino(enum.MinoMoveType.FALL)
            self.update_fall_mino_matrix()
        else:
            # 接地
            self.board_matrix = np.where(self.board_matrix != 0, self.board_matrix, self.fall_mino_matrix)
            self.fall_mino_matrix = self.clean_matrix()
            self.active_mino = None
    
    # 当たり判定チェック(なければTrue)
    def check_object(self, next_mino_matrix, next_mino_grid):
        for y in reversed(range(0, len(next_mino_matrix))):
            for x in range(0, len(next_mino_matrix[0])):
                index_x = next_mino_grid[0] + x
                index_y = next_mino_grid[1] + y
                if next_mino_matrix[y][x] == [0] or self.board_matrix[index_y][index_x] == 0:
                    continue
                return False
        return True
    
    # 降下中ミノの情報更新
    def update_fall_mino_matrix(self):
        self.fall_mino_matrix = self.clean_matrix()
        mino_matrix = self.active_mino.matrix[self.active_mino.index].copy()
        for y in reversed(range(0, len(mino_matrix))):
            for x in range(0, len(mino_matrix[0])):
                index_x = self.active_mino.left_upper_grid[0] + x
                index_y = self.active_mino.left_upper_grid[1] + y
                if mino_matrix[y][x] == [0]:
                    continue
                self.fall_mino_matrix[index_y][index_x] = self.active_mino.mino_type
    
    def clean_matrix(self):
        return np.full((define.GRID_NUM[1], define.GRID_NUM[0]), enum.MinoType.NONE)
    
    def create_mino(self):
        type = random.randint(enum.MinoType.NONE + 1, len(enum.MinoType) - 1)
        self.active_mino = mino.Mino(type)
        mino_matrix = self.active_mino.matrix[self.active_mino.index].copy()
        for y in range(0, len(mino_matrix)):
            for x in range(0, len(mino_matrix[0])):
                if mino_matrix[y][x] == [0]:
                    continue
                index_x = self.active_mino.left_upper_grid[0] + x
                index_y = self.active_mino.left_upper_grid[1] + y
                self.fall_mino_matrix[index_y][index_x] = self.active_mino.mino_type
    
    def change_state(self, next_state):
        match next_state:
            case enum.GameState.READY:
                self.active_func = self.ready
                print("READY")
            case enum.GameState.GAME:
                self.active_func = self.game
                print("GAME")
            case enum.GameState.PAUSE:
                self.active_func = self.pause
                print("PAUSE")
            case enum.GameState.GAME_OVER:
                self.active_func = self.game_over
                print("GAME_OVER")
            case enum.GameState.END:
                self.active_func = self.end
                print("END")       
        self.game_state = next_state
    
    def draw(self):
        def draw_matrix(matrix):
            for y in range(0, len(matrix)):
                for x in range(0, len(matrix[0])):
                    mino_type = matrix[y][x]
                    if mino_type <= enum.MinoType.NONE:
                        continue
                    pos_x = define.GAME_SCREEN_OFFSET[0] + define.BLOCK_SIZE[0] * x
                    pos_y = define.GAME_SCREEN_OFFSET[1] + define.BLOCK_SIZE[1] * y - define.BLOCK_SIZE[1]
                    block_tuple = (enum.ObjectType.OBJECT, 0, enum.DrawType.RECT, -1, define.MINO_COLOR_STR[mino_type],
                                pygame.Rect(pos_x + 1, pos_y + 1, define.BLOCK_SIZE[0] - 2, define.BLOCK_SIZE[1] - 2), -1, -1, -1)
                    sceneManager.SceneManager().add_draw_queue(block_tuple)
                
        draw_matrix(self.board_matrix)
        draw_matrix(self.fall_mino_matrix)
    
    # ブロックマスへのデバッグ表記
    def draw_debug(self):
        if not sceneManager.SceneManager().is_debug:
            return
        def draw_matrix(matrix, pos):
            font = pygame.font.Font(None, 12)
            for y in range(0, len(matrix)):
                for x in range(0, len(matrix[0])):
                    color = "#000000" if 0 < matrix[y][x] else "#FFFFFF"
                    gTxt = font.render(str(matrix[y][x]), True, color)
                    start_pos = [define.GAME_SCREEN_OFFSET[0] + (x * define.BLOCK_SIZE[0]) + pos[0],
                                 define.GAME_SCREEN_OFFSET[1] + ((y - 1) * define.BLOCK_SIZE[1]) + pos[1]]
                    text_tuple = (enum.ObjectType.DEBUG, 0, enum.DrawType.TEXT, gTxt, -1, -1, start_pos, -1, -1)
                    sceneManager.SceneManager().add_draw_queue(text_tuple)
        
        draw_matrix(self.board_matrix, (4, 22.0))
        draw_matrix(self.fall_mino_matrix, (24.0, 22.0))
