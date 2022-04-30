from tracemalloc import start
import marlo
import time
import sys
import numpy as np
np.set_printoptions(threshold=sys.maxsize)

# Debug
log = True

# Agent start, goal, and current coordinates
start_coords = (40, 40)
goal_coords = (29, 40)
curr_coords = start_coords
# Stores all nodes that have and have not been explored, respectively
explored = []
frontier = [start_coords]
# Stores cost for the agent to move from the start node to the given node
node_costs = { start_coords: 0 }
# Stores the immediate ancestor node of the node listed as the key
prev_node = { start_coords: None }

# Initialize map of environment with 80 x 80 array
# Agent starts in the middle (40, 40)
map = np.array([[-1] * 80] * 80)

# Initialize Environment
client_pool = [('127.0.0.1', 10000)]
join_tokens = marlo.make('C:\\Users\\Ryan.Kinnucan\\MinecraftRLAgent\\MarLO\\Missions\\lava_maze.xml',
                        params={
                            "client_pool": client_pool,
                            "max_retries": 100,
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
def walk_to_node(start, dest, reverse=True):
    if (start == dest): return

    path = reconstruct_path(start, dest, reverse)
    if log:
        print("--------------------")
        print("Path:", path)
        print("--------------------")

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

# Reconstruct the agent's path from the start location to the destination. 
# Start from the destination and work backwards, then reverse if necessary
def reconstruct_path(start, dest, reverse):
    if (reverse): curr_node = dest
    else: curr_node = start
    path = [curr_node]
    prev = prev_node[curr_node]

    if log:
        print("--------------------")
        print("Reconstructing Path")
        print("Start Node:", start)
        print("Destination Node:", dest)

    if (reverse):
        while (prev != start and prev != None):
            # if log:
            #     print("--------------------")
            #     print("Curr Node:", curr_node)
            #     print("Prev:", prev)
            path.append(prev)
            curr_node = prev
            prev = prev_node[curr_node]
    else:
        while (prev != dest):
            # if log:
                # print("--------------------")
                # print("Curr Node:", curr_node)
                # print("Prev:", prev)
            path.append(prev)
            curr_node = prev
            prev = prev_node[curr_node]

    if (reverse):
        path.append(start)
        path.reverse()
    else:
        path.append(dest)

    return path

# While frontier is not empty
while bool(frontier):
    # If agent falls into lava, the environment must
    # be reset so that the agent will respawn

    new_coords = frontier.pop(0)
    cost = node_costs[new_coords]

    if log:
        print("--------------------")
        print("New Coordinates:", new_coords)
        print("Cost:", cost)

    walk_to_node(curr_coords, new_coords)

    time.sleep(1)
    obs, reward, done, info = env.step(0)

    if (reward == -100): 
        map[new_coords[0], new_coords[1]] = -100
        env.reset()
        time.sleep(1)
        walk_to_node(start_coords, curr_coords)
    if (reward != -100):
        curr_coords = new_coords
        map[curr_coords[0], curr_coords[1]] = reward
        explored.append(curr_coords)

        agent_row = curr_coords[0]
        agent_col = curr_coords[1]
        neighbors = [
                        (agent_row - 1, agent_col),
                        (agent_row, agent_col - 1),
                        (agent_row + 1, agent_col),
                        (agent_row, agent_col + 1)
                    ]

        if log:
            print("Neighbors:", neighbors)

        # If the goal node is found, the agent doesn't need
        # to explore any of the blocks around it unless there
        # is a path which leads to said blocks that doesn't
        # go through the goal node
        if (reward != 100):
            for n in neighbors:
                new_cost = 1
                total_cost = cost + new_cost
                if ((n not in explored) and (n not in frontier)):
                    frontier.append(n)
                    node_costs[n] = total_cost
                    prev_node[n] = curr_coords
                elif (n not in explored):
                    if (total_cost < node_costs[n]): 
                        node_costs[n] = total_cost
                        prev_node[n] = curr_coords

        walk_to_node(curr_coords, start_coords, False)
        curr_coords = start_coords

    if log:
        print("reward:", reward)
        print("done:", done)
        print("info", info)
        print("map:")
        print(map[27:43, 38:46])

if (goal_coords in explored):
    env.reset()
    walk_to_node(start_coords, goal_coords)
    obs, reward, done, info = env.step(0)
    print("Final Reward:", reward)
    print("Final Cost:", node_costs[goal_coords])

env.close()
print(map[27:43, 38:46])
