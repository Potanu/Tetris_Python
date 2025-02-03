# DQNを使った学習スクリプト
import os
from Scenes import trainEnv
from stable_baselines3 import DQN

# 環境を初期化
env = trainEnv.TrainEnv()

# DQNエージェントを初期化
model = DQN("MlpPolicy", env, verbose=1)

# 学習を開始
model.learn(total_timesteps=100000)

# 学習済みモデルを保存
save_path = os.path.join(os.pardir, "models", "dqn_agent")
model.save(save_path)
