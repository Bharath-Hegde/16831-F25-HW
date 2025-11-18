#!/usr/bin/env python3
import os
import sys
import argparse
import matplotlib.pyplot as plt
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

def get_eval_returns(exp_dir):
    """Extract Eval_AverageReturn from tensorboard logs."""
    # Find the event file
    event_file = None
    for f in os.listdir(exp_dir):
        if f.startswith('events.out.tfevents'):
            event_file = os.path.join(exp_dir, f)
            break

    if event_file is None:
        raise FileNotFoundError(f"No event file found in {exp_dir}")

    # Load tensorboard data
    ea = EventAccumulator(event_file)
    ea.Reload()

    # Extract Eval AverageReturn
    eval_returns = ea.Scalars('Eval_AverageReturn')
    eval_steps = [s.step for s in eval_returns]
    eval_values = [s.value for s in eval_returns]

    return eval_steps, eval_values

def plot_eval_returns(exp_dirs, title=None, output_name=None, target_return=None, labels=None):
    """Plot Eval_AverageReturn from one or more experiment directories."""

    # Create plot
    plt.figure(figsize=(10, 6))

    colors = ['r', 'b', 'g', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']

    for i, exp_dir in enumerate(exp_dirs):
        eval_steps, eval_values = get_eval_returns(exp_dir)

        # Generate label from directory name or use provided label
        if labels and i < len(labels):
            label = labels[i]
        else:
            label = os.path.basename(exp_dir)

        color = colors[i % len(colors)]
        plt.plot(eval_steps, eval_values, f'{color}-o', label=label, linewidth=2, markersize=4)

        print(f"\n{label}:")
        print(f"  Eval_AverageReturn: {eval_values}")

    # Add target return line if specified
    if target_return is not None:
        plt.axhline(y=target_return, color='k', linestyle='--', linewidth=2, label=f'Target Return ({target_return})')

    plt.xlabel('Iteration')
    plt.ylabel('Eval Average Return')

    # Use provided title or generate default
    if title is None:
        if len(exp_dirs) == 1:
            exp_name = os.path.basename(exp_dirs[0])
            title = f'{exp_name}'
        else:
            title = 'Eval Average Return Comparison'
    plt.title(title)

    plt.legend()
    plt.grid(True, alpha=0.3)

    # Save plot
    if len(exp_dirs) == 1:
        output_path = os.path.join(exp_dirs[0], 'train_eval_comparison.pdf')
        plt.savefig(output_path, bbox_inches='tight')
        print(f"\nPlot saved to: {output_path}")

    # Also save with custom name if provided
    if output_name:
        # Save as PDF for vector graphics
        if not output_name.endswith('.pdf'):
            output_name = output_name.rsplit('.', 1)[0] + '.pdf'
        plt.savefig(output_name, bbox_inches='tight')
        print(f"Plot saved to: {output_name}")

    plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot Eval Average Returns from experiment logs')
    parser.add_argument('exp_dirs', type=str, nargs='+', help='Path(s) to experiment directory(ies)')
    parser.add_argument('--title', type=str, default=None, help='Custom plot title')
    parser.add_argument('--output', type=str, default=None, help='Output path for plot')
    parser.add_argument('--target', type=float, default=None, help='Target return value to draw as horizontal dotted line')
    parser.add_argument('--labels', type=str, nargs='+', default=None, help='Custom labels for each experiment')

    args = parser.parse_args()
    plot_eval_returns(args.exp_dirs, args.title, args.output, args.target, args.labels)
