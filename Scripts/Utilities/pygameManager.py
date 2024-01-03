import pygame
from Utilities import singleton

class PygameManager(singleton.Singleton):
    # イベントの取得（メインループの最初に呼ぶ）
    def get_events(self):
        self.event_list = pygame.event.get()
    
    def get_event(self, type):
        for event in self.event_list:
            if event.type == type:
                return True
        return False
    
    # キーを押下した瞬間かどうか
    def is_down(self, key_type):
        for event in self.event_list:
            if event.type == pygame.KEYDOWN:
                return event.key == key_type
      
    # キーを押下し続けているかどうか
    def is_pressed(self, key_type):
        keys = pygame.key.get_pressed()
        return keys[key_type]
    
    # キーを離した瞬間かどうか
    def is_up(self, key_type):
        for event in self.event_list:
            if event.type == pygame.KEYUP:
                return event.key == key_type
