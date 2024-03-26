import sumo_rl
import ray
import wandb
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
from ray import tune, train
from ray.tune.registry import register_env
from ray.rllib.env import PettingZooEnv
from reward import custom_waiting_time_reward
from ray.rllib.algorithms.ppo import PPOConfig, PPO
from ray.rllib.algorithms.algorithm_config import AlgorithmConfig
from custom_obs import PrioratizingObs
import random
from ray.tune.schedulers import PopulationBasedTraining

# Absolute paths are added for Ray evaluation

net_file = 'D:/Workspace/Personal/fyp/marl_sumo_simulation/network/colombo-suburbs.net.xml'
route_file = 'D:/Workspace/Personal/fyp/marl_sumo_simulation/network/colombo-suburbs.rou.xml'
sumo_cfg_file = 'D:/Workspace/Personal/fyp/marl_sumo_simulation/network/colombo-suburbs.net.xml'
ray_results_path = 'D:/Workspace/Personal/fyp/marl_sumo_simulation/ray_results'
use_gui = False
num_seconds = 2000
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

    return (None, obs_space, action_space, {})

def policy_mapping(agent_id, episode, worker, **kwards):
    return agent_id

def explore(config):
        # ensure we collect enough timesteps to do sgd
        if config["train_batch_size"] < config["sgd_minibatch_size"] * 2:
            config["train_batch_size"] = config["sgd_minibatch_size"] * 2
        # ensure we run at least one sgd iter
        if config["num_sgd_iter"] < 1:
            config["num_sgd_iter"] = 1
        return config

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

hyper_param_mutations = {
    "lambda": lambda: random.uniform(0.9, 1.0),
    "clip_param": lambda: random.uniform(0.01, 0.5),
    "lr": [3e-3, 3e-4, 3e-4, 3e-5, 3e-5],
    "num_sgd_iter": lambda: random.randint(1, 30),
    "sgd_minibatch_size": lambda: random.randint(128, 16384),
    "train_batch_size": lambda: random.randint(2000, 160000),
}

pbt = PopulationBasedTraining(
        time_attr="time_total_s",
        perturbation_interval=120,
        resample_probability=0.25,
        hyperparam_mutations=hyper_param_mutations,
        custom_explore_fn=explore,
    )

stopping_criteria = {"training_iteration": 100, "episode_reward_mean": 10}

config = (
        PPOConfig()
        .environment(env="SumoEnv")
        .rollouts(num_rollout_workers=4, rollout_fragment_length=128)
        .evaluation(
            evaluation_interval=10,
            evaluation_duration_unit='episode',
            evaluation_duration=2,
            evaluation_parallel_to_training=True,
            evaluation_num_workers=2
        )
        .training(
            train_batch_size=512,
            gamma=0.95,
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

tuner = tune.Tuner(
        "PPO",
        tune_config=tune.TuneConfig(
            metric="episode_reward_mean",
            mode="max",
            scheduler=pbt,
        ),
        param_space=config.to_dict(),
        run_config=train.RunConfig(stop=stopping_criteria, local_dir=ray_results_path),
    )
results = tuner.fit()


# # wandb.finish()
    
