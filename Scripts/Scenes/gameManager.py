import pygame
import numpy as np

from Utilities import enum
from Utilities import define
from Utilities import pygameEventManager
from Scenes import sceneManager
from Objects import mino

class GameManager:
    def init(self):
        self.matrix = np.full((define.GRID_NUM[1], define.GRID_NUM[0]), enum.MinoType.NONE)
        self.change_state(enum.GameState.READY)
        self.test_index = 0
        self.test_mino = mino.Mino(enum.MinoType.I)
        
    def update(self):
        self.active_func()
        self.draw()
    
    def ready(self):
        self.change_state(enum.GameState.GAME)
    
    def game(self):
        self.test()
        
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
        for y in range(0, len(self.matrix)):
            for x in range(0, len(self.matrix[0])):
                mino_type = self.matrix[y][x]
                if mino_type == enum.MinoType.NONE:
                    continue
                pos_x = define.GAME_SCREEN_OFFSET[0] + define.BLOCK_SIZE[0] * x
                pos_y = define.GAME_SCREEN_OFFSET[1] + define.BLOCK_SIZE[1] * y
                block_tuple = (enum.ObjectType.OBJECT, 0, enum.DrawType.RECT, -1, define.MINO_COLOR_STR[mino_type],
                            pygame.Rect(pos_x + 4.0, pos_y + 4.0, define.BLOCK_SIZE[0] - 8.0, define.BLOCK_SIZE[1] - 8.0), -1, -1, -1)
                sceneManager.SceneManager().add_draw_queue(block_tuple)
    
    # TODO: あとでけす
    def test(self):
        type = enum.MinoType.NONE
        if pygameEventManager.PygameEventManager().is_up(enum.KeyType.W):
            type = enum.MinoType.I
        elif pygameEventManager.PygameEventManager().is_up(enum.KeyType.A):
            type = enum.MinoType.O
        elif pygameEventManager.PygameEventManager().is_up(enum.KeyType.S):
            type = enum.MinoType.S
        elif pygameEventManager.PygameEventManager().is_up(enum.KeyType.D):
            type = enum.MinoType.Z
        elif pygameEventManager.PygameEventManager().is_up(enum.KeyType.LEFT):
            type = enum.MinoType.J
        elif pygameEventManager.PygameEventManager().is_up(enum.KeyType.UP):
            type = enum.MinoType.L
        elif pygameEventManager.PygameEventManager().is_up(enum.KeyType.RIGHT):
            type = enum.MinoType.T
        
        if type == enum.MinoType.NONE:
            return
        
        if self.test_mino.mino_type == type:
            self.test_mino.rotate_right()
        else:
            self.test_mino = mino.Mino(type)
        
        self.matrix = np.full((define.GRID_NUM[1], define.GRID_NUM[0]), enum.MinoType.NONE)
        y_index = 0
        for y in range(10, 10 + len(self.test_mino.matrix[0])):
            x_index = 0
            for x in range(5, 5 + len(self.test_mino.matrix[0][0])):
                if self.test_mino.matrix[self.test_mino.index][y_index][x_index] != [0]:
                    self.matrix[y][x] = type
                x_index = x_index + 1
            y_index = y_index + 1
