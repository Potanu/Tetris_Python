# PPOを使った学習スクリプト
import os
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecMonitor
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from Scenes import trainEnv

is_transfer_learning = False     # 転移学習フラグ

# ログフォルダの準備
log_dir = '../logs/'
os.makedirs(log_dir, exist_ok=True)

# 並列化された環境を作成
num_envs = 8
envs = DummyVecEnv([lambda: trainEnv.TrainEnv() for _ in range(num_envs)])
env = VecMonitor(envs, log_dir)

# 学習を開始
start_time = datetime.datetime.now()

if is_transfer_learning:
    # 転移学習
    # 学習済みモデルをロード
    load_path = os.path.join(os.pardir, "Models", "ppo_agent")
    old_model = PPO.load(load_path)
    
    # 新しいハイパーパラメータ設定
    policy_kwargs = dict(
        net_arch=dict(
            pi=[256, 128, 64],  # ポリシーネットワーク
            vf=[256, 128, 64]  # バリューネットワーク
        )
    )

    # 新しいPPOインスタンスを作成
    model = PPO(
        "MultiInputPolicy",
        env,  # 新しい環境
        learning_rate=0.0003,  
        batch_size=512,
        n_epochs=20,
        clip_range=0.2,
        ent_coef=0.3,
        gamma=0.99,
        gae_lambda=0.95,
        policy_kwargs=policy_kwargs,
        verbose=1
    )

    # 既存のモデルを新しいモデルに引き継ぐ
    model.set_parameters(old_model.get_parameters())  # パラメータの引き継ぎ

    # 追加学習
    model.learn(total_timesteps=500000, reset_num_timesteps=False)

else:
    # エージェントを初期化
    policy_kwargs = dict(
        #features_extractor_class=CustomCNN,
        net_arch=dict(
            pi=[256, 128, 64], # ポリシーネットワーク
            vf=[256, 128, 64]  # バリューネットワーク
        )
    )

    model = PPO(
        "MultiInputPolicy",
        env,
        learning_rate=0.0003, 
        batch_size=128,
        n_epochs=10,        
        clip_range=0.2,       
        ent_coef=0.2,        
        gamma=0.99,  
        gae_lambda=0.95,   
        policy_kwargs=policy_kwargs,
        verbose=1)


    model.learn(total_timesteps=500000)

# 学習環境の解放
env.close()

# 学習済みモデルを保存
save_path = os.path.join(os.pardir, "Models", "ppo_agent")
model.save(save_path)

end_time = datetime.datetime.now()
print("開始時刻:", start_time.strftime("%Y-%m-%d %H:%M:%S"))
print("終了時刻:", end_time.strftime("%Y-%m-%d %H:%M:%S"))

# monitor.csvの読み込み
df = pd.read_csv('../logs/monitor.csv', names=['r', 'l','t'])
df = df.drop(range(2)) # 1〜2行目の削除

# 報酬のプロット
x = range(len(df['r']))
y = df['r'].astype(float)
plt.plot(x, y)
plt.xlabel('episode')
plt.ylabel('reward')
plt.show()

# エピソード長のプロット
x = range(len(df['l']))
y = df['l'].astype(float)
plt.plot(x, y)
plt.xlabel('episode')
plt.ylabel('episode len')
plt.show()
