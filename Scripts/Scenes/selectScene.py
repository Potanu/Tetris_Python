import pygame
from Utilities import enum
from Utilities import define
from Utilities import pygameManager
from Scenes import sceneBase
from Scenes import sceneManager

class SelectScene(sceneBase.SceneBase):
    def __init__(self):
        self.font = pygame.font.Font(define.JP_FONT_PASS, define.SELECT_TEXT_SIZE)
    
    def update(self):
        if (pygameManager.PygameManager().is_pressed(pygame.K_w)):
            sceneManager.SceneManager().move_Scene(enum.SceneType.GAME)
        elif (pygameManager.PygameManager().is_pressed(pygame.K_s)):
            pass
            
        self.draw()
        
    def draw(self):
        # 背景
        bg_tuple = (enum.ObjectType.BG, 0, enum.DrawType.FILL, -1, define.SELECT_BG_COLOR, -1, -1, 1, -1)
        sceneManager.SceneManager().add_draw_queue(bg_tuple)
        
        # 操作説明
        index = 0
        for text in define.SELECT_TEXT:
            gTxt = self.font.render(text, True, define.SELECT_TEXT_COLOR)
            text_tuple = (enum.ObjectType.UI, 0, enum.DrawType.TEXT, gTxt, -1, -1,
                      (define.SELECT_TEXT_POS[0], define.SELECT_TEXT_POS[1] + (index * (define.SELECT_TEXT_SIZE * 2))), -1, -1)
            sceneManager.SceneManager().add_draw_queue(text_tuple)
            index += 1
