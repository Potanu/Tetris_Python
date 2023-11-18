import pygame
import numpy as np
import random
from Utilities import enum
from Utilities import define
from Utilities import pygameEventManager
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
    
    def ready(self):
        self.change_state(enum.GameState.GAME)
    
    def game(self):
        self.update_mino()
        
        if False:
            self.change_state(enum.GameState.PAUSE)
            
    def pause(self):
        if pygameEventManager.PygameEventManager().is_up(enum.KeyType.S):
            self.change_state(enum.GameState.GAME_OVER)
            
    def game_over(self):
        if pygameEventManager.PygameEventManager().is_up(enum.KeyType.S):
            self.change_state(enum.GameState.END)
            
    def end(self):
        if pygameEventManager.PygameEventManager().is_up(enum.KeyType.S):
            self.change_state(enum.GameState.READY)
    
    def update_mino(self):
        if self.active_mino == None:
            self.create_mino()
            return
        
        is_fall = self.active_mino.check_fall(self.fall_speed)
        if not is_fall:
            # 降下タイミングでは無いので処理を抜ける
            return
        
        # 降下可能かチェック
        next_mino_grid = (self.active_mino.left_upper_grid[0], self.active_mino.left_upper_grid[1] + 1)
        tmp_fall_mino_matrix = self.clean_matrix()
        mino_matrix = self.active_mino.matrix[self.active_mino.index].copy()
        
        def check_fall():
            for y in reversed(range(0, len(mino_matrix))):
                for x in range(0, len(mino_matrix[0])):
                    index_x = next_mino_grid[0] + x
                    index_y = next_mino_grid[1] + y
                    if mino_matrix[y][x] == [0]:
                        continue
                    elif self.board_matrix[index_y][index_x] == 0:
                        tmp_fall_mino_matrix[index_y][index_x] = self.active_mino.mino_type
                        continue
                    return False
            return True
        
        if check_fall():
            self.active_mino.fall_mino()
            self.fall_mino_matrix = tmp_fall_mino_matrix.copy()
        else:
            self.board_matrix = np.where(self.board_matrix != 0, self.board_matrix, self.fall_mino_matrix)
            self.fall_mino_matrix = self.clean_matrix()
            self.active_mino = None
    
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
        
