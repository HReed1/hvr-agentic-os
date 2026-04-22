import matplotlib.pyplot as plt
import numpy as np

# Data
tasks = ['Small', 'Medium', 'Large', 'Fullstack']
swarm_inf = [29, 21, 18, 25]
solo_inf = [25, 28, 26, 46]

swarm_tok = [285484, 225288, 191314, 253565]
solo_tok = [128462, 170717, 137223, 1491205]

# Aesthetics (Premium Dark Mode)
bg_color = '#0d1117'
grid_color = '#30363d'
text_color = '#c9d1d9'
swarm_color = '#58a6ff' # Blue for Swarm
solo_color = '#f85149'  # Red for Solo

plt.style.use('dark_background')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), facecolor=bg_color)
fig.patch.set_facecolor(bg_color)

x = np.arange(len(tasks))
width = 0.35

# Subplot 1: Inferences
ax1.set_facecolor(bg_color)
rects1 = ax1.bar(x - width/2, swarm_inf, width, label='Swarm', color=swarm_color, edgecolor='none', alpha=0.9)
rects2 = ax1.bar(x + width/2, solo_inf, width, label='Solo (God-Mode)', color=solo_color, edgecolor='none', alpha=0.9)

ax1.set_ylabel('Total Inferences', color=text_color, fontsize=12)
ax1.set_title('Architectural Stability (Inference Count)', color=text_color, fontsize=14, pad=15)
ax1.set_xticks(x)
ax1.set_xticklabels(tasks, color=text_color, fontsize=11)
ax1.legend(facecolor=bg_color, edgecolor=grid_color, labelcolor=text_color)
ax1.grid(True, axis='y', color=grid_color, linestyle='--', alpha=0.7)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['left'].set_color(grid_color)
ax1.spines['bottom'].set_color(grid_color)

# Add values on bars
for rect in rects1 + rects2:
    height = rect.get_height()
    ax1.annotate(f"{int(height)}",
                 xy=(rect.get_x() + rect.get_width() / 2, height),
                 xytext=(0, 3),  # 3 points vertical offset
                 textcoords="offset points",
                 ha='center', va='bottom', color=text_color, fontsize=10)

# Subplot 2: Token Window
ax2.set_facecolor(bg_color)
rects3 = ax2.bar(x - width/2, [t / 1000 for t in swarm_tok], width, label='Swarm', color=swarm_color, edgecolor='none', alpha=0.9)
rects4 = ax2.bar(x + width/2, [t / 1000 for t in solo_tok], width, label='Solo (God-Mode)', color=solo_color, edgecolor='none', alpha=0.9)

ax2.set_ylabel('Tokens Evaluated (Thousands)', color=text_color, fontsize=12)
ax2.set_title('Context Bleed (Tool Input Tokens)', color=text_color, fontsize=14, pad=15)
ax2.set_xticks(x)
ax2.set_xticklabels(tasks, color=text_color, fontsize=11)
ax2.legend(facecolor=bg_color, edgecolor=grid_color, labelcolor=text_color)
ax2.grid(True, axis='y', color=grid_color, linestyle='--', alpha=0.7)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_color(grid_color)
ax2.spines['bottom'].set_color(grid_color)

# Add values on bars
for rect in rects3 + rects4:
    height = rect.get_height()
    ax2.annotate(f"{int(height)}k",
                 xy=(rect.get_x() + rect.get_width() / 2, height),
                 xytext=(0, 3),  # 3 points vertical offset
                 textcoords="offset points",
                 ha='center', va='bottom', color=text_color, fontsize=10)

# The Inflection Point Marker
ax2.annotate('The Paradigm Inflection Point\n(Solo Token Explosion)', 
            xy=(3 + width/2, 1490), xytext=(1.5, 1200),
            arrowprops=dict(facecolor=text_color, shrink=0.05, width=2, headwidth=8),
            ha='center', color='#ff7b72', fontsize=12, fontweight='bold',
            bbox=dict(boxstyle="round4,pad=0.5", fc=bg_color, ec='#ff7b72', lw=2))

plt.suptitle('Evaluating Swarm Intelligence vs Monolithic AI Architectures', color=text_color, fontsize=18, y=1.02)
plt.tight_layout()

output_path = 'docs/comparisons/THE_INFLECTION_POINT.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), transparent=False)
print(f"Graph successfully generated at {output_path}")
