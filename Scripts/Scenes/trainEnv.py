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
            "fall_mino_matrix": spaces.Box(low=-1, high=7, shape=(define.BOARD_GRID_NUM[1], define.BOARD_GRID_NUM[0]), dtype=np.int8),
            "rotation": spaces.Discrete(4),
            "mino_type": spaces.Discrete(len(enum.MinoType)),
            #"block_normalized_variance": spaces.Box(low=0.0, high=3969.0, shape=(1,), dtype=np.float16),
            #"block_height_diff": spaces.Box(low=0.0, high=define.GAME_GRID_NUM[1], shape=(1,), dtype=np.float16)
        })
        
        
        # アクション空間の定義
        self.action_space = spaces.Discrete(len(enum.ACTION_SPACE_TYPE))
        
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
        self.elapsed_step = 0
        self.block_normalized_variance = 0.0  # ブロックの分散値
        self.block_height_diff = 0.0    # ブロックの最大段数-平均段数
        return self.get_state(), {}
    
    def step(self, action):
        # エージェントが選択したアクションを元にキーの押下状態を更新
        self.update_key_input(action)
        
        # ゲーム進行
        self.gameManager.active_func()
        
        # 状態を取得
        state = self.get_state()
        
        # 報酬を計算
        reward = self.get_reward()
        
        # ゲーム終了フラグを確認
        done = self.gameManager.game_state == enum.GameState.GAME_OVER
        self.elapsed_step += 1
        
        # エピソードが途中で切り捨てられたかどうか
        truncated = False   # ここでは常にFalseにしておく
        
        # 追加情報
        info = {}   # ここでは特になし
        
        # デバッグ表示
        if self.gameManager.game_state == enum.GameState.CLEAR_LINE:
            self.render(reward)
        elif self.gameManager.game_state == enum.GameState.DROP_LINE:
            self.render(reward)
        elif self.gameManager.game_state == enum.GameState.PROCESS_LANDING:
            self.render_counter += 1
            if self.render_counter % 1000 != 0:
                self.render(reward)
            
        
        return state, reward, done, truncated, info
    
    # エージェントが選択したアクションを元にキーの押下状態を更新
    def update_key_input(self, action):
        self.gameManager.key_input_state_is_up[:] = [False] * len(enum.KeyType)
        match action:
            case enum.ACTION_SPACE_TYPE.MOVE_RIGHT:
                self.gameManager.key_input_state_is_up[enum.KeyType.D] = True
            case enum.ACTION_SPACE_TYPE.MOVE_LEFT:
                self.gameManager.key_input_state_is_up[enum.KeyType.A] = True
            case enum.ACTION_SPACE_TYPE.ROTATE_RIGHT:
                self.gameManager.key_input_state_is_up[enum.KeyType.RIGHT] = True
            case enum.ACTION_SPACE_TYPE.ROTATE_LEFT:
                self.gameManager.key_input_state_is_up[enum.KeyType.LEFT] = True
            case enum.ACTION_SPACE_TYPE.HARD_DROP:
                self.gameManager.key_input_state_is_up[enum.KeyType.W] = True
    
    # エージェントが状況を理解するためのゲームデータを返す
    def get_state(self):
        # 観測データを辞書で返す
        index = 0 if self.gameManager.active_mino == None else self.gameManager.active_mino.index
        mino_type = 0 if self.gameManager.active_mino == None else self.gameManager.active_mino.mino_type
        state = {
            "board_matrix": self.gameManager.board_matrix,
            "fall_mino_matrix": self.gameManager.fall_mino_matrix,
            "rotation": index,
            "mino_type": mino_type,
            #"block_normalized_variance": np.array([self.block_normalized_variance], dtype=np.float16),
            #"block_height_diff": np.array([self.block_height_diff], dtype=np.float16)
        }
        
        return state
    
    # エージェントの行動結果に基づく報酬を返す
    def get_reward(self):
        reward = 0
        
        if self.gameManager.game_state == enum.GameState.GAME_OVER:
            # ゲームオーバーの場合、特大ペナルティを与える
            reward += define.GAME_OVER_PENALTY
        elif self.gameManager.game_state == enum.GameState.CLEAR_LINE:
            reward += 10
        elif self.gameManager.game_state == enum.GameState.DROP_LINE:
            # ライン消しが発生した場合、スコアを*10報酬として与える
            combo = self.gameManager.combo + 1
            score_index = len(self.gameManager.clear_line_list) - 1
            reward += define.SCORE_LIST[score_index] * combo * 10
            
            if self.gameManager.check_all_block_clear():
                # 全消ししたらさらに報酬を与える
                reward += define.ALL_BLOCK_CLEAR_REWARD
        elif self.gameManager.game_state == enum.GameState.PROCESS_LANDING:
            # ブロックの分散が小さいほど高い報酬を与える
            block_normalized_variance = self.get_block_normalized_variance()
            
            if self.block_normalized_variance > 0:
                # 分散の範囲に対して線形補間で報酬を設定
                sign = 1 if block_normalized_variance < self.block_normalized_variance else -0.50
                reward += (self.block_normalized_variance - block_normalized_variance) * 10 * sign
                #reward += np.interp(self.block_normalized_variance, [0.0, 0.30, 1.0], [100, 0, -100])
                
                # 高さペナルティ
                self.block_height_diff = self.get_block_height_diff()
                
                # ブロックの最大段数と平均段数の差が3段未満かどうかで報酬orペナルティ
                sign = 1 if self.block_height_diff < 3.0 else -0.50
                reward += self.block_height_diff * 10 * sign
            
            self.block_normalized_variance = block_normalized_variance
        
        if self.elapsed_step > 0 and self.elapsed_step % 100 == 0:
            # 長く生き延びて欲しいので、100ステップ生き延びるごとに報酬を与える
            reward += 50
        
        return reward

    # ブロックの分散を正規化したものを返す
    def get_block_normalized_variance(self):
        block_array = np.where(self.gameManager.board_matrix == 0, self.gameManager.fall_mino_matrix, self.gameManager.board_matrix)
        block_array = block_array[1:-1, 1:-1]   # 外周を削除
        block_list = np.zeros(define.GAME_GRID_NUM[0], dtype=int)   # 列ごとのブロック数を格納
        for x in range(0, define.GAME_GRID_NUM[0]):
            for y in range(0, define.GAME_GRID_NUM[1]):
                if (block_array[y][x] > enum.MinoType.NONE):
                    block_list[x] += 1
        
        # 分散を計算
        variance = np.var(block_list)
        
        # 最大分散を計算
        max_variance = (np.max(block_list) - np.min(block_list)) ** 2 / 4
        
        # 正規化分散を計算
        normalized_variance = variance / max_variance
        
        return normalized_variance

    # 積みあがったブロックの最大段数から平均段数を引いた値を返す
    def get_block_height_diff(self):
        block_array = np.where(self.gameManager.board_matrix == 0, self.gameManager.fall_mino_matrix, self.gameManager.board_matrix)
        block_array = block_array[1:-1, 1:-1]   # 外周を削除
        block_num = 0   # ブロックの数
        block_max_y_index = define.GAME_GRID_NUM[1] - 1 # 最も高いブロックのyインデックス
        for y in range(0, define.GAME_GRID_NUM[1]):
            for x in range(0, define.GAME_GRID_NUM[0]):
                if (block_array[y][x] > enum.MinoType.NONE):
                    block_num += 1
                    
                    if y < block_max_y_index:
                        block_max_y_index = y

        max_height = define.GAME_GRID_NUM[1] - block_max_y_index
        avg_height = block_num / define.GAME_GRID_NUM[0]
        
        return max_height - avg_height
        
    # デバッグ表示
    def render(self, reward):
        # ボード状態の表示
        all_array = np.where(self.gameManager.board_matrix == 0, self.gameManager.fall_mino_matrix, self.gameManager.board_matrix)
        # 外周を削除するために内側を取り出す
        board_array = all_array[1:-1, 1:-1]
        print("=" * 20)
        print(board_array)
        print("=" * 20)
        
        # 報酬表示
        print(f"\nnormalized_variance: {self.block_normalized_variance}") 
        print(f"height_diff: {self.block_height_diff}") 
        print(f"Reward: {reward}") 
        