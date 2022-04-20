import marlo
import time
import sys
import numpy as np
np.set_printoptions(threshold=sys.maxsize)

# 'C:\\Users\\Ryan.Kinnucan\\MinecraftRLAgent\\MarLO\\Missions\\lava_maze.xml'

# Debug
log = True

start_coords = (40, 40)
curr_coords = start_coords
frontier = [(40, 40)]
explored = []

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

# Given a set of coordinates, send the agent to that location
def go_to_coords():
    pass

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

# While frontier is not empty
while bool(frontier):
    env.send_command("move 1")
    time.sleep(1)
    obs, reward, done, info = env.step(0)

    if log:
        print("reward:", reward)
        print("done:", done)
        print("info", info)
    # if (reward == -100): map[curr_coords[0], curr_coords[1]] = -100
    # if (reward == 100): map[curr_coords[0], curr_coords[1]] = 100
    # if (reward == 0): map[curr_coords[0], curr_coords[1]] = 0

env.close()
print(map[27:43, 38:46])
