import pygame
from pygame.locals import *
from Utilities import singleton
from Utilities import enum
from Utilities import define
from Utilities import pygameManager
from Scenes import titleScene
from Scenes import gameScene

class SceneManager(singleton.Singleton):
  def init(self):
    pygame.init()
    self.screen = pygame.display.set_mode(define.SCREEN_SIZE)
    pygame.display.set_caption(u"タイトル")
    
    self.draw_queue = []
    self.active_scene = gameScene.GameScene()
    self.is_debug = False
    self.debug_text_count = 0           # デバッグ表示項目が複数行に渡る場合のカウンター
    self.old_elapsed_time = 0           # 経過時間保存用（/millseconds)
    self.fps_view_update_counter = 0    # fps表示更新用カウンター
    
  def run(self):
    while True:
      pygameManager.PygameManager().get_events()
      if pygameManager.PygameManager().get_event(QUIT):
          break
      
      # 画面更新
      self.active_scene.update()
      self.draw()
      
       # デバッグモード切替チェック
      if pygameManager.PygameManager().is_up(enum.KeyType.DEBUG):
        self.is_debug = not self.is_debug
      
      # FPSの固定
      self.set_frame_rate()
      
    # アプリケーション終了
    pygame.quit()
      
  def draw(self):
    self.screen.fill("#000000") # 画面のクリア
    self.draw_queue.sort(key = lambda x: (x[enum.DrawData.OBJECT_TYPE], x[enum.DrawData.Z_ORDER]))
    for data in self.draw_queue:
      object_type, z_order, draw_type, image, color, rect, start_pos, end_pos, width = data
      match draw_type:
        case enum.DrawType.TEXT:
          self.screen.blit(image, start_pos) 
        case enum.DrawType.RECT:
          pygame.draw.rect(self.screen, color, rect)
        case enum.DrawType.RECT_ALPHA:
          surface = pygame.Surface(rect.size, pygame.SRCALPHA)
          surface.fill(color)
          self.screen.blit(surface, rect)
        case enum.DrawType.LINE:
          pygame.draw.line(self.screen, color, start_pos, end_pos, width) 
        case enum.DrawType.FILL:
          surface = pygame.Surface(define.SCREEN_SIZE, pygame.SRCALPHA)
          surface.fill(color)
          self.screen.blit(surface, (0, 0))
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
  
  def set_frame_rate(self):
    elapsed_time = pygame.time.Clock().tick(define.FPS) # millsecond で返ってくる
    self.fps_view_update_counter += elapsed_time
    
    if self.is_debug:
      if self.fps_view_update_counter > 500:
        # 0.5秒おきに更新する
        fps = 1000 / elapsed_time
        self.old_elapsed_time = elapsed_time
        self.fps_view_update_counter = 0
      else:
        fps = 1000 / self.old_elapsed_time
      
      self.add_debug_text(f"FPS : {round(fps)}")
  
  def add_debug_text(self, text):
      font = pygame.font.Font(None, 40)
      gTxt = font.render(text, True, "#FFFFFF")
      start_pos = [0.0, 30.0 * self.debug_text_count]
      text_tuple = (enum.ObjectType.DEBUG, 0, enum.DrawType.TEXT, gTxt, -1, -1, start_pos, -1, -1)
      self.add_draw_queue(text_tuple)
      self.debug_text_count += 1
