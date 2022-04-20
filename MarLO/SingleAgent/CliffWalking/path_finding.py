# 80 x 80 maze
# Agent starts in the middle (40, 40)
rows, cols = (80, 80)
map = [["Unexplored"] * cols] * rows

# Initialize Lava
for i in range(5):
    for j in range(13):
        map[39 - j][39 - i] = "Lava"

# Agent Starting Location
map[40][40] = "Floor"

# Sandstone Path
for i in range(1, 3):
    for j in range(1, 12):
        map[40 - j][40 - i] = "Floor"

# Goal
map[29][40] = "Goal"
