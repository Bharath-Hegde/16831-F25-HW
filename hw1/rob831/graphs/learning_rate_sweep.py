import matplotlib.pyplot as plt
import numpy as np

# Data from 1.3logs.txt
learning_rates = [1e-4, 5e-4, 1e-3, 5e-3, 1e-2, 5e-2]
mean_returns = [-486.82, -613.87, 400.57, 1498.91, 644.30, 152.95]
std_returns = [895.43, 494.12, 313.13, 1372.83, 58.98, 86.50]

# Create the plot
plt.figure(figsize=(10, 6))
plt.errorbar(learning_rates, mean_returns, yerr=std_returns, 
             marker='o', capsize=5, capthick=2, linewidth=2, markersize=8)

# Formatting
plt.xscale('log')
plt.xlabel('Learning Rate', fontsize=12)
plt.ylabel('Mean Return', fontsize=12)
plt.title('Behavioral Cloning Performance vs Learning Rate (Ant-v2)', fontsize=14)
plt.grid(True, alpha=0.3)

# No additional lines needed

# Improve layout
plt.tight_layout()

# Save the plot
plt.savefig('/Users/bharath/Desktop/Fall25/Robot Learning/16831-F25-HW/hw1/graphs/learning_rate_sweep.png', 
            dpi=300, bbox_inches='tight')
plt.show()

print("Graph saved as learning_rate_sweep.png")
