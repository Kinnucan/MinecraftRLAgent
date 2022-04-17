import marlo
import time

client_pool = [('127.0.0.1', 10000)]
join_tokens = marlo.make('MarLo-CliffWalking-v0',
                        params={
                            "client_pool": client_pool,
                            "allowContinuousMovement": True,
                            "allowDiscreteMovement": True,
                            "allowAbsoluteMovement": True,
                        })

assert len(join_tokens) == 1
join_token = join_tokens[0]

env = marlo.init(join_token)
env.reset()

done = False
while not done:
    # _action = env.action_space.sample()
    # print(_action)

    # env.send_command("move 1")
    env.send_command("turn 1")
    # time.sleep(1)
    # done = True

    # obs, reward, done, info = env.step(0)
    # print("reward:", reward)
    # print("done:", done)
    # print("info", info)

env.close()
