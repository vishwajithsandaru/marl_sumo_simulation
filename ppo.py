import sumo_rl
import ray
import wandb
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
from ray import tune, air
from ray.tune.registry import register_env
from ray.rllib.env import PettingZooEnv
from reward import custom_waiting_time_reward
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.algorithms.algorithm_config import AlgorithmConfig
from custom_obs import PrioratizingObs

# Absolute paths are added for Ray evaluation

net_file = 'D:/Workspace/Personal/fyp/marl_sumo_simulation/network/colombo-suburbs.net.xml'
route_file = 'D:/Workspace/Personal/fyp/marl_sumo_simulation/network/colombo-suburbs.rou.xml'
sumo_cfg_file = 'D:/Workspace/Personal/fyp/marl_sumo_simulation/network/colombo-suburbs.net.xml'
ray_results_path = 'D:/Workspace/Personal/fyp/marl_sumo_simulation/ray_results'
use_gui = False
num_seconds = 5000
out_csv_name='D:/Workspace/Personal/fyp/marl_sumo_simulation/output/marl/ppo-2000s-3/colombo'

# net_file = './network/colombo-suburbs.net.xml'
# route_file = './network/colombo-suburbs.rou.xml'
# sumo_cfg_file = './network/colombo-suburbs.net.xml'
# ray_results_path = 'D:/Workspace/Personal/fyp/marl_sumo_simulation/ray_results'
# use_gui = False
# num_seconds = 2000
# out_csv_name='./output/marl/ppo-2000s-2/colombo'

# net_file = './sumo-net/4x4.net.xml'
# route_file = './sumo-net/4x4c1c2c1c2.rou.xml'
# sumo_cfg_file = './sumo-net/4x4.sumocfg'
# ray_results_path = 'D:/Workspace/Personal/fyp/marl_sumo_simulation/ray_results'
# use_gui = True
# num_seconds = 80000
# out_csv_name='outputs/4x4grid/ppo'

wandb.login()
wandb.tensorboard.patch(root_logdir="./ray_results")

wandb.init(
    project="sumo_petting_zoo_rllib",
)

ray.shutdown()
ray.init()

def custom_policy_fn(env_pz: ParallelPettingZooEnv,  agent_id):
    obs_space = env_pz.observation_space[agent_id]
    action_space = env_pz.action_space[agent_id]

    return (None, obs_space, action_space, {})

def policy_mapping(agent_id, episode, worker, **kwards):
    return agent_id

env_pz = ParallelPettingZooEnv(sumo_rl.parallel_env(
            net_file=net_file,
            route_file=route_file,
            use_gui=use_gui,
            num_seconds=num_seconds,
            time_to_teleport=500,
            min_green=20,
            out_csv_name=out_csv_name,
            max_green=200,
            reward_fn=custom_waiting_time_reward,
            observation_class=PrioratizingObs,
            additional_sumo_cmd='--lateral-resolution 0.3 --collision.action remove'))

def env_creator(config):
    return env_pz

register_env("SumoEnv", lambda config: env_creator(config))

env_pz.close()

agents = [a for a in env_pz.get_agent_ids()]

config = (
        PPOConfig()
        .environment(env="SumoEnv")
        .rollouts(num_rollout_workers=4, rollout_fragment_length=128)
        .evaluation(
            evaluation_interval=10,
            evaluation_duration_unit='episodes',
            evaluation_duration=2,
            evaluation_parallel_to_training=True,
            evaluation_num_workers=2
        )
        .training(
            train_batch_size=512,
            lr=2e-5,
            gamma=0.95,
            lambda_=0.9,
            use_gae=True,
            clip_param=0.4,
            grad_clip=None,
            entropy_coeff=0.1,
            vf_loss_coeff=0.25,
            sgd_minibatch_size=64,
            num_sgd_iter=10,
        )
        .debugging(log_level="ERROR")
        .framework(framework="torch")
        .multi_agent(
            policies= {
                agent_id: custom_policy_fn(env_pz, agent_id)
                for agent_id in agents
            },
            policy_mapping_fn=policy_mapping
        )
)

results = tune.run(
    "PPO",
    config=config.to_dict(),
    stop={"timesteps_total": 300000},
    checkpoint_freq=20,
    local_dir=ray_results_path,
)


wandb.finish()
    
