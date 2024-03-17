import sumo_rl
import ray
import wandb
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
from ray import tune
from ray.tune.registry import register_env
from ray.rllib.env import PettingZooEnv
from torchrl.envs.libs.pettingzoo import PettingZooWrapper

net_file = './network/colombo-suburbs.net.xml'
route_file = './network/colombo-suburbs.net.xml'
sumo_cfg_file = './network/colombo-suburbs.net.xml'
use_gui = False
num_seconds = 2000

# wandb.login()
# wandb.tensorboard.patch(root_logdir="./ray_results")

# wandb.init(
#     project="sumo_petting_zoo_rllib",
# )

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
            num_seconds=num_seconds))

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
    "soft_horizon": False
}
    
