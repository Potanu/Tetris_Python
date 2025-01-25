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
    def init(self):
        self.active_mino = None     # 降下中のミノ
        self.fall_speed = define.DEFAULT_FALL_SPEED # ミノの降下速度
        self.clear_line_list = []   # 消える段
        self.clear_line_anim_counter = 0    # ライン消しアニメーション管理用
        self.clear_line_animation_list = [] # ライン消しアニメーション管理用
        self.level = 1  # レベル
        self.board_matrix = self.clean_matrix()
        self.fall_mino_matrix = self.board_matrix.copy()    # 降下中ミノの描画用マトリクス
        self.ghost_mino_matrix = self.board_matrix.copy()   # ゴーストミノの描画用マトリクス
        self.ghost_mino_left_upper_grid = define.START_MINO_GRID   # ゴーストミノの左上マス座標
        self.board_matrix[-1, :] = -1   # 下辺の透明ブロック
        self.board_matrix[:,  0] = -1   # 左辺の透明ブロック
        self.board_matrix[:, -1] = -1   # 右辺の透明ブロック
        self.next_mino_list = []    # 予告ミノ
        self.ready_counter = define.READY_FRAME    # ゲーム開始までのフレーム
        self.score = 0  # スコア
        self.combo = 0  # 連続ライン消し数
        for y in range(0, define.NEXT_MINO_MAX):
            type = random.randint(enum.MinoType.NONE + 1, len(enum.MinoType) - 1)
            self.next_mino_list.append(mino.Mino(type))
        self.change_state(enum.GameState.READY)
        
    def update(self):
        self.active_func()
        self.draw()   
    
    # STATE: READY
    def ready(self):
        if (self.ready_counter <= 0):
            self.ready_counter = define.READY_FRAME
            self.change_state(enum.GameState.FALL)
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
   
    # STATE: GAME     
    def game(self):
        if self.active_mino == None:
            # 操作ミノの作成
            self.create_mino()
            return
        
        # ミノの操作
        self.check_key_input()
        self.fall_mino()
    
    # ライン消し
    def clear_line(self):
        # ラインのミノを全て削除
        for y in range(0, len(self.clear_line_list)):
            for x in range(1, 1 + define.GAME_GRID_NUM[0]):
                index_y = self.clear_line_list[y]
                self.board_matrix[index_y][x] = enum.MinoType.NONE
        
        # ライン消しアニメーション設定
        for y in range(0, len(self.clear_line_list)):
            for x in range(1, 1 + define.GAME_GRID_NUM[0]):
                anim = clearMinoAnim.ClearMinoAnim()
                grid = (x, self.clear_line_list[y])
                anim.set_data(grid)
                self.clear_line_animation_list.append(anim)
        
        self.change_state(enum.GameState.CLEAR_LINE_ANIM)
    
    # ライン消しアニメーション
    def clear_line_animation(self):
        is_end_all_anim = True
        for j in range(0, len(self.clear_line_animation_list)):
            self.clear_line_animation_list[j].update()
            is_end_all_anim &= self.clear_line_animation_list[j].is_end_anim
        
        if not is_end_all_anim:
            return
        
        self.clear_line_animation_list.clear()
        
        # 全消しチェック
        is_all_clear = True
        for y in range(0, define.GAME_GRID_NUM[1]):
            for x in range(1, 1 + define.GAME_GRID_NUM[0]):
                if self.board_matrix[y][x] != enum.MinoType.NONE:
                    is_all_clear = False
                    break
        
        if not is_all_clear:
        # 全消しでなければクリアした分の段を下に詰める
            for y in range(1, 1 + define.GAME_GRID_NUM[1]):
                top_mino_index = -1
                for x in range(1, 1 + define.GAME_GRID_NUM[0]):
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
        for y in reversed(range(top_mino_index, 1 + define.GAME_GRID_NUM[1])):
            is_clear = True
            for x in range(1, 1 + define.GAME_GRID_NUM[0]):
                if enum.MinoType.NONE < self.board_matrix[y][x]:
                    is_clear = False
                    break
            
            if is_clear:
                clear_index = y
                break
        
        if 0 < clear_index:
            for y in reversed(range(top_mino_index, clear_index + 1)):
                for x in range(1, 1 + define.GAME_GRID_NUM[0]):
                    if y == top_mino_index:
                        self.board_matrix[y][x] = enum.MinoType.NONE
                    else:
                        self.board_matrix[y][x] = self.board_matrix[y - 1][x]
            
            if top_mino_index < clear_index:
                self.shift_down(top_mino_index + 1)
   
    # STATE: PAUSE 
    def pause(self):
        if pygameManager.PygameManager().is_up(enum.KeyType.P):
            self.change_state(enum.GameState.FALL)
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
        if pygameManager.PygameManager().is_down(enum.KeyType.SPACE):
            self.init()
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
        if pygameManager.PygameManager().is_up(enum.KeyType.S):
            self.change_state(enum.GameState.READY)
    
    # キーの押下状態をチェック
    def check_key_input(self):
        if (pygameManager.PygameManager().is_up(enum.KeyType.P)):
            # ゲーム一時停止
            self.change_state(enum.GameState.PAUSE)
            return
        
        if (pygameManager.PygameManager().is_up(enum.KeyType.D)):
            next_mino_grid = (self.active_mino.left_upper_grid[0] + 1, self.active_mino.left_upper_grid[1])
            if self.check_object(self.active_mino.matrix[self.active_mino.index], next_mino_grid):
                # 右移動
                self.active_mino.move_mino(enum.MinoMoveType.MOVE_RIGHT)
                self.update_fall_mino_matrix()
                self.update_ghost_mino_matrix()
        elif (pygameManager.PygameManager().is_up(enum.KeyType.A)):
            next_mino_grid = (self.active_mino.left_upper_grid[0] - 1, self.active_mino.left_upper_grid[1])
            if self.check_object(self.active_mino.matrix[self.active_mino.index], next_mino_grid):
                # 左移動
                self.active_mino.move_mino(enum.MinoMoveType.MOVE_LEFT)
                self.update_fall_mino_matrix()
                self.update_ghost_mino_matrix()
        elif pygameManager.PygameManager().is_up(enum.KeyType.RIGHT):
            if self.check_object(self.active_mino.matrix[self.active_mino.get_next_index(1)], self.active_mino.left_upper_grid):
                # 右回転
                self.active_mino.move_mino(enum.MinoMoveType.ROTATE_RIGHT)
                self.update_fall_mino_matrix()
                self.update_ghost_mino_matrix()
        elif pygameManager.PygameManager().is_up(enum.KeyType.LEFT):
            if self.check_object(self.active_mino.matrix[self.active_mino.get_next_index(-1)], self.active_mino.left_upper_grid):
                # 左回転
                self.active_mino.move_mino(enum.MinoMoveType.ROTATE_LEFT)
                self.update_fall_mino_matrix()
                self.update_ghost_mino_matrix()
    
    # ミノの降下処理
    def fall_mino(self):
        # 降下速度を取得
        is_press_down = pygameManager.PygameManager().is_pressed(enum.KeyType.S)
        fall_speed = define.FALL_HIGH_SPEED if is_press_down else self.fall_speed
        
        if not self.active_mino.check_fall(fall_speed):
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
            self.board_matrix = np.where(self.board_matrix != 0, self.board_matrix, self.fall_mino_matrix)
            self.fall_mino_matrix = self.clean_matrix()
            self.active_mino = None
            if self.check_line_clear():
                self.change_state(enum.GameState.CLEAR_LINE)
            else:
                if self.check_gameover():
                    self.change_state(enum.GameState.GAME_OVER)  
                else:
                    self.combo = 0
    
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
    
    # ゲームオーバー判定
    def check_gameover(self):
        is_gameover = False
        for y in range(0, define.GAME_OVER_GRID_Y):
            for x in range(1, 1 + define.GAME_GRID_NUM[0]):
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
                self.active_func = self.game
            case enum.GameState.CLEAR_LINE:
                self.active_func = self.clear_line
            case enum.GameState.CLEAR_LINE_ANIM:
                self.active_func = self.clear_line_animation
            case enum.GameState.PAUSE:
                self.active_func = self.pause
            case enum.GameState.GAME_OVER:
                self.active_func = self.game_over
            case enum.GameState.END:
                self.active_func = self.end
                  
        self.game_state = next_state
    
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
