import marlo
import time
import sys
import numpy as np
np.set_printoptions(threshold=sys.maxsize)

# 'C:\\Users\\Ryan.Kinnucan\\MinecraftRLAgent\\MarLO\\Missions\\lava_maze.xml'

# Debug
log = True

# Agent start, goal, and current coordinates
start_coords = (40, 40)
goal_coords = (29, 40)
curr_coords = start_coords
# Stores all nodes that have been explored
explored = []
# Stores the moves the agent took to get to its last location
prev_node = { start_coords: None }
# List storing unexplored nodes and their cost
unexplored = [(start_coords, 0)]

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
    if (curr == dest): return

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
while bool(unexplored):
    # If agent falls into lava, the environment must
    # be reset so that the agent will respawn

    new_coords, cost = unexplored.pop(0)

    walk_to_node(curr_coords, new_coords)

    time.sleep(1)
    obs, reward, done, info = env.step(0)

    if (reward == -100): 
        map[curr_coords[0], curr_coords[1]] = -100
        env.reset()
        time.sleep(2)
        walk_to_node(start_coords, curr_coords)
    if (reward != -100):
        map[curr_coords[0], curr_coords[1]] = reward

        curr_coords = new_coords
        explored.append(curr_coords)

        agent_row = curr_coords[0]
        agent_col = curr_coords[1]
        neighbors = [
                        (agent_row - 1, agent_col),
                        (agent_row, agent_col - 1),
                        (agent_row + 1, agent_col),
                        (agent_row, agent_col + 1)
                    ]

        for n in neighbors:
            new_cost = 1
            total_cost = cost + new_cost
            if ((n not in explored) and (n not in unexplored)):
                unexplored.append((n, total_cost))
                prev_node[n] = curr_coords
            elif (n not in explored):
                if (total_cost < ): unexplored[(n, )]
                prev_node[n] = curr_coords

    if log:
        print("reward:", reward)
        print("done:", done)
        print("info", info)

if (goal_coords in explored):
    env.reset()
    time.sleep(2)
    walk_to_node(start_coords, goal_coords)
    obs, reward, done, info = env.step(0)
    print(reward)

env.close()
print(map[27:43, 38:46])
