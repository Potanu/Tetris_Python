# DQNを使った学習スクリプト
import os
from Scenes import trainEnv
from stable_baselines3 import DQN

# 環境を初期化
env = trainEnv.TrainEnv()

# DQNエージェントを初期化
model = DQN(
    "MlpPolicy",
    env,
    exploration_initial_eps=1.0,  # 最初の行動のランダム率
    exploration_final_eps=0.05,   # 最終的に0.05%の確率でランダム行動
    exploration_fraction=0.1,     # 10% の学習期間でランダム率を減少
    verbose=1)

# 学習を開始
model.learn(total_timesteps=100000)

# 学習済みモデルを保存
save_path = os.path.join(os.pardir, "Models", "dqn_agent")
model.save(save_path)
