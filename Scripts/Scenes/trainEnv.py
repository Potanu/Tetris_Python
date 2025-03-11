import gymnasium
from gymnasium import spaces
import numpy as np
from Utilities import enum
from Scenes import gameManager

class TrainEnv(gymnasium.Env):
    def __init__(self):
        super(TrainEnv, self).__init__()
            
        # 観測空間を定義
        self.observation_space = spaces.Dict({
            "board": spaces.Box(
                # ブロックの数、穴の数、空きブロック率、最大の高さ、ブロックのばらつき
                # 消したラインの数、消したラインの数（合計）、経過ステップ数
                low=np.array([0] + [0] + [0] + [0] + [0] + [0] + [0] + [0]),
                high=np.array([200] + [200] + [1] + [20] + [100] + [4] + [1000] + [10000]),
                shape=(8,),
                dtype=np.float32
            ),
            "board_matrix": spaces.Box(
                low=0,
                high=1,
                shape=(21,10),
                dtype=np.float32
            ),
            "ghost_mino_matrix": spaces.Box(
                low=0,
                high=1,
                shape=(21,10),
                dtype=np.float32
            ),
            "current_mino": spaces.Box(
                # ミノのタイプ、X、Y、回転
                low=np.array([1, -2, 0, 0]),
                high=np.array([7, 8, 19, 3]),
                shape=(4,),
                dtype=np.float32
            ),
            "current_mino_matrix": spaces.Box(
                low=0,
                high=1,
                shape=(21,10),
                dtype=np.float32
            ),
            "next_mino": spaces.Box(
                # ミノのタイプ、X、Y、回転
                low=np.array([1, 3, 0, 0]),
                high=np.array([7, 3, 0, 3]),
                shape=(4,),
                dtype=np.float32
            ),
            "next_mino_matrix": spaces.Box(
                low=0,
                high=1,
                shape=(4,4),
                dtype=np.float32
            ),
        })
        
        self.action_space = spaces.Discrete(5)  # 左右移動 + 左右回転 + ハードドロップ
        
        # ゲームの初期化
        self.gameManager = gameManager.GameManager()
        self.reset()
        
        self.render_flag = False
    
    # エピソードリセット時の処理
    def reset(self, seed=None, **kwarg):
        train_flag = True
        ai_play_flag = False
        self.gameManager.init(train_flag, ai_play_flag)
        self.old_under_empty_block_num = 0
        self.old_all_empty_block_num = 0
        self.old_block_normalized_variance = 0.0
        self.old_height_variance = 0.0
        return self.gameManager.get_state(), {}
    
    def step(self, action):
        tmp_action = action
        while (True):
            if self.gameManager.game_state == enum.GameState.FALL and self.gameManager.active_mino != None:
                if self.gameManager.step_num >= 10000:
                    tmp_action = enum.ACTION_SPACE_TYPE.HARD_DROP
                
                # ゲーム進行
                self.gameManager.key_input_state_is_up[:] = [False] * len(enum.KeyType)
                self.gameManager.update_virtual_key_input(tmp_action)
                self.gameManager.active_func()
                self.gameManager.key_input_state_is_up[:] = [False] * len(enum.KeyType)
                break
            else:
                self.gameManager.active_func()
        
        # 状態を取得
        state = self.gameManager.get_state()
        
         # ゲーム終了フラグを確認
        done = self.gameManager.max_block_height >= 19 
        
        # if done:
        #     print(state)
        
        # 報酬を計算
        reward = self.get_reward(done)
        
        # エピソードが途中で切り捨てられたかどうか
        truncated = False 
        
        # 追加情報
        info = {}   # ここでは特になし          

        return state, reward, done, truncated, info
    
    # エージェントの行動結果に基づく報酬を返す
    def get_reward(self, done):
        reward = 0
        
        if done:
            # ゲームオーバー
            reward -= 100
            
            if self.gameManager.total_clear_line_num == 0:
                reward -= 50
            else:
                reward += self.gameManager.total_clear_line_num * 10

        clear_line_num = self.gameManager.get_clear_line_num()
        if clear_line_num > 0:
            # ライン消しが発生
            reward += clear_line_num * 10
        
        # 経過ステップ数をチェック
        if self.gameManager.step_num <= 10:
            reward += 0.5
        else:
            reward -= (self.gameManager.step_num - 10) * 0.1
        
        if self.gameManager.game_state != enum.GameState.PROCESS_LANDING:
            reward -= 0.01
            return reward
        
        # 設置時
        
        # ブロックの最大の高さをチェック
        reward += 2 - (self.gameManager.max_block_height * 0.2)
        
        # 設置したブロック以下に発生した空きブロックの数に応じて報酬・ペナルティを付与する
        if self.old_under_empty_block_num > 0:
            if self.gameManager.under_empty_block_num <= self.old_under_empty_block_num:
                reward += ((self.old_under_empty_block_num - self.gameManager.under_empty_block_num) + 1) * 6
            else:
                reward -= (self.gameManager.under_empty_block_num - self.old_under_empty_block_num) * 0.3
        
        # 空きブロック率に応じて報酬・ペナルティを付与する
        if self.gameManager.empty_block_rate > 0.3:
            reward -= (1.0 - self.gameManager.empty_block_rate) * 0.5
        else:
            reward += 0.3
        
        # ブロックのばらつきに応じて報酬・ペナルティを付与する
        if self.old_height_variance > 0.0:
            if self.gameManager.height_variance <= self.old_height_variance:
                reward += (self.old_height_variance - self.gameManager.height_variance) * 1
            else:
                reward -= (self.gameManager.height_variance - self.old_height_variance) * 2
                
            if self.gameManager.height_variance > 20.0:
                reward -= 0.5
        
        self.old_under_empty_block_num = self.gameManager.under_empty_block_num
        self.old_all_empty_block_num = self.gameManager.all_empty_block_num
        self.old_block_normalized_variance = self.gameManager.block_variance
        self.old_height_variance = self.gameManager.height_variance
            
        return reward
