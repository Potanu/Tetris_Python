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
        self.userGuideFont = pygame.font.Font(define.JP_FONT_PASS, define.USER_GUIDE_FONT_SIZE)
        self.scoreFont = pygame.font.Font(define.JP_FONT_PASS, define.SCORE_TEXT_FONT_SIZE)
        self.comboFont = pygame.font.Font(define.JP_FONT_PASS, define.COMBO_FONT_SIZE)
    
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
                    bg_tuple = (enum.ObjectType.BG, 0, enum.DrawType.RECT, -1, define.GAME_BG_COLOR,
                                pygame.Rect(pos_x, pos_y, define.BLOCK_SIZE[0], define.BLOCK_SIZE[1]), -1, -1, -1)
                    sceneManager.SceneManager().add_draw_queue(bg_tuple)
    
        # ゲーム部分の枠
        line_length_x = define.GAME_GRID_NUM[0] * define.BLOCK_SIZE[0]
        line_length_y = define.GAME_GRID_NUM[1] * define.BLOCK_SIZE[1]
        limit_left_pos =  (offset_pos_x, offset_pos_y + define.BLOCK_SIZE[define.GAME_OVER_GRID_Y - 1])
        limit_right_pos = (offset_pos_x + (define.GAME_GRID_NUM[0] * define.BLOCK_SIZE[0]), offset_pos_y + define.BLOCK_SIZE[define.GAME_OVER_GRID_Y - 1])
        left_upper_pos =  (offset_pos_x - define.GAME_BG_FRAME_LINE_WIDTH, offset_pos_y)
        right_upper_pos = (offset_pos_x + (define.GAME_GRID_NUM[0] * define.BLOCK_SIZE[0]), offset_pos_y)
        left_lower_pos = (offset_pos_x - define.GAME_BG_FRAME_LINE_WIDTH, offset_pos_y + line_length_y)
        right_lower_pos = (offset_pos_x + line_length_x, offset_pos_y + line_length_y)
        limit_line_tuple = (enum.ObjectType.UI, 0, enum.DrawType.LINE, -1, define.GAME_BG_LIMIT_LINE_COLOR, -1, limit_left_pos, limit_right_pos, define.GAME_BG_LIMIT_LINE_WIDTH)
        line_left_tuple = (enum.ObjectType.UI, 0, enum.DrawType.LINE, -1, define.GAME_BG_FRAME_LINE_COLOR, -1, left_upper_pos, left_lower_pos, define.GAME_BG_FRAME_LINE_WIDTH)
        line_right_tuple = (enum.ObjectType.UI, 0, enum.DrawType.LINE, -1, define.GAME_BG_FRAME_LINE_COLOR, -1, right_upper_pos, right_lower_pos, define.GAME_BG_FRAME_LINE_WIDTH)
        line_bottom_tuple = (enum.ObjectType.UI, 0, enum.DrawType.LINE, -1, define.GAME_BG_FRAME_LINE_COLOR, -1, left_lower_pos, right_lower_pos, define.GAME_BG_FRAME_LINE_WIDTH)
        sceneManager.SceneManager().add_draw_queue(limit_line_tuple)
        sceneManager.SceneManager().add_draw_queue(line_left_tuple)
        sceneManager.SceneManager().add_draw_queue(line_right_tuple)
        sceneManager.SceneManager().add_draw_queue(line_bottom_tuple)
        
        # 予告ミノ
        next_mino_start_pos = [right_upper_pos[0], right_upper_pos[1] + define.NEXT_MINO_TEXT_AREA_Y]
        mino_center_pos_x = next_mino_start_pos[0] + (define.NEXT_MINO_LINE_LENGTH_X / 2)
        next_mino_line_length_y = next_mino_start_pos[1] + (len(self.gameManager.next_mino_list) * define.NEXT_MINO_INV_Y)
       
        for index in range(0, len(self.gameManager.next_mino_list)):
            mino = self.gameManager.next_mino_list[index]
            for y in range(0, len(mino.matrix[0])):
                for x in range(0, len(mino.matrix[0][0])):
                    if mino.matrix[0][y][x] == [0]:
                        continue
                    pos_x = mino_center_pos_x - (define.NEXT_MINO_SIZE * len(mino.matrix[0][0]) / 2) + (x * define.NEXT_MINO_SIZE)
                    pos_y = next_mino_start_pos[1] + (index * define.NEXT_MINO_INV_Y) + (y * define.NEXT_MINO_SIZE)
                    next_mino_tuple = (enum.ObjectType.UI, 0, enum.DrawType.RECT, -1, define.MINO_COLOR_STR[mino.mino_type],
                                pygame.Rect(pos_x + 1, pos_y + 1, define.NEXT_MINO_SIZE - 2, define.NEXT_MINO_SIZE - 2), -1, -1, -1)
                    sceneManager.SceneManager().add_draw_queue(next_mino_tuple)
        
        next_mino_frame_up_tuple = (enum.ObjectType.UI, 0, enum.DrawType.LINE, -1, define.GAME_BG_FRAME_LINE_COLOR, -1,
                                    right_upper_pos,
                                    (right_upper_pos[0] + define.NEXT_MINO_LINE_LENGTH_X, right_upper_pos[1]),
                                    define.GAME_BG_FRAME_LINE_WIDTH)
        next_mino_frame_down_tuple = (enum.ObjectType.UI, 0, enum.DrawType.LINE, -1, define.GAME_BG_FRAME_LINE_COLOR, -1,
                                    (next_mino_start_pos[0], right_upper_pos[1] + next_mino_line_length_y),
                                    (next_mino_start_pos[0] + define.NEXT_MINO_LINE_LENGTH_X, right_upper_pos[1] + next_mino_line_length_y),
                                    define.GAME_BG_FRAME_LINE_WIDTH)
        next_mino_frame_right_tuple = (enum.ObjectType.UI, 0, enum.DrawType.LINE, -1, define.GAME_BG_FRAME_LINE_COLOR, -1,
                                    (next_mino_start_pos[0] + define.NEXT_MINO_LINE_LENGTH_X, right_upper_pos[1]),
                                    (next_mino_start_pos[0] + define.NEXT_MINO_LINE_LENGTH_X, right_upper_pos[1] + next_mino_line_length_y),
                                    define.GAME_BG_FRAME_LINE_WIDTH)
        next_mino_text_bg_tuple = (enum.ObjectType.BG, 0, enum.DrawType.RECT, -1, define.NEXT_MINO_TEXT_BG_COLOR,
                                    pygame.Rect(right_upper_pos[0], right_upper_pos[1],
                                                define.NEXT_MINO_LINE_LENGTH_X, define.NEXT_MINO_TEXT_AREA_Y),
                                    -1, -1, -1)
        font = pygame.font.Font(None, define.NEXT_MINO_TEXT_SIZE)
        gTxt = font.render("NEXT", True, define.NEXT_MINO_TEXT_COLOR)
        text_tuple = (enum.ObjectType.UI, 0, enum.DrawType.TEXT, gTxt, -1, -1,
                      (next_mino_start_pos[0] + define.NEXT_MINO_TEXT_POS[0], define.NEXT_MINO_TEXT_POS[1]), -1, -1)
        sceneManager.SceneManager().add_draw_queue(next_mino_frame_up_tuple)
        sceneManager.SceneManager().add_draw_queue(next_mino_frame_down_tuple)
        sceneManager.SceneManager().add_draw_queue(next_mino_frame_right_tuple)
        sceneManager.SceneManager().add_draw_queue(next_mino_text_bg_tuple)
        sceneManager.SceneManager().add_draw_queue(text_tuple)
        
        # 操作説明
        index = 0
        for text in define.USER_GUIDE_TEXT:
            gTxt = self.userGuideFont.render(text, True, define.USER_GUIDE_TEXT_COLOR)
            text_tuple = (enum.ObjectType.UI, 0, enum.DrawType.TEXT, gTxt, -1, -1,
                      (define.USER_GUIDE_TEXT_POS[0], define.USER_GUIDE_TEXT_POS[1] + (index * define.USER_GUIDE_FONT_INV)), -1, -1)
            sceneManager.SceneManager().add_draw_queue(text_tuple)
            index += 1
        
        # スコア表示
        gTxt = self.scoreFont.render("スコア", True, define.SCORE_COLOR)
        text_tuple = (enum.ObjectType.UI, 0, enum.DrawType.TEXT, gTxt, -1, -1,
                      define.SCORE_TEXT_POS, -1, -1)
        sceneManager.SceneManager().add_draw_queue(text_tuple)
        
        font = pygame.font.Font(None, define.SCORE_NUM_SIZE)
        gTxt = font.render(str(self.gameManager.score), True, define.SCORE_COLOR)
        text_rect = gTxt.get_rect(bottomright=define.SCORE_NUM_RIGHT_POS)
        text_tuple = (enum.ObjectType.UI, 0, enum.DrawType.TEXT, gTxt, -1, -1,
                      text_rect, -1, -1)
        sceneManager.SceneManager().add_draw_queue(text_tuple)
        
        # コンボ表示
        if self.gameManager.combo > 1:
            combo = self.gameManager.combo - 1
            gTxt = self.comboFont.render("★COMBO " + str(combo), True, define.COMBO_COLOR)
            text_rect = gTxt.get_rect(bottomright=define.COMBO_RIGHT_POS)
            text_tuple = (enum.ObjectType.UI, 0, enum.DrawType.TEXT, gTxt, -1, -1,
                        text_rect, -1, -1)
            sceneManager.SceneManager().add_draw_queue(text_tuple)
        
        
