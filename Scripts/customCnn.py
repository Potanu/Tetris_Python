import torch
import torch.nn as nn
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

class CustomCNN(BaseFeaturesExtractor):
    def __init__(self, observation_space, features_dim=128):
        super(CustomCNN, self).__init__(observation_space, features_dim)
        
        # CNN
        # 21x10 の盤面データ
        n_input_channels_board = 3  # 3チャンネル（board_matrix, ghost_mino_matrix, current_mino_matrix）
        self.cnn_board = nn.Sequential(
            nn.Conv2d(n_input_channels_board, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Flatten()
        )

        # 4x4 のミノデータ
        n_input_channels_mino = 1  # 1チャンネル（next_mino_matrix）
        self.cnn_mino = nn.Sequential(
            nn.Conv2d(n_input_channels_mino, 16, kernel_size=2, stride=1),
            nn.ReLU(),
            nn.Flatten()
        )

        # MLPで処理するデータの次元数
        board_size = observation_space["board"].shape[0]
        current_mino_size = observation_space["current_mino"].shape[0]
        next_mino_size = observation_space["next_mino"].shape[0]

        mlp_input_size = board_size + current_mino_size + next_mino_size
        self.mlp = nn.Sequential(
            nn.Linear(mlp_input_size, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU()
        )

        # CNN の出力サイズを確認（ダミー入力で計算）
        with torch.no_grad():
            dummy_board = torch.zeros(1, n_input_channels_board, 21, 10)
            board_out_size = self.cnn_board(dummy_board).shape[1]

            dummy_mino = torch.zeros(1, n_input_channels_mino, 4, 4)
            mino_out_size = self.cnn_mino(dummy_mino).shape[1]

        # 最終的な特徴ベクトルを作るための全結合層
        self.linear = nn.Linear(board_out_size + mino_out_size + 16, features_dim)

    def forward(self, observations):
        # board_matrix、ghost_mino_matrix、current_mino_matrixを取得（形状: (batch, 210) → (batch, 1, 21, 10)）
        board_matrix = observations["board_matrix"].reshape(-1, 1, 21, 10)
        ghost_mino_matrix = observations["ghost_mino_matrix"].reshape(-1, 1, 21, 10) * -1  # ゴーストを -1 に
        current_mino_matrix = observations["current_mino_matrix"].reshape(-1, 1, 21, 10)
        board_input = torch.cat([board_matrix, ghost_mino_matrix, current_mino_matrix], dim=1)  # 3チャンネル入力
        board_features = self.cnn_board(board_input)

        # next_mino_matrix を取得（形状: (batch, 16) → (batch, 1, 4, 4)）
        next_mino_matrix = observations["next_mino_matrix"].reshape(-1, 1, 4, 4)
        mino_input = torch.cat([next_mino_matrix], dim=1)  # 1チャンネル入力
        mino_features = self.cnn_mino(mino_input)

        # 数値情報（board, current_mino, next_mino）を MLP で処理
        board_stats = observations["board"]
        current_mino = observations["current_mino"]
        next_mino = observations["next_mino"]

        mlp_input = torch.cat([board_stats, current_mino, next_mino], dim=1)
        mlp_features = self.mlp(mlp_input)

        # 全ての特徴を結合
        combined_features = torch.cat([board_features, mino_features, mlp_features], dim=1)
        return self.linear(combined_features)
