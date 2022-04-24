import marlo
import time
import sys
import numpy as np
np.set_printoptions(threshold=sys.maxsize)

# 'C:\\Users\\Ryan.Kinnucan\\MinecraftRLAgent\\MarLO\\Missions\\lava_maze.xml'

# Debug
log = True

# Agent starting and current coordinates
start_coords = (40, 40)
curr_coords = start_coords
# Stores nodes that are unexplored and explored, respectively
frontier = [start_coords]
explored = []
# Stores the moves the agent took to get to its last location
prev_node = { start_coords: None }

# Initialize map of environment with 80 x 80 array
# Agent starts in the middle (40, 40)
map = np.array([[-1] * 80] * 80)

# Initialize Environment
client_pool = [('127.0.0.1', 10000)]
join_tokens = marlo.make('MarLo-CliffWalking-v0',
                        params={
                            "client_pool": client_pool,
                            "tick_length": 30,
                            "agent_names": ["MarLo-Agent-0"],
                            "allowContinuousMovement": True,
                            "allowDiscreteMovement": True,
                        })

assert len(join_tokens) == 1
join_token = join_tokens[0]

env = marlo.init(join_token)
env.reset()

obs, reward, done, info = env.step(0)

# Commands (W/ Indicators of Reliability):

# Numerical, use env.step()
# 0 = Do Nothing                            (Reliable)
# 1 = Move Forward 1 Block                  (Reliable)
# 2 = Move Backward 1 Block                 (Reliable)
# 3 = Turn Right 90 Degrees             (Not Reliable)
# 4 = Turn Left 90 Degrees              (Not Reliable)
# 5 = Look Down                         (Not Reliable)
# 6 = Look Up                           (Not Reliable)

# Human readable, use env.send_command()
# move 1/-1 = Move Forward/Backward 1 Block (Reliable)
# movewest 1 = Move Right 1 Block           (Reliable)
# moveeast 1 = Move Left 1 Block            (Reliable)
# pitch -1/1 = Look Up/Down                 (Reliable)

# Given the agent's current location and a destination,
# send the agent to that destination
def walk_to_node(curr, dest):
    path = reconstruct_path(curr, dest)

    while bool(path):
        if (dest[0] < curr[0] and dest[1] == curr[1]):
            command = "move 1"
        if (dest[0] == curr[0] and dest[1] < curr[1]):
            command = "moveeast 1"
        if (dest[0] > curr[0] and dest[1] == curr[1]):
            command = "move -1"
        if (dest[0] == curr[0] and dest[1] > curr[1]):
            command = "movewest 1"
        env.send_command(command)
        time.sleep(0.5)

def reconstruct_path(curr, dest):
    path = [dest]
    prev = prev_node[dest]
    while prev is not None:
        path.append(prev)
    return path

# While frontier is not empty
while bool(frontier):
    # If agent falls into lava, the environment must
    # be reset so that the agent will respawn
    if (reward == -100): 
        map[curr_coords[0], curr_coords[1]] = -100
        env.reset()
        time.sleep(2)
        
    if (reward == 100): map[curr_coords[0], curr_coords[1]] = 100
    if (reward == 0): map[curr_coords[0], curr_coords[1]] = 0

    explored.append(curr_coords)
    frontier.remove(curr_coords)

    agent_row = curr_coords[0]
    agent_col = curr_coords[1]
    neighbors = [
                    (agent_row - 1, agent_col),
                    (agent_row, agent_col - 1),
                    (agent_row + 1, agent_col),
                    (agent_row, agent_col + 1)
                ]

    # If a neighboring nodes has not already been 
    # explored, then add it to the frontier
    for n in neighbors:
        if ((n not in explored) and (n not in frontier)): frontier.append(n)

    # If frontier is not empty, send the agent to
    # the next unexplored node
    if bool(frontier):
        dest = frontier[0]
        prev_node[dest] = curr_coords
        walk_to_node(curr_coords, dest)
        curr_coords = dest

    time.sleep(1)
    obs, reward, done, info = env.step(0)

    if log:
        print("reward:", reward)
        print("done:", done)
        print("info", info)

env.close()
print(map[27:43, 38:46])
