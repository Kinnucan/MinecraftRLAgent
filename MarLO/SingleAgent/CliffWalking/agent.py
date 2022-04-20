import marlo
import time

# 'C:\\Users\\Ryan.Kinnucan\\MinecraftRLAgent\\MarLO\\Missions\\lava_maze.xml'

# 80 x 80 maze
# Agent starts in the middle (40, 40)
rows, cols = (80, 80)
map = [["Unexplored"] * cols] * rows
frontier = []
explored = []

map[40][40] = "Floor"
frontier.append(())

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

while not bool(frontier):
    pass
    # env.send_command("move -1")

    # obs, reward, done, info = env.step(0)
    # print("reward:", reward)
    # print("done:", done)
    # print("info", info)

env.close()
