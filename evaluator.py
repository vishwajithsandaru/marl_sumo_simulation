import sumo_rl
import ray
# import os
import wandb
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
from ray import tune
from ray.tune.registry import register_env
from ray.rllib.algorithms.ppo import PPO
from ray.rllib.algorithms.ppo import PPOConfig
from reward import custom_waiting_time_reward
from custom_obs import PrioratizingObs

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
checkpoint_path = 'D:/Workspace/Personal/fyp/marl_sumo_simulation/ray_results/ppo-5000s-2/PPO_SumoEnv_f7ffa_00000_0_2024-03-27_20-53-31/checkpoint_000013'
use_gui = False
num_seconds = 3000
out_csv_name='./output/custom-eval/ppo-3000s-2'

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
        .rollouts(num_rollout_workers=1, rollout_fragment_length=512)
        .evaluation(
            evaluation_interval=4,
            evaluation_duration_unit='episodes',
            evaluation_duration=1,
            evaluation_parallel_to_training=False
        )
        .training(
            train_batch_size=2048,
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

for i in range(600):
    actions = {}
    for agent in agents:
        _obs = obs[agent]
        actions[agent] = trained_agents[agent].compute_single_action(_obs)
    action_dict = gen_env_action_dict(actions)
    obs, rews, terminateds, truncateds, infos = env_pz.step(action_dict)
    print(f'Time Steps: {i}', end='\r')

env_pz.reset();

print('Evaluation terminated successfully!\n')
    