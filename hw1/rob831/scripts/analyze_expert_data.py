#!/usr/bin/env python3

import pickle
import numpy as np
import os

def analyze_expert_data(file_path):
    """Load expert data and calculate returns for each trajectory"""
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    
    # Data is a list of 2 trajectories, each trajectory is a dict with 'reward' key
    returns = [np.sum(trajectory['reward']) for trajectory in data]
    return returns


environments = ['Ant-v2', 'Humanoid-v2', 'Walker2d-v2', 'Hopper-v2', 'HalfCheetah-v2']
expert_data_path = './rob831/expert_data'

print(f"{'Environment':<15} {'Mean':<10} {'Std':<10} {'Returns':<20}")
print("-" * 60)

for env in environments:
    file_path = os.path.join(expert_data_path, f'expert_data_{env}.pkl')
    returns = analyze_expert_data(file_path)
    mean_return = np.mean(returns)
    std_return = np.std(returns)
    print(f"{env:<15} {mean_return:<10.2f} {std_return:<10.2f} {returns}")
