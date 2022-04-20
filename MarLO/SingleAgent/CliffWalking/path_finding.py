import sys
import numpy as np
np.set_printoptions(threshold=sys.maxsize)

# 80 x 80 maze
# Agent starts in the middle (40, 40)
map = np.array([[-1] * 80] * 80)

# Initialize Lava
map[28:42, 39:45] = -100

# Agent Starting Location
map[40, 40] = 0

# Sandstone Path
map[29:41, 41:44] = 0

# Goal
map[29, 40] = 100

print(map[27:43, 38:46])
