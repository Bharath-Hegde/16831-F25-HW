import matplotlib.pyplot as plt
import numpy as np

# Data from 2.1logs.txt
iterations = np.arange(0, 8)

# Ant-v2 data
ant_returns = [2357.03, 4532.50, 4737.56, 4764.85, 4644.42, 4618.45, 4737.69, 4704.22]
ant_stds = [1869.77, 169.10, 70.85, 105.33, 97.47, 58.48, 39.77, 113.93]
ant_expert = 4713.65
ant_bc = 2357.03

# Hopper-v2 data
hopper_returns = [575.73, 1402.36, 1873.33, 1811.18, 3688.47, 3767.43, 3767.98, 3764.95]
hopper_stds = [315.91, 318.89, 577.04, 425.71, 26.84, 6.03, 4.11, 7.84]
hopper_expert = 3772.67
hopper_bc = 575.73

# Create subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Ant-v2 plot
ax1.errorbar(iterations, ant_returns, yerr=ant_stds, marker='o', capsize=5, capthick=2, 
             linewidth=2, markersize=8, label='DAgger', color='blue')
ax1.axhline(y=ant_expert, color='red', linestyle='--', linewidth=2, label='Expert')
ax1.axhline(y=ant_bc, color='green', linestyle=':', linewidth=2, label='BC')
ax1.set_xlabel('DAgger Iterations', fontsize=12)
ax1.set_ylabel('Mean Return', fontsize=12)
ax1.set_title('Ant-v2', fontsize=14)
ax1.grid(True, alpha=0.3)
ax1.legend()
ax1.set_ylim(0, 5000)

# Hopper-v2 plot
ax2.errorbar(iterations, hopper_returns, yerr=hopper_stds, marker='o', capsize=5, capthick=2, 
             linewidth=2, markersize=8, label='DAgger', color='blue')
ax2.axhline(y=hopper_expert, color='red', linestyle='--', linewidth=2, label='Expert')
ax2.axhline(y=hopper_bc, color='green', linestyle=':', linewidth=2, label='BC')
ax2.set_xlabel('DAgger Iterations', fontsize=12)
ax2.set_ylabel('Mean Return', fontsize=12)
ax2.set_title('Hopper-v2', fontsize=14)
ax2.grid(True, alpha=0.3)
ax2.legend()
ax2.set_ylim(0, 4000)

# Overall title
fig.suptitle('DAgger Learning Curves', fontsize=16)

# Improve layout
plt.tight_layout()

# Save the plot
plt.savefig('/Users/bharath/Desktop/Fall25/Robot Learning/16831-F25-HW/hw1/graphs/dagger_learning_curves.png', 
            dpi=300, bbox_inches='tight')
plt.show()

print("DAgger learning curves saved as dagger_learning_curves.png")
