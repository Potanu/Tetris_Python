import pygame
import numpy as np
import random
from Utilities import enum
from Utilities import define
from Utilities import pygameManager
from Scenes import sceneManager
from Objects import mino
from Objects import clearMinoAnim

class GameManager:
    def init(self, train_flag, ai_play_flag):
        self.train_flag = train_flag        # DQN学習フラグ
        self.ai_play_flag = ai_play_flag    # AIプレイフラグ
        self.active_mino = None             # 降下中のミノ
        self.fall_counter = 0               # ミノの降下タイミング管理用カウンター
        self.clear_line_list = []           # 消える段
        self.clear_line_anim_counter = 0    # ライン消しアニメーション管理用
        self.clear_line_animation_list = [] # ライン消しアニメーション管理用
        self.level = 1  # レベル
        self.board_matrix = self.clean_matrix()
        self.fall_mino_matrix = self.board_matrix.copy()    # 降下中ミノの描画用マトリクス
        self.ghost_mino_matrix = self.board_matrix.copy()   # ゴーストミノの描画用マトリクス
        self.ghost_mino_left_upper_grid = define.START_MINO_GRID   # ゴーストミノの左上マス座標
        self.board_matrix[-1, :] = -1       # 下辺の透明ブロック
        self.board_matrix[:,  0] = -1       # 左辺の透明ブロック
        self.board_matrix[:, -1] = -1       # 右辺の透明ブロック
        self.next_mino_list = []            # 予告ミノ
        self.ready_counter = define.READY_FRAME    # ゲーム開始までのフレーム
        self.score = 0  # スコア
        self.combo = 0  # 連続ライン消し数
        self.key_input_state_is_down = [False] * len(enum.KeyType)      # キーの押下状態（押下した瞬間）
        self.key_input_state_is_up = [False] * len(enum.KeyType)        # キーの押下状態（離した瞬間）
        self.key_input_state_is_pressed = [False] * len(enum.KeyType)   # キーの押下状態（押下中）
        
        self.block_normalized_variance = 0.0  # ブロックの分散値
        self.block_height_diff = 0.0    # ブロックの最大段数-平均段数
        self.empty_block_num = 0        # 空きブロック数
        self.ai_action_list = []        # 行動予定格納リスト
        
        for y in range(0, define.NEXT_MINO_MAX):
            type = random.randint(enum.MinoType.NONE + 1, len(enum.MinoType) - 1)
            self.next_mino_list.append(mino.Mino(type))
        self.create_mino()
        
        if self.train_flag:
            self.change_state(enum.GameState.FALL)  # 強化学習中の場合、準備画面を省略する
        else:
            self.change_state(enum.GameState.READY)
        
    def update(self):
        if not self.train_flag and not self.ai_play_flag:
            self.update_key_input()
            
        self.active_func()
        self.draw()   
    
    # STATE: READY
    def ready(self):
        if (self.ready_counter <= 0):
            self.ready_counter = define.READY_FRAME
            self.change_state(enum.GameState.FALL)
            sceneManager.SceneManager().call_bgm(enum.bgmType.GAME)
            return
        
        string = ""
        rate = self.ready_counter / define.READY_FRAME
        if 0.750 < rate:
            string = "3"
        elif 0.50 < rate:
            string = "2"
        elif 0.250 < rate:
            string = "1"
        elif 0.0 < rate:
            string = "0"

        fill_tuple = (enum.ObjectType.UI, 10, enum.DrawType.FILL, -1, define.READY_SCREEN_BG_COLOR, -1, -1, -1, -1)
        sceneManager.SceneManager().add_draw_queue(fill_tuple)
        font = pygame.font.Font(None, define.READY_TEXT_SIZE)
        gTxt = font.render(string, True, define.READY_TEXT_COLOR)
        text_rect = gTxt.get_rect(center=define.SCREEN_CENTER_POS)
        text_tuple = (enum.ObjectType.UI, 11, enum.DrawType.TEXT, gTxt, -1, -1, text_rect, -1, -1)
        sceneManager.SceneManager().add_draw_queue(text_tuple)
        self.ready_counter -= 1
   
    # STATE: FALL     
    def fall(self):
        if self.active_mino == None:
            # 操作ミノの作成
            self.create_mino()
            return
        
        # ミノの操作
        self.check_key_input()
        self.fall_mino()
    
    # STATE: PROCESS_LANDING
    def process_landing(self):
        self.board_matrix = np.where(self.board_matrix != 0, self.board_matrix, self.fall_mino_matrix)
        self.fall_mino_matrix = self.clean_matrix()
        self.active_mino = None
        if self.check_line_clear():
            # 消せるラインがある場合
            self.change_state(enum.GameState.CLEAR_LINE)
        else:
            if self.check_gameover():
                # ゲームオーバー
                self.change_state(enum.GameState.GAME_OVER)
            else:
                # 次のミノ出現へ
                self.combo = 0
                self.change_state(enum.GameState.FALL)
    
    # ライン消し
    def clear_line(self):
        # ラインのミノを全て削除
        for y in range(0, len(self.clear_line_list)):
            for x in range(1, define.BOARD_GRID_NUM[0] - 1):
                index_y = self.clear_line_list[y]
                self.board_matrix[index_y][x] = enum.MinoType.NONE
        
        # ライン消しアニメーション設定
        for y in range(0, len(self.clear_line_list)):
            for x in range(1, define.BOARD_GRID_NUM[0] - 1):
                anim = clearMinoAnim.ClearMinoAnim()
                grid = (x, self.clear_line_list[y])
                anim.set_data(grid)
                self.clear_line_animation_list.append(anim)
        
        if self.train_flag:
            self.change_state(enum.GameState.DROP_LINE)  # 強化学習中の場合、ライン消しアニメーションを省略する
        else:
            self.change_state(enum.GameState.CLEAR_LINE_ANIM)
            sceneManager.SceneManager().call_se(enum.SeType.CLEAR_LINE)
    
    # ライン消しアニメーション
    def clear_line_animation(self):
        is_end_all_anim = True
        for j in range(0, len(self.clear_line_animation_list)):
            self.clear_line_animation_list[j].update()
            is_end_all_anim &= self.clear_line_animation_list[j].is_end_anim
        
        if not is_end_all_anim:
            return
        
        self.clear_line_animation_list.clear()
        self.change_state(enum.GameState.DROP_LINE)
    
    # ラインクリア後、ブロックを下に詰める処理 
    def drop_line(self):
        if self.check_all_block_clear():
            if not self.train_flag:
                sceneManager.SceneManager().call_se(enum.SeType.CLEAR_ALL_BLOCK)
        else:
        # 全消しでなければクリアした分の段を下に詰める
            for y in range(1, define.BOARD_GRID_NUM[1] - 1):
                top_mino_index = -1
                for x in range(1, define.BOARD_GRID_NUM[0] - 1):
                    if enum.MinoType.NONE < self.board_matrix[y][x]:
                        top_mino_index = y
                        break
                if -1 < top_mino_index:
                    break
            
            self.shift_down(top_mino_index)
        
        # スコア加算
        self.combo += 1
        score_index = len(self.clear_line_list) - 1
        self.score += define.SCORE_LIST[score_index] * self.combo
        
        if self.check_gameover():
            self.change_state(enum.GameState.GAME_OVER)
        else:
            self.clear_line_list.clear()
            self.change_state(enum.GameState.FALL)
    
    # クリアした分の段を下に詰める         
    def shift_down(self, top_mino_index):
        clear_index = -1
        for y in reversed(range(top_mino_index, define.BOARD_GRID_NUM[1] - 1)):
            is_clear = True
            for x in range(1, define.BOARD_GRID_NUM[0] - 1):
                if enum.MinoType.NONE < self.board_matrix[y][x]:
                    is_clear = False
                    break
            
            if is_clear:
                clear_index = y
                break
        
        if 0 < clear_index:
            for y in reversed(range(top_mino_index, clear_index + 1)):
                for x in range(1, define.BOARD_GRID_NUM[0] - 1):
                    if y == top_mino_index:
                        self.board_matrix[y][x] = enum.MinoType.NONE
                    else:
                        self.board_matrix[y][x] = self.board_matrix[y - 1][x]
            
            if not self.train_flag:
                sceneManager.SceneManager().call_se(enum.SeType.PUT_BLOCK)
            
            if top_mino_index < clear_index:
                self.shift_down(top_mino_index + 1)
   
    # STATE: PAUSE 
    def pause(self):
        if self.key_input_state_is_up[enum.KeyType.P]:
            self.change_state(enum.GameState.FALL)
            
            if not self.train_flag:
                sceneManager.SceneManager().pause_sound(False)
            return
        
        fill_tuple = (enum.ObjectType.UI, 10, enum.DrawType.FILL, -1, define.PAUSE_SCREEN_BG_COLOR, -1, -1, -1, -1)
        sceneManager.SceneManager().add_draw_queue(fill_tuple)
        font = pygame.font.Font(None, define.PAUSE_TEXT_SIZE)
        gTxt = font.render("PAUSE", True, define.PAUSE_TEXT_COLOR)
        text_rect = gTxt.get_rect(center=define.SCREEN_CENTER_POS)
        text_tuple = (enum.ObjectType.UI, 11, enum.DrawType.TEXT, gTxt, -1, -1, text_rect, -1, -1)
        sceneManager.SceneManager().add_draw_queue(text_tuple)
    
    # STATE: GAME_OVER  
    def game_over(self):
        if self.train_flag:
           # 強化学習中は画面をスキップする 
           self.init(self.train_flag, self.ai_play_flag)
           return
        
        if self.key_input_state_is_down[enum.KeyType.SPACE]:
            self.init(self.train_flag, self.ai_play_flag)
            self.change_state(enum.GameState.READY)
            return
        
        fill_tuple = (enum.ObjectType.UI, 10, enum.DrawType.FILL, -1, define.GAME_OVER_SCREEN_BG_COLOR, -1, -1, -1, -1)
        sceneManager.SceneManager().add_draw_queue(fill_tuple)
        
        gameover_font = pygame.font.Font(None, define.GAME_OVER_TEXT_SIZE)
        gTxt = gameover_font.render("GAME OVER", True, define.GAME_BG_COLOR)
        text_rect = gTxt.get_rect(center=define.GAME_OVER_TEXT_MIDDLE_POS)
        text_tuple = (enum.ObjectType.UI, 11, enum.DrawType.TEXT, gTxt, -1, -1, text_rect, -1, -1)
        sceneManager.SceneManager().add_draw_queue(text_tuple)
        
        input_font = pygame.font.Font(None, define.GAME_OVER_GUIDE_TEXT_SIZE)
        gTxt = input_font.render("Please Enter SPACE KEY", True, define.GAME_OVER_GUIDE_TEXT_COLOR)
        text_rect = gTxt.get_rect(center=define.GAME_OVER_GUIDE_TEXT_MIDDLE_POS)
        text_tuple = (enum.ObjectType.UI, 11, enum.DrawType.TEXT, gTxt, -1, -1, text_rect, -1, -1)
        sceneManager.SceneManager().add_draw_queue(text_tuple)
    
    # STATE: END
    def end(self):
        pass
    
    # キーの押下状態をチェック
    def check_key_input(self):
        if (self.key_input_state_is_up[enum.KeyType.ESC]):
            # ゲーム終了
            self.change_state(enum.GameState.END)
            
            if not self.train_flag:
                sceneManager.SceneManager().stop_sound()
            return
        
        if (self.key_input_state_is_up[enum.KeyType.P]):
            # ゲーム一時停止
            self.change_state(enum.GameState.PAUSE)
            
            if not self.train_flag:
                sceneManager.SceneManager().pause_sound(True)
            return
        
        if (self.key_input_state_is_up[enum.KeyType.D]):
            next_mino_grid = (self.active_mino.left_upper_grid[0] + 1, self.active_mino.left_upper_grid[1])
            if self.check_object(self.active_mino.matrix[self.active_mino.index], next_mino_grid):
                # 右移動
                self.active_mino.move_mino(enum.MinoMoveType.MOVE_RIGHT)
                self.update_fall_mino_matrix()
                self.update_ghost_mino_matrix()
        elif (self.key_input_state_is_up[enum.KeyType.A]):
            next_mino_grid = (self.active_mino.left_upper_grid[0] - 1, self.active_mino.left_upper_grid[1])
            if self.check_object(self.active_mino.matrix[self.active_mino.index], next_mino_grid):
                # 左移動
                self.active_mino.move_mino(enum.MinoMoveType.MOVE_LEFT)
                self.update_fall_mino_matrix()
                self.update_ghost_mino_matrix()
        elif (self.key_input_state_is_up[enum.KeyType.RIGHT]):
            if self.check_object(self.active_mino.matrix[self.active_mino.get_next_index(1)], self.active_mino.left_upper_grid):
                # 右回転
                self.active_mino.move_mino(enum.MinoMoveType.ROTATE_RIGHT)
                self.update_fall_mino_matrix()
                self.update_ghost_mino_matrix()
        elif (self.key_input_state_is_up[enum.KeyType.LEFT]):
            if self.check_object(self.active_mino.matrix[self.active_mino.get_next_index(-1)], self.active_mino.left_upper_grid):
                # 左回転
                self.active_mino.move_mino(enum.MinoMoveType.ROTATE_LEFT)
                self.update_fall_mino_matrix()
                self.update_ghost_mino_matrix()
        elif (self.key_input_state_is_up[enum.KeyType.W]):
            # ハードドロップ
            self.active_mino.left_upper_grid = self.ghost_mino_left_upper_grid
            self.fall_mino_matrix = self.ghost_mino_matrix
            self.fall_counter = define.DEFAULT_FALL_SPEED
                   
    # ミノの降下処理
    def fall_mino(self):
        # 降下速度を取得
        is_press_down = self.key_input_state_is_pressed[enum.KeyType.S]
        fall_speed = define.FALL_HIGH_SPEED if is_press_down else define.DEFAULT_FALL_SPEED
        
        if not self.check_fall(fall_speed):
            # 降下タイミングでは無いので処理を抜ける
            return
        
        # 降下可能かチェック
        next_mino_grid = (self.active_mino.left_upper_grid[0], self.active_mino.left_upper_grid[1] + 1)
        
        if self.check_object(self.active_mino.matrix[self.active_mino.index], next_mino_grid):
            # 降下
            self.active_mino.move_mino(enum.MinoMoveType.FALL)
            self.update_fall_mino_matrix()
        else:
            # 接地
            self.change_state(enum.GameState.PROCESS_LANDING)
            
            if not self.train_flag:
                sceneManager.SceneManager().call_se(enum.SeType.PUT_BLOCK)
    
    # ミノの降下タイミングを管理
    def check_fall(self, fall_speed):
        if fall_speed <= self.fall_counter:
            self.fall_counter = 0
            return True
        else:
            self.fall_counter += 1
            return False
    
    # 消せるラインがあるかをチェック
    def check_line_clear(self):
        for y in range(0, len(self.board_matrix) - 1): # 一番下の段は固定ブロックしかないので見ない
            is_clear = True
            for x in range(0, len(self.board_matrix[0])):
                if self.board_matrix[y][x] == enum.MinoType.NONE:
                    is_clear = False
                    break
            
            if is_clear:
                self.clear_line_list.append(y)
        
        return 0 < len(self.clear_line_list)
    
    # 当たり判定チェック(なければTrue)
    def check_object(self, next_mino_matrix, next_mino_grid):
        for y in reversed(range(0, len(next_mino_matrix))):
            for x in range(0, len(next_mino_matrix[0])):
                index_x = next_mino_grid[0] + x
                index_y = next_mino_grid[1] + y
                if next_mino_matrix[y][x] == [0] or self.board_matrix[index_y][index_x] == 0:
                    continue
                return False
        return True
    
    # ブロック全消し判定
    def check_all_block_clear(self):
        is_all_clear = True
        for y in range(0, define.GAME_GRID_NUM[1]):
            for x in range(1, define.BOARD_GRID_NUM[0] - 1):
                if self.board_matrix[y][x] != enum.MinoType.NONE:
                    is_all_clear = False
                    break
            if not is_all_clear:
                break
            
        return is_all_clear
    
    # ゲームオーバー判定
    def check_gameover(self):
        is_gameover = False
        for y in range(0, define.GAME_OVER_GRID_Y):
            for x in range(1, define.BOARD_GRID_NUM[0] - 1):
                if self.board_matrix[y][x] != enum.MinoType.NONE:
                    is_gameover = True
                    break
            if is_gameover:
                break
        
        return is_gameover
    
    # 降下ミノ描画用マトリクスの更新
    def update_fall_mino_matrix(self):
        self.fall_mino_matrix = self.clean_matrix()
        fall_mino_matrix = self.active_mino.matrix[self.active_mino.index].copy()
        for y in range(0, len(fall_mino_matrix)):
            for x in range(0, len(fall_mino_matrix[0])):
                index_x = self.active_mino.left_upper_grid[0] + x
                index_y = self.active_mino.left_upper_grid[1] + y
                if fall_mino_matrix[y][x] == [0]:
                    continue
                self.fall_mino_matrix[index_y][index_x] = self.active_mino.mino_type
    
    # ゴーストミノ描画用マトリクスの更新
    def update_ghost_mino_matrix(self):
        self.ghost_mino_left_upper_grid = self.active_mino.left_upper_grid
   
        while True:
            if self.check_object(self.active_mino.matrix[self.active_mino.index],
                    (self.ghost_mino_left_upper_grid[0], self.ghost_mino_left_upper_grid[1] + 1)):
                self.ghost_mino_left_upper_grid = (self.ghost_mino_left_upper_grid[0], self.ghost_mino_left_upper_grid[1] + 1)
            else:
                break     
        
        fall_mino_matrix = self.active_mino.matrix[self.active_mino.index].copy()
        self.ghost_mino_matrix = self.clean_matrix()
        for y in range(0, len(fall_mino_matrix)):
            for x in range(0, len(fall_mino_matrix[0])):
                index_x = self.ghost_mino_left_upper_grid[0] + x
                index_y = self.ghost_mino_left_upper_grid[1] + y
                if fall_mino_matrix[y][x] == [0]:
                    continue
                self.ghost_mino_matrix[index_y][index_x] = self.active_mino.mino_type
    
    # 初期化したボード配列を返す
    def clean_matrix(self):
        return np.full((define.BOARD_GRID_NUM[1], define.BOARD_GRID_NUM[0]), enum.MinoType.NONE)
    
    # 新規ミノの作成
    def create_mino(self):
        self.active_mino = self.next_mino_list[0]
        mino_matrix = self.active_mino.matrix[self.active_mino.index].copy()
        for y in range(0, len(mino_matrix)):
            for x in range(0, len(mino_matrix[0])):
                if mino_matrix[y][x] == [0]:
                    continue
                index_x = self.active_mino.left_upper_grid[0] + x
                index_y = self.active_mino.left_upper_grid[1] + y
                self.fall_mino_matrix[index_y][index_x] = self.active_mino.mino_type
                
        self.update_next_mino()
        self.update_ghost_mino_matrix()
    
    # 予告ミノの更新
    def update_next_mino(self):
        for index in range(1, len(self.next_mino_list)):
            self.next_mino_list[index - 1] = self.next_mino_list[index]
        next_type = random.randint(enum.MinoType.NONE + 1, len(enum.MinoType) - 1)
        self.next_mino_list[len(self.next_mino_list) - 1] = mino.Mino(next_type)
    
    # ステート変更
    def change_state(self, next_state):
        match next_state:
            case enum.GameState.READY:
                self.active_func = self.ready
            case enum.GameState.FALL:
                self.active_func = self.fall
            case enum.GameState.PROCESS_LANDING:
                self.active_func = self.process_landing
            case enum.GameState.CLEAR_LINE:
                self.active_func = self.clear_line
            case enum.GameState.CLEAR_LINE_ANIM:
                self.active_func = self.clear_line_animation
            case enum.GameState.DROP_LINE:
                self.active_func = self.drop_line
            case enum.GameState.PAUSE:
                self.active_func = self.pause
            case enum.GameState.GAME_OVER:
                self.active_func = self.game_over
            case enum.GameState.END:
                self.active_func = self.end
                  
        self.game_state = next_state
    
    # キーの押下状態の更新
    def update_key_input(self):
        self.key_input_state_is_up[:] = [False] * len(enum.KeyType)
        if (pygameManager.PygameManager().is_up(pygame.K_w)):
            self.key_input_state_is_up[enum.KeyType.W] = True
        if (pygameManager.PygameManager().is_up(pygame.K_a)):
            self.key_input_state_is_up[enum.KeyType.A] = True
        if (pygameManager.PygameManager().is_up(pygame.K_s)):
            self.key_input_state_is_up[enum.KeyType.S] = True
        if (pygameManager.PygameManager().is_up(pygame.K_d)):
            self.key_input_state_is_up[enum.KeyType.D] = True
        if (pygameManager.PygameManager().is_up(pygame.K_p)):
            self.key_input_state_is_up[enum.KeyType.P] = True
        if (pygameManager.PygameManager().is_up(pygame.K_LEFT)):
            self.key_input_state_is_up[enum.KeyType.LEFT] = True
        if (pygameManager.PygameManager().is_up(pygame.K_RIGHT)):
            self.key_input_state_is_up[enum.KeyType.RIGHT] = True
        if (pygameManager.PygameManager().is_up(pygame.K_SPACE)):
            self.key_input_state_is_up[enum.KeyType.SPACE] = True
        if (pygameManager.PygameManager().is_up(pygame.K_ESCAPE)):
            self.key_input_state_is_up[enum.KeyType.ESC] = True
        if (pygameManager.PygameManager().is_up(pygame.K_F1)):
            self.key_input_state_is_up[enum.KeyType.F1] = True
        
        self.key_input_state_is_pressed = [False] * len(enum.KeyType)
        if (pygameManager.PygameManager().is_pressed(pygame.K_w)):
            self.key_input_state_is_pressed[enum.KeyType.W] = True
        if (pygameManager.PygameManager().is_pressed(pygame.K_a)):
            self.key_input_state_is_pressed[enum.KeyType.A] = True
        if (pygameManager.PygameManager().is_pressed(pygame.K_s)):
            self.key_input_state_is_pressed[enum.KeyType.S] = True
        if (pygameManager.PygameManager().is_pressed(pygame.K_d)):
            self.key_input_state_is_pressed[enum.KeyType.D] = True
        if (pygameManager.PygameManager().is_pressed(pygame.K_p)):
            self.key_input_state_is_pressed[enum.KeyType.P] = True
        if (pygameManager.PygameManager().is_pressed(pygame.K_LEFT)):
            self.key_input_state_is_pressed[enum.KeyType.LEFT] = True
        if (pygameManager.PygameManager().is_pressed(pygame.K_RIGHT)):
            self.key_input_state_is_pressed[enum.KeyType.RIGHT] = True
        if (pygameManager.PygameManager().is_pressed(pygame.K_SPACE)):
            self.key_input_state_is_pressed[enum.KeyType.SPACE] = True
        if (pygameManager.PygameManager().is_pressed(pygame.K_ESCAPE)):
            self.key_input_state_is_pressed[enum.KeyType.ESC] = True
        if (pygameManager.PygameManager().is_pressed(pygame.K_F1)):
            self.key_input_state_is_pressed[enum.KeyType.F1] = True
        
        self.key_input_state_is_down = [False] * len(enum.KeyType)
        if (pygameManager.PygameManager().is_down(pygame.K_w)):
            self.key_input_state_is_down[enum.KeyType.W] = True
        if (pygameManager.PygameManager().is_down(pygame.K_a)):
            self.key_input_state_is_down[enum.KeyType.A] = True
        if (pygameManager.PygameManager().is_down(pygame.K_s)):
            self.key_input_state_is_down[enum.KeyType.S] = True
        if (pygameManager.PygameManager().is_down(pygame.K_d)):
            self.key_input_state_is_down[enum.KeyType.D] = True
        if (pygameManager.PygameManager().is_down(pygame.K_p)):
            self.key_input_state_is_down[enum.KeyType.P] = True
        if (pygameManager.PygameManager().is_down(pygame.K_LEFT)):
            self.key_input_state_is_down[enum.KeyType.LEFT] = True
        if (pygameManager.PygameManager().is_down(pygame.K_RIGHT)):
            self.key_input_state_is_down[enum.KeyType.RIGHT] = True
        if (pygameManager.PygameManager().is_down(pygame.K_SPACE)):
            self.key_input_state_is_down[enum.KeyType.SPACE] = True
        if (pygameManager.PygameManager().is_down(pygame.K_ESCAPE)):
            self.key_input_state_is_down[enum.KeyType.ESC] = True
        if (pygameManager.PygameManager().is_down(pygame.K_F1)):
            self.key_input_state_is_down[enum.KeyType.F1] = True
    
    # 描画
    def draw(self):
        def draw_matrix(matrix, alpha):
            for y in range(0, len(matrix)):
                for x in range(0, len(matrix[0])):
                    mino_type = matrix[y][x]
                    if mino_type <= enum.MinoType.NONE:
                        continue
                    pos_x = define.GAME_SCREEN_OFFSET[0] + define.BLOCK_SIZE[0] * x
                    pos_y = define.GAME_SCREEN_OFFSET[1] + define.BLOCK_SIZE[1] * y - define.BLOCK_SIZE[1]
                    color = define.MINO_COLOR_STR[mino_type] + alpha
                    block_tuple = (enum.ObjectType.OBJECT, 0, enum.DrawType.RECT_ALPHA, -1, color,
                                pygame.Rect(pos_x + 1, pos_y + 1, define.BLOCK_SIZE[0] - 2, define.BLOCK_SIZE[1] - 2), -1, -1, -1)
                    sceneManager.SceneManager().add_draw_queue(block_tuple)
        
        draw_matrix(self.board_matrix, "FF")
        draw_matrix(self.fall_mino_matrix, "FF")
        draw_matrix(self.ghost_mino_matrix, define.GHOST_MINO_ALPHA)

    # ==========================
    # AI学習用
    # ==========================
    
    # エージェントが状況を理解するためのゲームデータを返す
    def get_state(self):
        # 観測データを辞書で返す
        index = 0 if self.active_mino == None else self.active_mino.index
        mino_type = 0 if self.active_mino == None else self.active_mino.mino_type
        active_mino_list = np.zeros((4, 4)) if self.active_mino == None else list(self.active_mino.matrix[0])
        active_mino_array = np.array(active_mino_list, dtype=np.int8).squeeze()
        state = {
            "board_matrix": self.board_matrix,
            "mino_matrix": active_mino_array,
            #"fall_mino_matrix": self.fall_mino_matrix,
            #"ghost_mino_matrix": self.ghost_mino_matrix,
            "rotation": index,
            "mino_type": mino_type,
            "block_normalized_variance": np.array([self.block_normalized_variance], dtype=np.float16),
            "block_height_diff": np.array([self.block_height_diff], dtype=np.float16),
            "empty_block_num": np.array([self.empty_block_num], dtype=np.int8)
        }
        
        return state
    
    # 消せるラインの段数を返す
    def get_clear_line_num(self):
        clear_line_num = 0
        for y in range(0, len(self.board_matrix) - 1): # 一番下の段は固定ブロックしかないので見ない
            is_clear = True
            for x in range(0, len(self.board_matrix[0])):
                if self.board_matrix[y][x] == enum.MinoType.NONE:
                    is_clear = False
                    break
            
            if is_clear:
                clear_line_num += 1
        
        return clear_line_num

    # ブロック設置時に発生した穴の数を返す
    def count_empty_block_num(self):
        pairs = set()
        # 現在の操作ブロック各列を下から検索し、一番下に位置するブロック座標を見つけたら保存する
        for x in range(1, define.BOARD_GRID_NUM[0] - 1):
            for y in reversed(range(2, define.GAME_GRID_NUM[1])): # デッドラインから上と、最下段の列は無視する
                if (self.fall_mino_matrix[y][x] > enum.MinoType.NONE):
                    pairs.add((x,y))
                    break
        
        # 操作ブロックの下にある空きブロックの数をカウントする
        empty_block_counter = 0
        for x, y in pairs:
            for y_grid in range(y + 1, define.GAME_GRID_NUM[1]):
                if (self.fall_mino_matrix[y_grid][x] > enum.MinoType.NONE):
                    # 空きブロックでなければ次の列へ
                    break
                empty_block_counter += 1
        
        self.empty_block_num = empty_block_counter
        return self.empty_block_num

    # ブロックの分散を正規化したものを返す
    def calculate_block_normalized_variance(self):
        block_array = np.where(self.board_matrix == 0, self.fall_mino_matrix, self.board_matrix)
        block_array = block_array[1:-1, 1:-1]   # 外周を削除
        block_list = np.zeros(define.GAME_GRID_NUM[0], dtype=int)   # 列ごとのブロック数を格納
        for x in range(0, define.GAME_GRID_NUM[0]):
            for y in range(0, define.GAME_GRID_NUM[1] - 1):
                if (block_array[y][x] > enum.MinoType.NONE):
                    block_list[x] += 1
        
        # 分散を計算
        variance = np.var(block_list)
        
        # 最大分散を計算
        max_variance = (np.max(block_list) - np.min(block_list)) ** 2 / 4
        
        # 正規化分散を計算
        normalized_variance = variance / max_variance
        
        self.normalized_variance = normalized_variance
        return self.normalized_variance

    # 積みあがったブロックの最大段数から平均段数を引いた値を返す
    def count_block_height_diff(self):
        block_array = np.where(self.board_matrix == 0, self.fall_mino_matrix, self.board_matrix)
        block_array = block_array[1:-1, 1:-1]   # 外周を削除
        block_num = 0   # ブロックの数
        block_max_y_index = define.GAME_GRID_NUM[1] - 1 # 最も高いブロックのyインデックス
        for y in range(0, define.GAME_GRID_NUM[1] - 1):
            for x in range(0, define.GAME_GRID_NUM[0]):
                if (block_array[y][x] > enum.MinoType.NONE):
                    block_num += 1
                    
                    if y < block_max_y_index:
                        block_max_y_index = y

        max_height = define.GAME_GRID_NUM[1] - block_max_y_index
        avg_height = block_num / define.GAME_GRID_NUM[0]
        
        self.block_height_diff = max_height - avg_height
        return self.block_height_diff

    # エージェントが選択したアクションを元にキーの押下状態を更新
    def update_virtual_key_input(self, action):
        match action:
            case enum.ACTION_SPACE_TYPE.MOVE_RIGHT:
                self.key_input_state_is_up[enum.KeyType.D] = True
            case enum.ACTION_SPACE_TYPE.MOVE_LEFT:
                self.key_input_state_is_up[enum.KeyType.A] = True
            case enum.ACTION_SPACE_TYPE.ROTATE_RIGHT:
                self.key_input_state_is_up[enum.KeyType.RIGHT] = True
            case enum.ACTION_SPACE_TYPE.HARD_DROP:
                self.key_input_state_is_up[enum.KeyType.W] = True

    # エージェントの選択したアクションをリストに格納
    def insert_action(self, action):
        self.ai_action_list.clear()
        move_num = (action // 4) - 4    # 左右移動（-4~4 に変換）
        right_rotate_num = action % 4   # 右回転（0〜3）
        
        if move_num != 0:
            # 左右移動
            action_state = enum.ACTION_SPACE_TYPE.MOVE_RIGHT if move_num > 0 else enum.ACTION_SPACE_TYPE.MOVE_LEFT
            sign = 1 if move_num > 0 else -1
            for j in range(1, move_num * sign):
                # 移動操作を格納
                self.ai_action_list.append(action_state)
        
        if right_rotate_num > 0:
            # 右回転
            action_state = enum.ACTION_SPACE_TYPE.ROTATE_RIGHT
            for j in range(1, right_rotate_num):
                # 右回転操作を格納
                self.ai_action_list.append(action_state)
        
        # 降下操作を格納
        action_state = enum.ACTION_SPACE_TYPE.HARD_DROP
        self.ai_action_list.append(action_state)
        