#!/usr/bin/env python
"""
Script to plot DQN vs DDQN learning curves from tensorboard logs.
Based on rob831/scripts/read_results.py

Usage:
    python plot/plot_q1_results.py --logdir data/Part1_QLearning --output plot/q1_dqn_vs_ddqn.png
"""

import argparse
import glob
import os
import numpy as np
import matplotlib.pyplot as plt
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator


def get_section_results(file):
    """
    Read tensorboard event file and extract timesteps and returns.
    Returns X (timesteps), Y (average returns)
    """
    # Load the event file
    event_acc = EventAccumulator(file)
    event_acc.Reload()

    X = []
    Y = []

    # Get the scalar data
    if 'Train_EnvstepsSoFar' in event_acc.Tags()['scalars']:
        steps_data = event_acc.Scalars('Train_EnvstepsSoFar')
        X = [s.value for s in steps_data]

    if 'Train_AverageReturn' in event_acc.Tags()['scalars']:
        returns_data = event_acc.Scalars('Train_AverageReturn')
        Y = [r.value for r in returns_data]

    # Ensure X and Y have the same length (take minimum)
    min_len = min(len(X), len(Y))
    X = X[:min_len]
    Y = Y[:min_len]

    return X, Y


def read_experiment(logdir, exp_name):
    """
    Read a single experiment's tensorboard logs.
    """
    exp_path = os.path.join(logdir, exp_name + '*')
    matching_dirs = glob.glob(exp_path)

    if not matching_dirs:
        print(f"Warning: No directories found matching {exp_path}")
        return None, None

    exp_dir = matching_dirs[0]
    eventfile_pattern = os.path.join(exp_dir, 'events*')
    eventfiles = glob.glob(eventfile_pattern)

    if not eventfiles:
        print(f"Warning: No event files found in {exp_dir}")
        return None, None

    eventfile = eventfiles[0]
    print(f"Reading {exp_name} from {eventfile}")

    X, Y = get_section_results(eventfile)
    return np.array(X), np.array(Y)


def interpolate_to_common_steps(data_dict, max_steps=None):
    """
    Interpolate all runs to a common set of timesteps for averaging.
    """
    # Find common timestep range
    all_steps = []
    for X, Y in data_dict.values():
        if X is not None and len(X) > 0:
            all_steps.extend(X)

    if not all_steps:
        return None, None, None

    min_step = min(all_steps)
    if max_steps is None:
        max_step = min([X[-1] for X, Y in data_dict.values() if X is not None and len(X) > 0])
    else:
        max_step = max_steps

    # Create common timesteps (1000 points for smooth curves)
    common_steps = np.linspace(min_step, max_step, 1000)

    # Interpolate each run
    interpolated_returns = []
    for X, Y in data_dict.values():
        if X is not None and len(X) > 0:
            # Interpolate to common timesteps
            interp_Y = np.interp(common_steps, X, Y)
            interpolated_returns.append(interp_Y)

    if not interpolated_returns:
        return None, None, None

    # Calculate mean and std
    interpolated_returns = np.array(interpolated_returns)
    mean_returns = np.mean(interpolated_returns, axis=0)
    std_returns = np.std(interpolated_returns, axis=0)

    return common_steps, mean_returns, std_returns


def plot_comparison(logdir, output_path):
    """
    Plot DQN vs DDQN comparison with error bars.
    """
    # Read DQN experiments (3 seeds)
    dqn_data = {}
    for seed in [1, 2, 3]:
        exp_name = f'q1_dqn_{seed}'
        X, Y = read_experiment(logdir, exp_name)
        if X is not None:
            dqn_data[seed] = (X, Y)

    # Read DDQN experiments (3 seeds)
    ddqn_data = {}
    for seed in [1, 2, 3]:
        exp_name = f'q1_doubledqn_{seed}'
        X, Y = read_experiment(logdir, exp_name)
        if X is not None:
            ddqn_data[seed] = (X, Y)

    # Check if we have data
    if not dqn_data and not ddqn_data:
        print("Error: No experiment data found!")
        return

    # Interpolate to common timesteps and compute statistics
    print("\nProcessing DQN results...")
    dqn_steps, dqn_mean, dqn_std = interpolate_to_common_steps(dqn_data)

    print("Processing DDQN results...")
    ddqn_steps, ddqn_mean, ddqn_std = interpolate_to_common_steps(ddqn_data)

    # Create plot
    plt.figure(figsize=(10, 6))

    # Plot DQN
    if dqn_steps is not None:
        plt.plot(dqn_steps, dqn_mean, label='DQN', linewidth=2, color='blue')
        plt.fill_between(dqn_steps,
                        dqn_mean - dqn_std,
                        dqn_mean + dqn_std,
                        alpha=0.3,
                        color='blue')

    # Plot DDQN
    if ddqn_steps is not None:
        plt.plot(ddqn_steps, ddqn_mean, label='Double DQN', linewidth=2, color='red')
        plt.fill_between(ddqn_steps,
                        ddqn_mean - ddqn_std,
                        ddqn_mean + ddqn_std,
                        alpha=0.3,
                        color='red')

    # Format plot
    plt.xlabel('Timesteps', fontsize=12)
    plt.ylabel('Average Evaluation Return', fontsize=12)
    plt.title('DQN vs Double DQN on LunarLander-v3', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)

    # Use scientific notation for x-axis
    plt.ticklabel_format(style='scientific', axis='x', scilimits=(0,0))

    # Tight layout
    plt.tight_layout()

    # Save plot
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nPlot saved to: {output_path}")

    # Show plot statistics
    if dqn_mean is not None:
        print(f"\nDQN Final Return: {dqn_mean[-1]:.2f} ± {dqn_std[-1]:.2f}")
    if ddqn_mean is not None:
        print(f"DDQN Final Return: {ddqn_mean[-1]:.2f} ± {ddqn_std[-1]:.2f}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot DQN vs DDQN learning curves')
    parser.add_argument('--logdir',
                       type=str,
                       default='data/Part1_QLearning',
                       help='Path to directory containing experiment logs')
    parser.add_argument('--output',
                       type=str,
                       default='plot/q1_dqn_vs_ddqn.png',
                       help='Output path for the plot')

    args = parser.parse_args()

    # Get absolute paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    logdir = os.path.join(project_root, args.logdir) if not os.path.isabs(args.logdir) else args.logdir
    output_path = os.path.join(project_root, args.output) if not os.path.isabs(args.output) else args.output

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"Reading logs from: {logdir}")
    print(f"Output will be saved to: {output_path}")
    print("="*60)

    plot_comparison(logdir, output_path)
