import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import os
import argparse
from play import *
from config_4 import *
import time
# 训练参数
BOARD_SIZE = 11  # 可以通过命令行参数修改
NUM_SIMULATIONS = 200
NUM_SELF_PLAY_GAMES = 50
BATCH_SIZE = 128
LEARNING_RATE = 0.001
NUM_EPOCHS = 10
STATIC_WEIGHT = 0.1

# 解析命令行参数
parser = argparse.ArgumentParser(description='Train Gomoku AI')
parser.add_argument('--board_size', type=int, default=15,
                    help='Size of the Gomoku board (11, 13 or 15)')
args = parser.parse_args()

# 设置棋盘大小
BOARD_SIZE = args.board_size
ACTION_SIZE = BOARD_SIZE * BOARD_SIZE

# 创建模型保存目录
model_dir = "models"
os.makedirs(model_dir, exist_ok=True)
model_path = os.path.join(model_dir, f"gomoku_{BOARD_SIZE}x{BOARD_SIZE}.pth")

# 初始化模型
model = GomokuNet(BOARD_SIZE)
optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

# 初始化静态评估器
static_evaluator = StaticEvaluator(BOARD_SIZE, value_model_X_test, value_model_O_test)

# 训练循环
for round_idx in range(NUM_EPOCHS):
    print(f"\n=== Training Round {round_idx + 1}/{NUM_EPOCHS} ===")
    start_time = time.time()
    # 初始化MCTS
    mcts = MCTS(model, static_evaluator, num_simulations=NUM_SIMULATIONS, static_weight=STATIC_WEIGHT)

    # 自我对弈生成数据
    game = GomokuGame(BOARD_SIZE)
    replay_buffer = []

    for game_idx in range(NUM_SELF_PLAY_GAMES):
        game.reset()
        game_data = []

        while not game.done:
            state = game.get_state()
            action_probs = mcts.run(state, game)
            action = np.random.choice(ACTION_SIZE, p=action_probs)

            game.make_move(action)
            mcts.update_root(action)

            # 保存数据
            game_data.append((state, action_probs, game.current_player))

        # 确定最终奖励
        if game.winner != 0:
            reward = 1 if game.winner == 1 else -1
        else:
            reward = 0

        # 为每一步添加奖励
        for i, (state, action_probs, player) in enumerate(game_data):
            adjusted_reward = reward if player == 1 else -reward
            replay_buffer.append((state, action_probs, adjusted_reward))

        print(f"Game {game_idx + 1} completed, Winner: {game.winner}")

    # 训练模型
    if len(replay_buffer) < BATCH_SIZE:
        print("Not enough data for training")
        continue

    # 准备训练数据
    states = []
    probs = []
    values = []

    # 随机采样一批数据
    indices = np.random.choice(len(replay_buffer), BATCH_SIZE, replace=False)
    for idx in indices:
        state, prob, value = replay_buffer[idx]
        states.append(state)
        probs.append(prob)
        values.append(value)

    states = torch.tensor(np.array(states), dtype=torch.float32)
    probs = torch.tensor(np.array(probs), dtype=torch.float32)
    values = torch.tensor(np.array(values), dtype=torch.float32).unsqueeze(1)

    # 训练
    model.train()
    policy_pred, value_pred = model(states)

    # 计算损失
    policy_loss = -torch.sum(probs * F.log_softmax(policy_pred, dim=1)) / BATCH_SIZE
    value_loss = F.mse_loss(value_pred, values)
    total_loss = policy_loss + value_loss

    # 反向传播
    optimizer.zero_grad()
    total_loss.backward()
    optimizer.step()

    print(f"Loss: {total_loss.item():.4f}, Policy Loss: {policy_loss.item():.4f}, Value Loss: {value_loss.item():.4f}")

    # 减小静态权重
    STATIC_WEIGHT = max(0.01, STATIC_WEIGHT * 0.7)

    elapsed = time.time() - start_time
    remaining = elapsed * (NUM_EPOCHS - round_idx - 1)
    print(f"本轮耗时: {elapsed / 60:.1f}分钟, 预计剩余: {remaining / 60:.1f}分钟")
# 保存最终模型
torch.save(model.state_dict(), model_path)
print(f"Model saved to {model_path}")