import marlo
import time
import sys
import numpy as np
np.set_printoptions(threshold=sys.maxsize)

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

obs, reward, done, info = env.step(0)
map[start_coords[0], start_coords[1]] = reward
explored.append(start_coords)

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

# Given a list of neighboring nodes and the
# agent's current location, explore all neighbors
def explore_neighbors(neighbors, curr_coords):
    for n in neighbors:
        if (n not in explored):
            prev_node[n] = curr_coords

            if log:
                print("--------------------")
                print("Current Neighbor:", n)
                print("Neighbor's Prev:", prev_node[n])

            walk_to_node(curr_coords, n)

            # Get observation
            time.sleep(1)
            obs, reward, done, info = env.step(0)

            if log:
                print("--------------------")
                print("reward:", reward)
                print("done:", done)
                print("info", info)

            # If agent falls into lava, the environment must
            # be reset so that the agent will respawn, after
            # which the agent needs to be returned to the
            # last location it was exploring from
            if (reward == -100): 
                map[n[0], n[1]] = -100

                if log:
                    print("map:")
                    print(map[27:43, 38:46])
                    print("--------------------")
                    print("Reseting Env")
                    print("--------------------")

                env.reset()

                explored.append(n)

                # Remove lava nodes from frontier because 
                # their neighbors will be inaccessible
                frontier.remove(n)

                # Walk the agent back to its previous location
                # if there are still neighbors to explore
                if (bool(neighbors)): walk_to_node(start_coords, curr_coords)

            # If agent does not fall into lava, set the node
            # at that location equal to the reward, then walk
            # the agent back to curr_coords
            if (reward != -100):
                map[n[0], n[1]] = reward

                # If the goal node is found, the agent doesn't need
                # to explore any of the blocks around it unless there
                # is a path which leads to said blocks that doesn't
                # go through the goal node
                if (reward == 100): frontier.remove(n)

                if log:
                    print("map:")
                    print(map[27:43, 38:46])
                    
                explored.append(n)
                walk_to_node(n, curr_coords, False)

# While frontier is not empty
while bool(frontier):
    # Walk agent to the first node in the frontier
    dest = frontier.pop(0)
    if log:
        print("--------------------")
        print("Node to Explore:", dest)
        print("Current Node:", curr_coords)
    walk_to_node(curr_coords, dest)
    curr_coords = dest

    # Get agent's current row and column
    # and all of its neighbors
    agent_row = curr_coords[0]
    agent_col = curr_coords[1]
    neighbors = [
                    (agent_row - 1, agent_col),
                    (agent_row, agent_col - 1),
                    (agent_row + 1, agent_col),
                    (agent_row, agent_col + 1)
                ]

    # If a neighboring node has not already been explored, and
    # is not already in the frontier, then add it to the frontier
    for n in neighbors:
        if ((n not in explored) and (n not in frontier)): frontier.append(n)
    if log:
        print("Frontier:", frontier)
        print("Neighbors:", neighbors)

    # Explore all neighbors of the current node, then
    # walk the agent back to its starting location
    explore_neighbors(neighbors, curr_coords)
    walk_to_node(curr_coords, start_coords, False)

    # Once a node has been fully explored, remove it from the frontier
    if (curr_coords in frontier): frontier.remove(curr_coords)
    curr_coords = start_coords

env.close()
print(map[27:43, 38:46])
