# Plotting Instructions

This file explains how to generate all plots in the submission PDF using the `plot.py` script.

## Usage

### Basic Usage
```bash
python rob831/plot.py <exp_dir1> [exp_dir2 ...] --output <output_path> [additional args]
```

### Examples

```
python rob831/plot.py rob831/data/hw4_q3_cheetah_cheetah-hw4_part1-v0_17-11-2025_04-54-08 --target 250
```

```
python rob831/plot.py rob831/data/hw4_part2_expl_q6_env1_random_PointmassEasy-v0_17-11-2025_23-03-04 rob831/data/hw4_part2_expl_q6_env1_rnd_PointmassEasy-v0_17-11-2025_22-59-41 --output rob831/data/plots_q4/TEST_q6_comparison_easy.pdf --title "RND vs Random Exploration Performance Comparison (PointmassEasy)"
```