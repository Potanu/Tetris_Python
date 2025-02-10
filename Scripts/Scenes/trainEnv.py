import gymnasium
from gymnasium import spaces
import numpy as np
from Utilities import define
from Utilities import enum
from Scenes import gameManager

class TrainEnv(gymnasium.Env):
    def __init__(self):
        super(TrainEnv, self).__init__()
        
        # 観測空間を定義
        self.observation_space = spaces.Dict({
            "board_matrix": spaces.Box(low=-1, high=7, shape=(define.BOARD_GRID_NUM[1], define.BOARD_GRID_NUM[0]), dtype=np.int8),
            "mino_matrix": spaces.Box(low=0, high=1, shape=(4, 4), dtype=np.int8),
            #"fall_mino_matrix": spaces.Box(low=-1, high=7, shape=(define.BOARD_GRID_NUM[1], define.BOARD_GRID_NUM[0]), dtype=np.int8),
            #"ghost_mino_matrix":  spaces.Box(low=-1, high=7, shape=(define.BOARD_GRID_NUM[1], define.BOARD_GRID_NUM[0]), dtype=np.int8),
            "rotation": spaces.Discrete(4),
            "mino_type": spaces.Discrete(len(enum.MinoType)),
            "block_normalized_variance": spaces.Box(low=0.0, high=3969.0, shape=(1,), dtype=np.float16),
            "block_height_diff": spaces.Box(low=0.0, high=define.GAME_GRID_NUM[1], shape=(1,), dtype=np.float16),
            "empty_block_num": spaces.Box(low=0, high=(define.GAME_GRID_NUM[1] - 1)*4, shape=(1,), dtype=np.int8),
        })
        
        # 行動空間の定義
        self.action_space = spaces.Discrete(9 * 4)  # 左右移動の範囲-4~4 * 右回転の範囲0~3
        
        # ゲームの初期化
        self.gameManager = gameManager.GameManager()
        self.reset()
    
    # エピソードリセット時の処理
    def reset(self, seed=None, **kwarg):
        train_flag = True
        ai_play_flag = False
        self.gameManager.init(train_flag, ai_play_flag)
        self.done = False
        self.render_counter = 0
        return self.gameManager.get_state(), {}
    
    def step(self, action):
        if self.gameManager.game_state == enum.GameState.FALL and self.gameManager.active_mino != None:
            self.gameManager.insert_action(action)
            ai_action_list = self.gameManager.ai_action_list

            # ゲーム進行
            for j in range(0, len(ai_action_list)):
                if len(self.gameManager.ai_action_list) == 0:
                    break

                self.gameManager.key_input_state_is_up[:] = [False] * len(enum.KeyType)
                self.gameManager.update_virtual_key_input(ai_action_list[j])
                self.gameManager.active_func()
            self.gameManager.key_input_state_is_up[:] = [False] * len(enum.KeyType)
        else:
            self.gameManager.active_func()
        
        # 状態を取得
        state = self.gameManager.get_state()
        
        # 報酬を計算
        reward = self.get_reward()
        
        # ゲーム終了フラグを確認
        done = self.gameManager.game_state == enum.GameState.GAME_OVER
        
        # エピソードが途中で切り捨てられたかどうか
        truncated = False   # ここでは常にFalseにしておく
        
        # 追加情報
        info = {}   # ここでは特になし
        
        # デバッグ表示
        if self.gameManager.game_state == enum.GameState.CLEAR_LINE:
            self.render()            
          
        return state, reward, done, truncated, info
    
    # エージェントの行動結果に基づく報酬を返す
    def get_reward(self):
        reward = 0
        
        if self.gameManager.game_state == enum.GameState.GAME_OVER:
            # ゲームオーバーの場合、特大ペナルティを与える
            reward += define.GAME_OVER_PENALTY
        elif self.gameManager.game_state == enum.GameState.PROCESS_LANDING:
            reward += 1
            
            # ライン消しが発生した場合、報酬を与える
            clear_line_num = self.gameManager.get_clear_line_num()
            if clear_line_num > 0:
                index = clear_line_num - 1
                combo = self.gameManager.combo + 1  # コンボ数加算前のため
                reward += define.SCORE_LIST[index] * combo
            
            # 接地したとき、操作ブロックの下に隙間が出来てしまった場合ペナルティを与える
            empty_block_num = self.gameManager.count_empty_block_num()
            if empty_block_num == 0:
                reward += define.NO_EMPTY_BLOCK_REWARD
            else:
                reward += empty_block_num * define.EMPTY_BLOCK_PENALTY
            
            # ブロックの分散が小さいほど高い報酬を与える
            old_block_normalized_variance = self.gameManager.block_normalized_variance
            block_normalized_variance = self.gameManager.calculate_block_normalized_variance()
        
            if block_normalized_variance > 0:
                # 分散の範囲に対して報酬を設定
                sign = 1 if block_normalized_variance < old_block_normalized_variance else -0.010
                reward += (old_block_normalized_variance - block_normalized_variance) * sign
                
                # 高さペナルティ
                block_height_diff = self.gameManager.count_block_height_diff()
                
                # ブロックの最大段数と平均段数の差が3段未満かどうかで報酬orペナルティ
                sign = 1 if block_height_diff < 3.0 else -0.010
                reward += block_height_diff * sign
        
        return reward
        
    # デバッグ表示
    def render(self):
        # ボード状態の表示
        all_array = np.where(self.gameManager.board_matrix == 0, self.gameManager.fall_mino_matrix, self.gameManager.board_matrix)
        # 外周を削除するために内側を取り出す
        board_array = all_array[1:-1, 1:-1]
        print("=" * 20)
        print(board_array)
        print("=" * 20)
        
        # 報酬表示
        #print(f"\nnormalized_variance: {self.gameManager.block_normalized_variance}") 
        #print(f"height_diff: {self.gameManager.block_height_diff}") 
        #print(f"empty_block: {self.gameManager.empty_block_num}")
        #print(f"Reward: {reward}") 
        