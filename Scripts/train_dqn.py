# DQNを使った学習スクリプト
import os
from Scenes import trainEnv
from stable_baselines3 import DQN

# 環境を初期化
env = trainEnv.TrainEnv()

# 学習を開始
# DQNエージェントを初期化
model = DQN(
    "MultiInputPolicy",
    env,
    buffer_size=500000,          # リプレイバッファ容量
    exploration_initial_eps=1.0,  # 最初の行動のランダム率
    exploration_final_eps=0.050,   # 最終的に0.05%の確率でランダム行動
    exploration_fraction=0.10,     # 10% の学習期間でランダム率を減少
    verbose=1)


model.learn(total_timesteps=500000)

# 学習済みモデルを保存
save_path = os.path.join(os.pardir, "Models", "dqn_agent")
model.save(save_path)
