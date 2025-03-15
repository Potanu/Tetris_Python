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
            # 配列（盤面・ゴーストミノ・操作ミノ）
            "matrix" : spaces.Box(
                low=0,
                high=1,
                shape=(630,),  # 21* 10 * 3 のサイズに変更
                dtype=np.float32
            ),
            # 盤面の状態
            "board": spaces.Box(
                # 穴の数、ブロックの最大高さ、ブロックの最小高さ、ブロックの平均高さ、高さのばらつき
                # 消したラインの数、消したラインの数（合計）、経過ステップ数
                low=np.array([0] + [0] + [0] + [0] + [0] + [0] + [0] + [0]),
                high=np.array([200] + [20] + [20] + [20] + [100] + [4] + [1000] + [1000]),
                shape=(8,),
                dtype=np.float32
            ),
            # 操作ミノの状態
            "current_mino": spaces.Box(
                # ミノのタイプ、X、Y、回転
                low=np.array([1, 0, 0, 0]),
                high=np.array([7, 10, 19, 3]),
                shape=(4,),
                dtype=np.float32
            ),
        })
        
        # 行動空間を定義
        self.action_space = spaces.Discrete(5)  # 右移動 + 左移動 + 右回転 + 左回転 + ハードドロップ
        
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
        return self.gameManager.get_state(), {}
    
    def step(self, action):
        tmp_action = action
        while (True):
            if self.gameManager.game_state == enum.GameState.FALL and self.gameManager.active_mino != None:
                if self.gameManager.step_num >= 1000:
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
        
        # 経過ステップ数をチェック
        if self.gameManager.step_num <= 10:
            reward += 0.5
        else:
            reward -= (self.gameManager.step_num - 10) * 0.1
        
        if self.gameManager.game_state != enum.GameState.PROCESS_LANDING:
            return reward
        
        # 設置時の処理
        if done:
            # ゲームオーバー
            reward -= 50
            
            if self.gameManager.total_clear_line_num == 0:
                reward -= 50
            else:
                reward += self.gameManager.total_clear_line_num * 10
        
        clear_line_num = self.gameManager.get_clear_line_num()
        if clear_line_num > 0:
            # ライン消しが発生
            reward += clear_line_num * 10

        # ブロックの最大の高さをチェック
        if self.gameManager.max_block_height > 15:
            reward -= 0.3
        elif self.gameManager.max_block_height > 10:
            reward -= 0.1
        
        # 設置したブロック以下に発生した空きブロックの数に応じて報酬・ペナルティを付与する
        if self.gameManager.under_empty_block_num <= self.old_under_empty_block_num:
            # 空きブロック数に変化がない or 空きブロック数が減った
            reward += ((self.old_under_empty_block_num - self.gameManager.under_empty_block_num) + 1) * 1
        else:
            # 空きブロック数が増えた
            reward -= (self.gameManager.under_empty_block_num - self.old_under_empty_block_num) * 2
        
        # ブロックのばらつきに応じて報酬・ペナルティを付与する
        if self.gameManager.height_variance > 20.0:
            reward -= 0.5
        
        self.old_under_empty_block_num = self.gameManager.under_empty_block_num
        
        return reward
