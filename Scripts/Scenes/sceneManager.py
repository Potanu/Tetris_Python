import pygame
import time
from pygame.locals import *
from Utilities import singleton
from Utilities import enum
from Utilities import define
from Utilities import pygameEventManager
from Scenes import titleScene
from Scenes import gameScene

class SceneManager(singleton.Singleton):
  def init(self):
    pygame.init()
    self.screen = pygame.display.set_mode(define.SCREEN_SIZE)
    pygame.display.set_caption(u"タイトル")
    
    self.draw_queue = []
    now_time = time.time()
    self.fps_starttime = now_time
    self.fps_count = 0
    self.fps_view = 0
    self.active_scene = gameScene.GameScene()
    self.is_debug = False
    self.debug_text_count = 0
    
  def run(self):
    while True:
      pygameEventManager.PygameEventManager().get_events()
      if pygameEventManager.PygameEventManager().get_event(QUIT):
          break
      
      # 画面更新
      self.active_scene.update()
      self.debug()  # デバッグ関連の処理
      self.draw()
      # FPSの固定
      pygame.time.Clock().tick(define.FPS)
    # アプリケーション終了
    pygame.quit()
      
  def draw(self):
    self.draw_queue.sort(key = lambda x: (x[enum.DrawData.OBJECT_TYPE], x[enum.DrawData.Z_ORDER]))
    for data in self.draw_queue:
      object_type, z_order, draw_type, image, color, rect, start_pos, end_pos, width = data
      match draw_type:
        case enum.DrawType.TEXT:
          self.screen.blit(image, start_pos) 
        case enum.DrawType.RECT:
          pygame.draw.rect(self.screen, color, rect)
        case enum.DrawType.LINE:
          pygame.draw.line(self.screen, color, start_pos, end_pos, width) 
        case enum.DrawType.FILL:
          self.screen.fill(color)
    pygame.display.flip()
    self.draw_queue.clear()
    self.debug_text_count = 0
  
  def add_draw_queue(self, tuple):
    self.draw_queue.append(tuple)
  
  def move_Scene(self, type):
    self.active_scene = self.get_scene(type)
      
  def get_scene(self, type):
    match type:
      case enum.SceneType.TITLE:
        return titleScene.TitleScene()
      case enum.SceneType.GAME:
        return gameScene.GameScene()
    
  def debug(self):
    if pygameEventManager.PygameEventManager().is_up(enum.KeyType.DEBUG):
      self.is_debug = not self.is_debug
    
    # FPS表示
    fps_endtime = time.time()
    if 1.0 <= (fps_endtime - self.fps_starttime):
      self.fps_view = self.fps_count
      self.fps_count = 0
      self.fps_starttime = fps_endtime
    else:
      self.fps_count += 1
    
    if not self.is_debug:
      return
    
    self.add_debug_text(f"fps={self.fps_view}")
  
  def add_debug_text(self, text):
      font = pygame.font.Font(None, 40)
      gTxt = font.render(text, True, "#FFFFFF")
      start_pos = [0.0, 30.0 * self.debug_text_count]
      text_tuple = (enum.ObjectType.DEBUG, 0, enum.DrawType.TEXT, gTxt, -1, -1, start_pos, -1, -1)
      self.add_draw_queue(text_tuple)
      self.debug_text_count += 1
