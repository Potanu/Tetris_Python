import pygame

from Utilities import enum
from Utilities import define
from Utilities import pygameEventManager
from Scenes import sceneBase
from Scenes import sceneManager
from Scenes import gameManager

class GameScene(sceneBase.SceneBase):
    def __init__(self):
        self.gameManager = gameManager.GameManager()
        self.gameManager.init()
    
    def update(self):
        if self.gameManager.game_state == enum.GameState.END:
            sceneManager.SceneManager().move_Scene(enum.SceneType.TITLE)
        
        self.draw()
        self.gameManager.update()
    
    def draw(self):
        # 背景のクリア
        screen_clear_tuple = (enum.ObjectType.BG, 0, enum.DrawType.FILL, -1, "#000000", -1, -1, -1, -1)
        sceneManager.SceneManager().add_draw_queue(screen_clear_tuple)
        
        # ゲーム部分の背景
        for y in range(0, define.GRID_NUM[1]):
            for x in range(0, define.GRID_NUM[0]):
                if x % 2 == y % 2:
                    pos_x = define.GAME_SCREEN_OFFSET[0] + define.BLOCK_SIZE[0] * x
                    pos_y = define.GAME_SCREEN_OFFSET[1] + define.BLOCK_SIZE[1] * y
                    bg_tuple = (enum.ObjectType.BG, 0, enum.DrawType.RECT, -1, "#111111",
                                pygame.Rect(pos_x, pos_y, define.BLOCK_SIZE[0], define.BLOCK_SIZE[1]), -1, -1, -1)
                    sceneManager.SceneManager().add_draw_queue(bg_tuple)
    
        # ゲーム部分の枠
        frame_color = (0, 0, 180)
        line_width = 1
        line_length_x = define.GRID_NUM[0] * define.BLOCK_SIZE[0]
        line_length_y = define.GRID_NUM[1] * define.BLOCK_SIZE[1]
        left_upper_pos =  (define.GAME_SCREEN_OFFSET[0], define.GAME_SCREEN_OFFSET[1])
        right_upper_pos = (define.GAME_SCREEN_OFFSET[0] + (define.GRID_NUM[0] * define.BLOCK_SIZE[0]), define.GAME_SCREEN_OFFSET[1])
        left_lower_pos = (define.GAME_SCREEN_OFFSET[0], define.GAME_SCREEN_OFFSET[1] + line_length_y)
        right_lower_pos = (define.GAME_SCREEN_OFFSET[0] + line_length_x, define.GAME_SCREEN_OFFSET[1] + line_length_y)
        line_up_tuple = (enum.ObjectType.BG, 0, enum.DrawType.LINE, -1, frame_color, -1, left_upper_pos, right_upper_pos, line_width)
        line_left_tuple = (enum.ObjectType.BG, 0, enum.DrawType.LINE, -1, frame_color, -1, left_upper_pos, left_lower_pos, line_width)
        line_right_tuple = (enum.ObjectType.BG, 0, enum.DrawType.LINE, -1, frame_color, -1, right_upper_pos, right_lower_pos, line_width)
        line_bottom_tuple = (enum.ObjectType.BG, 0, enum.DrawType.LINE, -1, frame_color, -1, left_lower_pos, right_lower_pos, line_width)
        sceneManager.SceneManager().add_draw_queue(line_up_tuple)
        sceneManager.SceneManager().add_draw_queue(line_left_tuple)
        sceneManager.SceneManager().add_draw_queue(line_right_tuple)
        sceneManager.SceneManager().add_draw_queue(line_bottom_tuple)
        
        # TODO: UI
