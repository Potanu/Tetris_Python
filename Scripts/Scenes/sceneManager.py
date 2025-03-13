import pygame
from pygame.locals import *
import numpy as np
from Utilities import singleton
from Utilities import enum
from Utilities import define
from Utilities import pygameManager
from Scenes import selectScene
from Scenes import gameScene

class SceneManager(singleton.Singleton):
  def init(self):
    pygame.init()
    self.screen = pygame.display.set_mode(define.SCREEN_SIZE)
    pygame.display.set_caption(u"タイトル")
    
    self.draw_queue = []
    self.active_scene = self.get_scene(enum.SceneType.SELECT)
    self.is_debug = False               # デバッグ表示管理用
    self.debug_text_count = 0           # デバッグ表示項目が複数行に渡る場合のカウンター
    self.old_elapsed_time = 0           # 経過時間保存用（/millseconds)
    self.fps_view_update_counter = 0    # fps表示更新用カウンター
    
    # サウンド初期化
    self.init_sound()
 
  def init_sound(self):
    pygame.mixer.init()
    self.se_list = np.zeros(len(enum.SeType), dtype=pygame.mixer.Sound)
    self.se_list[enum.SeType.PUT_BLOCK] = pygame.mixer.Sound(define.PUT_BLOCK_SE)
    self.se_list[enum.SeType.CLEAR_LINE] = pygame.mixer.Sound(define.CLEAR_LINE_SE)
    self.se_list[enum.SeType.CLEAR_ALL_BLOCK] = pygame.mixer.Sound(define.CLEAR_ALL_BLOCK_SE)
    
  def run(self):
    while True:
      pygameManager.PygameManager().get_events()
      if pygameManager.PygameManager().get_event(QUIT):
          break
      
      # 画面更新
      self.active_scene.update()
      self.draw()
      
       # デバッグモード切替チェック
      if (pygameManager.PygameManager().is_up(pygame.K_F1)):
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
  
  def call_bgm(self, type):
    match type:
      case enum.bgmType.GAME:
        pygame.mixer.music.load(define.GAME_BGM)  # BGM読み込み
        pygame.mixer.music.play(loops=-1)         # BGM再生
  
  def call_se(self, type):
    if type < 0 or type >= len(enum.SeType):
      return
    
    self.se_list[type].play()
  
  def stop_sound(self):
    pygame.mixer.music.stop()
  
  def pause_sound(self, state):
    if state:
      pygame.mixer.music.pause()
    else:
      pygame.mixer.music.unpause()
  
  def add_draw_queue(self, tuple):
    self.draw_queue.append(tuple)
  
  def move_Scene(self, type):
    self.active_scene = self.get_scene(type)
      
  def get_scene(self, type):
    match type:
      case enum.SceneType.SELECT:
        return selectScene.SelectScene()
      case enum.SceneType.GAME:
        return gameScene.GameScene()
      case enum.SceneType.AI_PLAY_GAME:
        return gameScene.GameScene(ai_play_flag=True)
  
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

  def exit(self):
    self.active_scene.exit()
