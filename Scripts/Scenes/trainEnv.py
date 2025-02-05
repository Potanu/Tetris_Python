import gymnasium
from gymnasium import spaces
import numpy as np
from Utilities import define
from Utilities import enum
from Scenes import gameManager

class TrainEnv(gymnasium.Env):
    def __init__(self):
        super(TrainEnv, self).__init__()
        
        # ボード状態空間
        width = define.BOARD_GRID_NUM[0]
        height = define.BOARD_GRID_NUM[1]
        
         # 観察空間をフラットな Box 型に統一（ボード配列・操作ミノ配列・コンボ数）
        self.observation_space = spaces.Box(
            low=-1, high=7, shape=(2 * height * width + 1,), dtype=np.int32
        )
        
        # アクション空間の定義
        self.action_space = spaces.Discrete(len(enum.ACTION_SPACE_TYPE))
        
        # ゲームの初期化
        self.gameManager = gameManager.GameManager()
        self.reset()
    
    # エピソードリセット時の処理
    def reset(self, seed=None, **kwarg):
        train_flag = True
        self.gameManager.init(train_flag)
        self.done = False
        self.render_counter = 0
        self.elapsed_step = 0
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
        # 状態空間としてフラット化した値を返す
        state = np.concatenate([
            self.gameManager.board_matrix.flatten(),
            self.gameManager.fall_mino_matrix.flatten(),
            [self.gameManager.combo]
        ])
        
        return state
    
    # エージェントの行動結果に基づく報酬を返す
    def get_reward(self):
        reward = 0
        
        if self.gameManager.game_state == enum.GameState.GAME_OVER:
            # ゲームオーバーの場合、特大ペナルティを与える
            reward += define.GAME_OVER_PENALTY
        elif self.gameManager.game_state == enum.GameState.DROP_LINE:
            # ライン消しが発生した場合、スコアをそのまま報酬として与える
            combo = self.gameManager.combo + 1
            score_index = len(self.gameManager.clear_line_list) - 1
            reward += define.SCORE_LIST[score_index] * combo
            
            if self.gameManager.check_all_block_clear():
                # 全消ししたらさらに報酬を与える
                reward += define.ALL_BLOCK_CLEAR_REWARD
        elif self.gameManager.game_state == enum.GameState.PROCESS_LANDING:
            # 接地したとき、操作ブロックの下に隙間が出来てしまった場合ペナルティを与える
            # 底に設置したかどうかを判定
            bottom_state = False
            for x in range(1, define.BOARD_GRID_NUM[0] - 1):
                y = define.GAME_GRID_NUM[1]
                if (self.gameManager.fall_mino_matrix[y][x] > enum.MinoType.NONE):
                    bottom_state = True
                    break
                
            penalty_rate = 1.0
            if (self.gameManager.active_mino == enum.MinoType.S or
                self.gameManager.active_mino == enum.MinoType.Z):
                # S・Zミノは難しい形をしているのでペナルティを緩める。底に接地する場合はペナルティを0にする。
                penalty_rate = 0.0 if bottom_state else 0.50

            # 操作ブロックの下に隙間が発生したかどうかを判定する
            pairs = set()
            # 現在の操作ブロック各列を下から検索し、一番下に位置するブロック座標を見つけたら保存する
            for x in range(1, define.BOARD_GRID_NUM[0] - 1):
                for y in reversed(range(2, define.GAME_GRID_NUM[1])): # デッドラインから上と、最下段の列は無視する
                    if (self.gameManager.fall_mino_matrix[y][x] > enum.MinoType.NONE):
                        pairs.add((x,y))
                        break
            
            # 操作ブロックの下にある空きブロックの数をカウントする
            empty_block_counter = 0
            for x, y in pairs:
                for y_grid in range(y + 1, define.GAME_GRID_NUM[1]):
                    if (self.gameManager.fall_mino_matrix[y_grid][x] > enum.MinoType.NONE):
                        # 空きブロックでなければ次の列へ
                        break
                    empty_block_counter += 1
            
            if empty_block_counter == 0:
                reward += define.NO_EMPTY_BLOCK_REWARD
            elif (empty_block_counter > 0 and penalty_rate == 0.0):
                reward += empty_block_counter * define.EMPTY_BLOCK_PENALTY * penalty_rate
        
        if self.elapsed_step > 0 and self.elapsed_step % 100:
            # 長く生き延びて欲しいので、100ステップ生き延びるごとに報酬を与える
            reward += 5
        
        return reward

    # デバッグ表示
    def render(self, reward):
        self.render_counter += 1
        if self.render_counter % 500 != 0:
            return
        
        # ボード状態の表示
        all_array = np.where(self.gameManager.board_matrix == 0, self.gameManager.fall_mino_matrix, self.gameManager.board_matrix)
        # 外周を削除するために内側を取り出す
        board_array = all_array[1:-1, 1:-1]
        print("=" * 20)
        print(board_array)
        print("=" * 20)
        
        # 報酬表示
        #print(f"\nReward: {reward}") 
        