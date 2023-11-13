import pygame
import numpy as np

from Utilities import enum
from Utilities import define
from Utilities import pygameEventManager
from Scenes import sceneManager

class GameManager():
    def init(self):
        self.test_index = enum.MinoType.NONE
        self.matrix = np.full((define.GRID_NUM[1], define.GRID_NUM[0]), enum.MinoType.NONE)
        self.game_state = enum.GameState.READY
        
    def update(self):
        match self.game_state:
            case enum.GameState.READY:
                print("READY")
                if pygameEventManager.PygameEventManager().is_up(enum.KeyType.W):
                    self.game_state = enum.GameState.GAME
            case enum.GameState.GAME:
                print("GAME")
            case enum.GameState.PAUSE:
                print("PAUSE")
            case enum.GameState.GAME_OVER:
                print("GAME_OVER")
            case enum.GameState.END:
                print("END")
    
        if pygameEventManager.PygameEventManager().is_up(enum.KeyType.A):
            self.test_index = enum.MinoType.NONE if self.test_index == len(enum.MinoType) - 1 else self.test_index + 1
            self.matrix = np.full((define.GRID_NUM[1], define.GRID_NUM[0]), self.test_index)
    
        self.draw()
    
    def draw(self):
        for y in range(0, len(self.matrix)):
            for x in range(0, len(self.matrix[0])):
                if self.matrix[y][x] == enum.MinoType.NONE:
                    continue
                pos_x = define.GAME_SCREEN_OFFSET[0] + define.BLOCK_SIZE[0] * x
                pos_y = define.GAME_SCREEN_OFFSET[1] + define.BLOCK_SIZE[1] * y
                block_tuple = (enum.ObjectType.OBJECT, 0, enum.DrawType.RECT, -1, define.MINO_COLOR_STR[self.test_index],
                            pygame.Rect(pos_x + 8.0, pos_y + 8.0, define.BLOCK_SIZE[0] - 16.0, define.BLOCK_SIZE[1] - 16.0), -1, -1, -1)
                sceneManager.SceneManager().add_draw_queue(block_tuple)
    
