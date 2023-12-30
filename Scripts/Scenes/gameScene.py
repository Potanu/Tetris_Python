import pygame
from Utilities import enum
from Utilities import define
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
            return
        
        self.draw()
        self.gameManager.update()
    
    def draw(self):
        grid_num_x = define.GRID_NUM[0] - 2
        grid_num_y = define.GRID_NUM[1] - 2
        offset_pos_x = define.GAME_SCREEN_OFFSET[0] + define.BLOCK_SIZE[0]
        offset_pos_y = define.GAME_SCREEN_OFFSET[1]
        
        # ゲーム部分の背景
        for y in range(0, grid_num_y):
            for x in range(0, grid_num_x):
                if x % 2 == y % 2:
                    pos_x = offset_pos_x + define.BLOCK_SIZE[0] * x
                    pos_y = offset_pos_y + define.BLOCK_SIZE[1] * y
                    bg_tuple = (enum.ObjectType.BG, 0, enum.DrawType.RECT, -1, "#111111",
                                pygame.Rect(pos_x, pos_y, define.BLOCK_SIZE[0], define.BLOCK_SIZE[1]), -1, -1, -1)
                    sceneManager.SceneManager().add_draw_queue(bg_tuple)
    
        # ゲーム部分の枠
        limit_color = "#FFFFFF"
        frame_color = "#0000B4"
        limit_width = 1
        frame_width = 2
        line_length_x = grid_num_x * define.BLOCK_SIZE[0]
        line_length_y = grid_num_y * define.BLOCK_SIZE[1]
        limit_left_pos =  (offset_pos_x, offset_pos_y + define.BLOCK_SIZE[1])
        limit_right_pos = (offset_pos_x + (grid_num_x * define.BLOCK_SIZE[0]), offset_pos_y + define.BLOCK_SIZE[1])
        left_upper_pos =  (offset_pos_x - frame_width, offset_pos_y)
        right_upper_pos = (offset_pos_x + (grid_num_x * define.BLOCK_SIZE[0]), offset_pos_y)
        left_lower_pos = (offset_pos_x - frame_width, offset_pos_y + line_length_y)
        right_lower_pos = (offset_pos_x + line_length_x, offset_pos_y + line_length_y)
        limit_line_tuple = (enum.ObjectType.BG, 0, enum.DrawType.LINE, -1, limit_color, -1, limit_left_pos, limit_right_pos, limit_width)
        line_left_tuple = (enum.ObjectType.BG, 0, enum.DrawType.LINE, -1, frame_color, -1, left_upper_pos, left_lower_pos, frame_width)
        line_right_tuple = (enum.ObjectType.BG, 0, enum.DrawType.LINE, -1, frame_color, -1, right_upper_pos, right_lower_pos, frame_width)
        line_bottom_tuple = (enum.ObjectType.BG, 0, enum.DrawType.LINE, -1, frame_color, -1, left_lower_pos, right_lower_pos, frame_width)
        sceneManager.SceneManager().add_draw_queue(limit_line_tuple)
        sceneManager.SceneManager().add_draw_queue(line_left_tuple)
        sceneManager.SceneManager().add_draw_queue(line_right_tuple)
        sceneManager.SceneManager().add_draw_queue(line_bottom_tuple)
        
        # TODO: UI
