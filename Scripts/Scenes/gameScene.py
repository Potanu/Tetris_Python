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
        
        self.gameManager.update()
        self.draw()
    
    def draw(self):
        offset_pos_x = define.GAME_SCREEN_OFFSET[0] + define.BLOCK_SIZE[0]
        offset_pos_y = define.GAME_SCREEN_OFFSET[1]
        
        # ゲーム部分の背景
        for y in range(0, define.GAME_GRID_NUM[1]):
            for x in range(0, define.GAME_GRID_NUM[0]):
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
        line_length_x = define.GAME_GRID_NUM[0] * define.BLOCK_SIZE[0]
        line_length_y = define.GAME_GRID_NUM[1] * define.BLOCK_SIZE[1]
        limit_left_pos =  (offset_pos_x, offset_pos_y + define.BLOCK_SIZE[1])
        limit_right_pos = (offset_pos_x + (define.GAME_GRID_NUM[0] * define.BLOCK_SIZE[0]), offset_pos_y + define.BLOCK_SIZE[1])
        left_upper_pos =  (offset_pos_x - frame_width, offset_pos_y)
        right_upper_pos = (offset_pos_x + (define.GAME_GRID_NUM[0] * define.BLOCK_SIZE[0]), offset_pos_y)
        left_lower_pos = (offset_pos_x - frame_width, offset_pos_y + line_length_y)
        right_lower_pos = (offset_pos_x + line_length_x, offset_pos_y + line_length_y)
        limit_line_tuple = (enum.ObjectType.UI, 0, enum.DrawType.LINE, -1, limit_color, -1, limit_left_pos, limit_right_pos, limit_width)
        line_left_tuple = (enum.ObjectType.UI, 0, enum.DrawType.LINE, -1, frame_color, -1, left_upper_pos, left_lower_pos, frame_width)
        line_right_tuple = (enum.ObjectType.UI, 0, enum.DrawType.LINE, -1, frame_color, -1, right_upper_pos, right_lower_pos, frame_width)
        line_bottom_tuple = (enum.ObjectType.UI, 0, enum.DrawType.LINE, -1, frame_color, -1, left_lower_pos, right_lower_pos, frame_width)
        sceneManager.SceneManager().add_draw_queue(limit_line_tuple)
        sceneManager.SceneManager().add_draw_queue(line_left_tuple)
        sceneManager.SceneManager().add_draw_queue(line_right_tuple)
        sceneManager.SceneManager().add_draw_queue(line_bottom_tuple)
        
        # 予告ミノ
        size = 10.0
        next_mino_inv_y = 40.0
        next_mino_line_length_x = 94.0
        next_mino_text_area_y = 32.0
        next_mino_start_pos = [right_upper_pos[0], right_upper_pos[1] + next_mino_text_area_y]
        mino_center_pos_x = next_mino_start_pos[0] + (next_mino_line_length_x / 2)
        next_mino_line_length_y = next_mino_start_pos[1] + (len(self.gameManager.next_mino_list) * next_mino_inv_y)
       
        for index in range(0, len(self.gameManager.next_mino_list)):
            mino = self.gameManager.next_mino_list[index]
            for y in range(0, len(mino.matrix[0])):
                for x in range(0, len(mino.matrix[0][0])):
                    if mino.matrix[0][y][x] == [0]:
                        continue
                    pos_x = mino_center_pos_x - (size * len(mino.matrix[0][0]) / 2) + (x * size)
                    pos_y = next_mino_start_pos[1] + (index * next_mino_inv_y) + (y * size)
                    next_mino_tuple = (enum.ObjectType.UI, 0, enum.DrawType.RECT, -1, define.MINO_COLOR_STR[mino.mino_type],
                                pygame.Rect(pos_x + 1, pos_y + 1, size - 2, size - 2), -1, -1, -1)
                    sceneManager.SceneManager().add_draw_queue(next_mino_tuple)
        
        next_mino_frame_up_tuple = (enum.ObjectType.UI, 0, enum.DrawType.LINE, -1, frame_color, -1,
                                    right_upper_pos,
                                    (right_upper_pos[0] + next_mino_line_length_x, right_upper_pos[1]),
                                    frame_width)
        next_mino_frame_down_tuple = (enum.ObjectType.UI, 0, enum.DrawType.LINE, -1, frame_color, -1,
                                    (next_mino_start_pos[0], right_upper_pos[1] + next_mino_line_length_y),
                                    (next_mino_start_pos[0] + next_mino_line_length_x, right_upper_pos[1] + next_mino_line_length_y),
                                    frame_width)
        next_mino_frame_right_tuple = (enum.ObjectType.UI, 0, enum.DrawType.LINE, -1, frame_color, -1,
                                    (next_mino_start_pos[0] + next_mino_line_length_x, right_upper_pos[1]),
                                    (next_mino_start_pos[0] + next_mino_line_length_x, right_upper_pos[1] + next_mino_line_length_y),
                                    frame_width)
        next_mino_text_bg_tuple = (enum.ObjectType.BG, 0, enum.DrawType.RECT, -1, "#0000A0",
                                    pygame.Rect(right_upper_pos[0], right_upper_pos[1],
                                                next_mino_line_length_x, next_mino_text_area_y),
                                    -1, -1, -1)
        font = pygame.font.Font(None, 30)
        gTxt = font.render("NEXT", True, "#FFFFFF")
        text_tuple = (enum.ObjectType.UI, 0, enum.DrawType.TEXT, gTxt, -1, -1,
                      (next_mino_start_pos[0] + 20.0, 8.0), -1, -1)
        sceneManager.SceneManager().add_draw_queue(next_mino_frame_up_tuple)
        sceneManager.SceneManager().add_draw_queue(next_mino_frame_down_tuple)
        sceneManager.SceneManager().add_draw_queue(next_mino_frame_right_tuple)
        sceneManager.SceneManager().add_draw_queue(next_mino_text_bg_tuple)
        sceneManager.SceneManager().add_draw_queue(text_tuple)
        # TODO: 他UI
