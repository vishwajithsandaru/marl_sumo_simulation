import sumo_rl
import ray
# import os
import wandb
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
from ray import tune
from ray.tune.registry import register_env
from ray.rllib.algorithms.ppo import PPO

# net_file = './network/colombo-suburbs.net.xml'
# route_file = './network/colombo-suburbs.rou.xml'
# sumo_cfg_file = './network/colombo-suburbs.net.xml'
# ray_results_path = '/home/sandaruvi/Workspace/Playground/marl_sumo_simulation/ray_results'
# checkpoint_path = '/home/sandaruvi/Workspace/Playground/marl_sumo_simulation/ray_results/PPO_2024-03-20_13-20-38/PPO_SumoEnv_8a9d6_00000_0_2024-03-20_13-20-38/checkpoint_000000'
# use_gui = False
# num_seconds = 5005
# out_csv_name='./output/marl/info2'

net_file = './network/colombo-suburbs.net.xml'
route_file = './network/colombo-suburbs.rou.xml'
sumo_cfg_file = './network/colombo-suburbs.net.xml'
ray_results_path = 'D:/Workspace/Personal/fyp/marl_sumo_simulation/ray_results'
checkpoint_path = 'D:/Workspace/Personal/fyp/marl_sumo_simulation/ray_results/PPO_2024-03-20_23-46-56/PPO_SumoEnv_09114_00000_0_2024-03-20_23-46-56/checkpoint_000002'
use_gui = False
num_seconds = 5005
out_csv_name='./output/marl/info'

ray.shutdown()
ray.init()

def custom_policy_fn(env_pz: ParallelPettingZooEnv,  agent_id):
    obs_space = env_pz.observation_space[agent_id]
    action_space = env_pz.action_space[agent_id]

    obs_space_sample = env_pz.observation_space_sample([agent_id])
    action_space_sample = env_pz.action_space_sample([agent_id])

    # info = {
    #     'id': agent_id,
    #     'obs_space': obs_space,
    #     'sample_obs': obs_space_sample,
    #     'action_space': action_space,
    #     'action_space_sample': action_space_sample
    # }

    # print(info)

    return (None, obs_space, action_space, {})

def policy_mapping(agent_id, episode, worker, **kwards):
    return agent_id


env_pz = ParallelPettingZooEnv(sumo_rl.parallel_env(
            net_file=net_file,
            route_file=route_file,
            use_gui=use_gui,
            num_seconds=num_seconds,
            add_per_agent_info=False,
            add_system_info=True,
            out_csv_name=out_csv_name,
            additional_sumo_cmd='--lateral-resolution 0.3 --collision.action remove'))

agents = [a for a in env_pz.get_agent_ids()]

config = {
    "env": "SumoEnv",
    "multiagent": {
        "policies": {
            agent_id: custom_policy_fn(env_pz, agent_id)
            for agent_id in agents
        },
        "policy_mapping_fn": policy_mapping,
    },
    "framework": "torch",
    "num_cpus_per_worker": 1,
    "resources_per_trial": 2,
    "num_workers": 1,
    "horizon": 1500,
    "soft_horizon": False,
    "evaluation_interval": 1
}

def env_creator(config):
    return env_pz

register_env("SumoEnv", lambda config: env_creator(config))

policy = PPO(config=config)
policy.restore(checkpoint_path)

trained_agents = {}

for agent in agents:
    trained_agents[agent] = policy.get_policy(agent)

def gen_env_action_dict(agent_actions):
    action_dict = {}
    for agent in agents:
        action_dict[agent] = agent_actions[agent][0]
    return action_dict


obs = env_pz.reset()[0]

for i in range(1000):
    actions = {}
    for agent in agents:
        _obs = obs[agent]
        actions[agent] = trained_agents[agent].compute_single_action(_obs)
    action_dict = gen_env_action_dict(actions)
    obs, rews, terminateds, truncateds, infos = env_pz.step(action_dict)
    print(f'Time Steps: {i}', end='\r')

env_pz.reset();

print('Evaluation terminated successfully!\n')
    