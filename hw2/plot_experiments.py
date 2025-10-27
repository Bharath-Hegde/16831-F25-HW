#!/usr/bin/env python3
"""
General script to extract data from TensorBoard event files and create plots for HW2.
Supports all experiments with clean styling (no markers).
"""

import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
import argparse

def extract_scalar_data(event_file_path, scalar_name='Eval_AverageReturn'):
    """Extract scalar data from a TensorBoard event file."""
    try:
        ea = EventAccumulator(event_file_path)
        ea.Reload()
        
        if scalar_name in ea.Tags()['scalars']:
            scalar_events = ea.Scalars(scalar_name)
            steps = [s.step for s in scalar_events]
            values = [s.value for s in scalar_events]
            return steps, values
        else:
            print(f"Scalar '{scalar_name}' not found in {event_file_path}")
            print(f"Available scalars: {ea.Tags()['scalars']}")
            return [], []
    except Exception as e:
        print(f"Error reading {event_file_path}: {e}")
        return [], []

def plot_experiment(experiment_dir, output_path, title, experiment_type="general"):
    """Create plots for any experiment with clean styling."""
    
    # Find all experiment subdirectories
    exp_dirs = glob.glob(os.path.join(experiment_dir, "*"))
    exp_dirs = [d for d in exp_dirs if os.path.isdir(d)]
    
    plt.figure(figsize=(10, 6))
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
    labels = []
    
    for i, exp_dir in enumerate(sorted(exp_dirs)):
        exp_name = os.path.basename(exp_dir)
        
        # Find the events file
        events_files = glob.glob(os.path.join(exp_dir, "events.out.tfevents.*"))
        
        if not events_files:
            print(f"No events file found in {exp_dir}")
            continue
            
        events_file = events_files[0]
        steps, values = extract_scalar_data(events_file)
        
        if steps and values:
            # Extract configuration from directory name based on experiment type
            if experiment_type == "cartpole":
                if 'no_rtg_dsa' in exp_name:
                    label = 'No RTG, DSA'
                elif 'rtg_dsa' in exp_name:
                    label = 'RTG, DSA'
                elif 'rtg_na' in exp_name:
                    label = 'RTG, No DSA'
                else:
                    label = exp_name
            elif experiment_type == "inverted_pendulum":
                # Extract batch size and learning rate from directory name
                # Format: q2_b<batch>_r<rate>_InvertedPendulum-v4_<timestamp>
                parts = exp_name.split('_')
                batch_size = None
                lr = None
                for part in parts:
                    if part.startswith('b') and part[1:].replace('.', '').isdigit():
                        batch_size = part[1:]
                    elif part.startswith('r') and part[1:].replace('.', '').isdigit():
                        lr = part[1:]
                
                if batch_size and lr:
                    label = f'Batch={batch_size}, LR={lr}'
                else:
                    label = exp_name
            elif experiment_type == "lunar_lander":
                label = 'LunarLander'
            elif experiment_type == "half_cheetah":
                # Extract configuration details
                if 'search' in exp_name:
                    if 'rtg' in exp_name and 'nnbaseline' in exp_name:
                        label = 'RTG + NN Baseline'
                    elif 'rtg' in exp_name:
                        label = 'RTG'
                    elif 'nnbaseline' in exp_name:
                        label = 'NN Baseline'
                    else:
                        label = 'Baseline'
                else:
                    # Extract batch and lr from optimal runs
                    parts = exp_name.split('_')
                    batch_size = None
                    lr = None
                    for part in parts:
                        if part.startswith('b') and part[1:].replace('.', '').isdigit():
                            batch_size = part[1:]
                        elif part.startswith('r') and part[1:].replace('.', '').isdigit():
                            lr = part[1:]
                    
                    if batch_size and lr:
                        if 'rtg' in exp_name and 'nnbaseline' in exp_name:
                            label = f'Optimal (b={batch_size}, lr={lr}) + RTG + NN'
                        elif 'rtg' in exp_name:
                            label = f'Optimal (b={batch_size}, lr={lr}) + RTG'
                        elif 'nnbaseline' in exp_name:
                            label = f'Optimal (b={batch_size}, lr={lr}) + NN'
                        else:
                            label = f'Optimal (b={batch_size}, lr={lr})'
                    else:
                        label = exp_name
            elif experiment_type == "hopper":
                # Extract lambda value
                if 'lambda' in exp_name:
                    lambda_val = exp_name.split('lambda')[-1].split('_')[0]
                    label = f'λ = {lambda_val}'
                else:
                    label = exp_name
            else:
                label = exp_name
                
            plt.plot(steps, values, color=colors[i % len(colors)], 
                    linewidth=1.5, label=label, alpha=0.8)
            labels.append(label)
        else:
            print(f"No data found for {exp_name}")
    
    plt.xlabel('Iteration', fontsize=12)
    plt.ylabel('Average Return', fontsize=12)
    plt.title(f'{title}', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10, framealpha=0.9)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Plot saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Extract plots from TensorBoard data')
    parser.add_argument('--data_dir', type=str, 
                       default='/Users/bharath/Desktop/Fall25/Robot Learning/16831-F25-HW/hw2/data',
                       help='Path to data directory')
    parser.add_argument('--output_dir', type=str,
                       default='/Users/bharath/Desktop/Fall25/Robot Learning/16831-F25-HW/hw2/plots',
                       help='Path to output directory')
    parser.add_argument('--experiment', type=str, choices=['1', '2', '3', '4', '5', 'all'],
                       default='all', help='Which experiment to plot (1-5 or all)')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    if args.experiment in ['1', 'all']:
        # Experiment 1: CartPole
        cartpole_dir = os.path.join(args.data_dir, 'Experiment1(CartPole)')
        
        # Small batch plot
        small_batch_dir = os.path.join(cartpole_dir, 'SmallBatch')
        small_batch_output = os.path.join(args.output_dir, 'Experiment1', 'cartpole_small_batch.png')
        plot_experiment(small_batch_dir, small_batch_output, 
                       'CartPole - Small Batch', 'cartpole')
        
        # Large batch plot
        large_batch_dir = os.path.join(cartpole_dir, 'LargeBatch')
        large_batch_output = os.path.join(args.output_dir, 'Experiment1', 'cartpole_large_batch.png')
        plot_experiment(large_batch_dir, large_batch_output, 
                       'CartPole - Large Batch', 'cartpole')
    
    if args.experiment in ['2', 'all']:
        # Experiment 2: InvertedPendulum
        inverted_pendulum_dir = os.path.join(args.data_dir, 'Experiment2(InvertedPendulum)')
        inverted_pendulum_output = os.path.join(args.output_dir, 'Experiment2', 'inverted_pendulum.png')
        plot_experiment(inverted_pendulum_dir, inverted_pendulum_output, 
                       'InvertedPendulum', 'inverted_pendulum')
    
    if args.experiment in ['3', 'all']:
        # Experiment 3: LunarLander
        lunar_lander_dir = os.path.join(args.data_dir, 'Experiment3(LunarLander)')
        lunar_lander_output = os.path.join(args.output_dir, 'Experiment3', 'lunar_lander.png')
        plot_experiment(lunar_lander_dir, lunar_lander_output, 
                       'LunarLander', 'lunar_lander')
    
    if args.experiment in ['4', 'all']:
        # Experiment 4: HalfCheetah
        half_cheetah_dir = os.path.join(args.data_dir, 'Experiment4(HalfCheetah)')
        
        # Search plots
        search_dir = os.path.join(half_cheetah_dir, 'Search')
        if os.path.exists(search_dir):
            search_output = os.path.join(args.output_dir, 'Experiment4', 'half_cheetah_search.png')
            plot_experiment(search_dir, search_output, 
                           'HalfCheetah - Search', 'half_cheetah')
        
        # Optimal plots
        optimal_dir = os.path.join(half_cheetah_dir, 'Optimal')
        if os.path.exists(optimal_dir):
            optimal_output = os.path.join(args.output_dir, 'Experiment4', 'half_cheetah_optimal.png')
            plot_experiment(optimal_dir, optimal_output, 
                           'HalfCheetah - Optimal', 'half_cheetah')
    
    if args.experiment in ['5', 'all']:
        # Experiment 5: Hopper
        hopper_dir = os.path.join(args.data_dir, 'Experiment5(Hopper)')
        hopper_output = os.path.join(args.output_dir, 'Experiment5', 'hopper.png')
        plot_experiment(hopper_dir, hopper_output, 
                       'Hopper - GAE Lambda Comparison', 'hopper')

if __name__ == '__main__':
    main()
