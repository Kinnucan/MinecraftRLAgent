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
# Stores all nodes that have and have not been explored, respectively
explored = []
unexplored = [start_coords]
# Stores cost for the agent to move from the start node to the given node
node_costs = { start_coords: 0 }
# Stores the immediate ancestor node of the node listed as the key
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

    for i in range(0, len(path) - 1):
        curr = path[i]
        next = path[i + 1]
        if (next[0] < curr[0] and next[1] == curr[1]):
            command = "move 1"
        if (next[0] == curr[0] and next[1] < curr[1]):
            command = "moveeast 1"
        if (next[0] > curr[0] and next[1] == curr[1]):
            command = "move -1"
        if (next[0] == curr[0] and next[1] > curr[1]):
            command = "movewest 1"
        env.send_command(command)
        time.sleep(0.5)

# Given a starting node and a destination, reconstruct the path
# to get from the start to the destination based on prev_node
def reconstruct_path(start, dest):
    curr_node = dest
    path = [curr_node]
    prev = prev_node[curr_node]
    while prev != start:
        path.append(prev)
        curr_node = prev
        prev = prev_node[curr_node]
    return path.reverse()

# While frontier is not empty
while bool(unexplored):
    # If agent falls into lava, the environment must
    # be reset so that the agent will respawn

    new_coords = unexplored.pop(0)
    cost = node_costs[new_coords]

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
                unexplored.append(n)
                node_costs[n] = total_cost
                prev_node[n] = curr_coords
            elif (n not in explored):
                if (total_cost < node_costs[n]): 
                    node_costs[n] = total_cost
                prev_node[n] = curr_coords
        unexplored.sort(reverse=True)

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
