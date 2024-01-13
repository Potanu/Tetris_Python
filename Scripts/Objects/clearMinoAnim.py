import pygame
from Utilities import define
from Utilities import enum
from Scenes import sceneManager

class ClearMinoAnim():
    def set_data(self, grid):
        self.pos = (define.GAME_SCREEN_OFFSET[0] + (grid[0] * define.BLOCK_SIZE[0]),
                    define.GAME_SCREEN_OFFSET[1] + (grid[1] * define.BLOCK_SIZE[1]) - define.BLOCK_SIZE[1])
        self.counter = 255
        self.is_end_anim = False
    
    def update(self):
        if self.is_end_anim:
            return
        
        if self.counter == 0:
            self.is_end_anim = True
            return
        
        if 0 < self.counter:
            self.counter -= define.CLEAR_LINE_ANIM_SPEED
            if self.counter < 0:
                self.counter = 0
        else:
            self.counter = 0
        
        self.draw()
        
    def draw(self):
        color = (255, 255, 255, self.counter)
        block_tuple = (enum.ObjectType.OBJECT, 0, enum.DrawType.RECT_ALPHA, -1, color,
                    pygame.Rect(self.pos[0], self.pos[1], define.BLOCK_SIZE[0], define.BLOCK_SIZE[1]), -1, -1, -1)
        sceneManager.SceneManager().add_draw_queue(block_tuple)
