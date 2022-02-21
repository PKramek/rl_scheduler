import argparse


class ArgumentParserWithoutSystemExit(argparse.ArgumentParser):
    # This is a wrapper class, that allows to catch error messages from argparse and prevents app closure

    def __init__(self, *args, **kwargs):
        super(ArgumentParserWithoutSystemExit, self).__init__(*args, **kwargs)

        self.error_message = ''

    def error(self, message):
        self.error_message = message

    def parse_args(self, *args, **kwargs):
        self.error_message = ''
        # catch SystemExit exception to prevent closing the application
        result = None
        try:
            result = super().parse_args(*args, **kwargs)
        except SystemExit:
            pass
        return result


class AcerAceracParser(ArgumentParserWithoutSystemExit):
    def __init__(self, *args, **kwargs):
        super(AcerAceracParser, self).__init__(*args, **kwargs)

        acer_acer_algos = {'acer', 'acerac'}
        autocorrelated_actors = {'autocor+u'}

        self.add_argument('--algo', type=str, help='Algorithm to be used', default="acer",
                          choices=acer_acer_algos)
        self.add_argument('--env_name', type=str, help='OpenAI Gym environment name', default="CartPole-v0")
        self.add_argument('--gamma', type=float, help='discount factor', required=False, default=0.99)
        self.add_argument('--lam', type=float, help='lambda parameter', required=False, default=0.9)
        self.add_argument('--b', type=float, help='probability density truncation coefficient',
                          required=False, default=3)
        self.add_argument('--actor_adam_epsilon', type=float,
                          help='ADAM optimizer epsilon parameter (BaseActor)',
                          required=False, default=None)
        self.add_argument('--actor_adam_beta1', type=float, help='ADAM optimizer beta1 (BaseActor)',
                          required=False, default=0.9)
        self.add_argument('--actor_adam_beta2', type=float, help='ADAM optimizer beta2 (BaseActor)',
                          required=False, default=0.999)
        self.add_argument('--critic_adam_epsilon', type=float, help='ADAM optimizer epsilon (Critic)',
                          required=False, default=None)
        self.add_argument('--critic_adam_beta1', type=float, help='ADAM optimizer beta1 (Critic)',
                          required=False, default=0.9)
        self.add_argument('--critic_adam_beta2', type=float, help='ADAM optimizer beta2 (Critic)',
                          required=False, default=0.999)
        self.add_argument('--actor_lr', type=float, help='BaseActor learning rate', required=False,
                          default=0.001)
        self.add_argument('--critic_lr', type=float, help='Critic learning rate', required=False, default=0.001)
        self.add_argument('--explorer_lr', type=float, help='Explorer (eacer) learning rate', required=False,
                          default=0.001)
        self.add_argument('--actor_beta_penalty', type=float, help='BaseActor penalty coefficient',
                          default=0.001)
        self.add_argument('--n_step', type=int, help='experience replay frequency', required=False, default=1)
        self.add_argument('--c', type=int, help='experience replay intensity', required=False, default=1)
        self.add_argument('--c0', type=float, help='experience replay warm start coefficient', default=1)
        self.add_argument('--alpha', type=float, help='Alpha parameter for acerac.', default=0.5)
        self.add_argument('--tau', type=int, help='Tau parameter for acerac', default=2)
        self.add_argument('--n', type=int, help='N parameter for acerac', default=2)
        self.add_argument('--noise_type', type=str, help='Type of noise for ACERAC',
                          default='autocor+u', choices=list(autocorrelated_actors))
        self.add_argument('--std', type=float,
                          help='value on diagonal of Normal dist. covariance matrix. If not specified,'
                               '0.4 * actions_bound is set.',
                          required=False, default=None)
        self.add_argument('--learning_starts', type=int, help='experience replay warm start coefficient',
                          default=10000)
        self.add_argument('--memory_size', type=int,
                          help='memory buffer size (sum of all of the buffers from every env',
                          required=False, default=1e6)
        self.add_argument('--actor_layers', nargs='+', type=int,
                          help='List of BaseActor\'s neural network hidden layers sizes',
                          required=False, default=(100, 100))
        self.add_argument('--critic_layers', nargs='+', type=int,
                          help='List of Critic\'s neural network hidden layers sizes',
                          required=False, default=(100, 100))
        self.add_argument('--num_parallel_envs', type=int,
                          help='Number of environments to be run in a parallel',
                          default=1)
        self.add_argument('--batches_per_env', type=int,
                          help='Number of batches sampled from one environment buffer in one'
                               'backward pass',
                          default=5)
        self.add_argument('--standardize_obs', help='True, if observations should be standarized online'
                                                    ' (and clipped between -5, 5)',
                          action='store_true')
        self.add_argument('--rescale_rewards',
                          help='-1 to turn rescaling off, 0 to rescale automatically based on'
                               'running variance; value greater than 0 rescales the rewards by'
                               'dividing them by the value',
                          type=float, default=-1)
        self.add_argument('--limit_reward_tanh', help='limits reward to [-value, value] using tanh function'
                                                      '0 to disable',
                          type=float, default=None)
        self.add_argument('--td_clip', help='Temporal difference clipping threshold (ACERAC only)',
                          type=float, default=None)
        self.add_argument('--gradient_norm',
                          help='Global gradient clip norm, 0 to use learned median of the gradient',
                          type=float, default=None)
        self.add_argument('--gradient_norm_median_threshold',
                          help='Number of medians used to clip gradients by their norm',
                          type=float, default=4)
        self.add_argument('--use_v', action='store_true',
                          help='If true then value instead of noise-value will be used (ACERAC only)')
        self.add_argument('--evaluate_time_steps_interval', type=int,
                          help='Number of time steps between evaluations. '
                               '-1 to turn evaluation off',
                          default=10000)
        self.add_argument('--num_evaluation_runs', type=int,
                          help='Number of evaluation runs in a single evaluation',
                          default=10)
        self.add_argument('--max_time_steps', type=int,
                          help='Maximum number of time steps of agent learning. -1 means no '
                               'time steps limit',
                          default=-1)
        self.add_argument('--log_dir', type=str, help='Logging directory', default='logs/')
        self.add_argument('--no_checkpoint', help='Disable checkpoint saving', action='store_true')
        self.add_argument('--no_tensorboard', help='Disable tensorboard logs', action='store_true')
        self.add_argument('--experiment_name', type=str, help='Name of the current experiment', default='')
        self.add_argument('--save_video_on_kill', action='store_true',
                          help='True if SIGINT signal should trigger registration of the video')
        self.add_argument('--record_time_steps', type=int, default=None,
                          help='Number of time steps between evaluation video recordings')
        self.add_argument('--use_cpu', action='store_true',
                          help='True if CPU (instead of GPU) should be used')
        self.add_argument('--synchronous', action='store_true',
                          help='True if not use asynchronous envs')
        self.add_argument('--timesteps_increase', help='Timesteps per second increase. Affects:'
                                                       ' gamma, max time steps, memory size, lam, n, alpha, evaluate_time_steps_interval, n_step',
                          type=int, default=None)

        self.add_argument('--dump', help='Dump memory and models on given timesteps', nargs='*', type=int)


class OtherAlgorithmsParser(ArgumentParserWithoutSystemExit):
    def __init__(self, *args, **kwargs):
        super(OtherAlgorithmsParser, self).__init__(*args, **kwargs)

        algorithms = {'PPO', 'SAC'}

        self.add_argument('--algo', type=str, help='Algorithm to be used', required=True, choices=algorithms)
        self.add_argument('--env', type=str, help='OpenAI Gym environment name', default="Humanoid-v2")
        self.add_argument('--max_timesteps', type=int, help='Maximum number of timesteps', default=int(1e6))
        self.add_argument('--gamma', type=float, help='Discount factor', required=False, default=0.99)
        self.add_argument('--initial_alpha', type=float, help='This is the inverse of reward scale', required=False,
                          default=1)
        self.add_argument('--lambda', type=float, help='The GAE (lambda) parameter', required=False, default=0.95)
        self.add_argument('--lr', type=float, help='Learning rate (used in PPO)', required=False, default=0.001)
        self.add_argument('--actor_learning_rate', type=float, help='BaseActor learning rate', required=False,
                          default=0.0003)
        self.add_argument('--critic_learning_rate', type=float, help='Critic learning rate', required=False,
                          default=0.0003)
        self.add_argument('--entropy_learning_rate', type=float, help='Critic learning rate', required=False,
                          default=0.0003)
        self.add_argument('--learning_starts', type=int, help='Experience replay warm start coefficient',
                          default=10000)
        self.add_argument('--tau', type=float, help='Target smoothing coefficient', required=False, default=0.005)
        self.add_argument('--buffer_size', type=int, help='Memory buffer size', required=False, default=int(1e6))
        self.add_argument('--fcnet_hiddens', nargs='+', type=int, help='List of neural network hidden layers sizes',
                          required=False, default=[256, 256])
        self.add_argument('--policy_layers', nargs='+', type=int,
                          help='List of Policy\'s neural network hidden layers sizes',
                          required=False, default=[256, 256])
        self.add_argument('--q_value_layers', nargs='+', type=int,
                          help='List of Q-Value neural network hidden layers sizes',
                          required=False, default=[256, 256])
        self.add_argument('--num_sgd_iter', type=int, help='Number of SGD iterations in PPO learning', default=10)
        self.add_argument('--train_batch_size', type=int,
                          help='Minibatch size, corresponds to horizon size in PPO algorithm',
                          default=64)
        self.add_argument('--sgd_minibatch_size', type=int, help='Minibatch size in PPO',
                          default=64)

        # TODO add Target update interval
        # parser.add_argument('--n_step', type=int, help='Target update interval', default=64)
        self.add_argument('--evaluation_interval',
                          help='Number of training iterations between evaluations. None disables'
                               'evaluation', type=int, default=5)
        self.add_argument('--evaluation_num_episodes', help='Number of evaluation runs', type=int, default=10)
        self.add_argument('--fcnet_activation', type=str, help='Activation function used in hidden layers',
                          default="tanh", choices={'tanh', 'relu'})
        self.add_argument('--kl_target', type=float, help='Target KL in PPO',
                          default=0.01)
        self.add_argument('--vf_clip_param', type=float, help='Value function clipping parameter',
                          default=10.0)
        self.add_argument('--clip_param', type=float, help='Clip parameter used in PPO',
                          default=0.2)


#
# def get_acer_acerac_parser() -> ArgumentParserWithoutSystemExit:
#     # Arguments are the same as in this repository: https://github.com/lychanl/acerac
#
#     acer_acer_algos = {'acer', 'acerac'}
#     autocorrelated_actors = {'autocor+u'}
#
#     parser = ArgumentParserWithoutSystemExit(
#         description='Parser for checking parameters for ACER and ACERAC algorithms')
#     parser.add_argument('--algo', type=str, help='Algorithm to be used', default="acer",
#                         choices=acer_acer_algos)
#     parser.add_argument('--env_name', type=str, help='OpenAI Gym environment name', default="CartPole-v0")
#     parser.add_argument('--gamma', type=float, help='discount factor', required=False, default=0.99)
#     parser.add_argument('--lam', type=float, help='lambda parameter', required=False, default=0.9)
#     parser.add_argument('--b', type=float, help='probability density truncation coefficient',
#                         required=False, default=3)
#     parser.add_argument('--actor_adam_epsilon', type=float,
#                         help='ADAM optimizer epsilon parameter (BaseActor)',
#                         required=False, default=None)
#     parser.add_argument('--actor_adam_beta1', type=float, help='ADAM optimizer beta1 (BaseActor)',
#                         required=False, default=0.9)
#     parser.add_argument('--actor_adam_beta2', type=float, help='ADAM optimizer beta2 (BaseActor)',
#                         required=False, default=0.999)
#     parser.add_argument('--critic_adam_epsilon', type=float, help='ADAM optimizer epsilon (Critic)',
#                         required=False, default=None)
#     parser.add_argument('--critic_adam_beta1', type=float, help='ADAM optimizer beta1 (Critic)',
#                         required=False, default=0.9)
#     parser.add_argument('--critic_adam_beta2', type=float, help='ADAM optimizer beta2 (Critic)',
#                         required=False, default=0.999)
#     parser.add_argument('--actor_lr', type=float, help='BaseActor learning rate', required=False,
#                         default=0.001)
#     parser.add_argument('--critic_lr', type=float, help='Critic learning rate', required=False, default=0.001)
#     parser.add_argument('--explorer_lr', type=float, help='Explorer (eacer) learning rate', required=False,
#                         default=0.001)
#     parser.add_argument('--actor_beta_penalty', type=float, help='BaseActor penalty coefficient',
#                         default=0.001)
#     parser.add_argument('--n_step', type=int, help='experience replay frequency', required=False, default=1)
#     parser.add_argument('--c', type=int, help='experience replay intensity', required=False, default=1)
#     parser.add_argument('--c0', type=float, help='experience replay warm start coefficient', default=1)
#     parser.add_argument('--alpha', type=float, help='Alpha parameter for acerac.', default=0.5)
#     parser.add_argument('--tau', type=int, help='Tau parameter for acerac', default=2)
#     parser.add_argument('--n', type=int, help='N parameter for acerac', default=2)
#     parser.add_argument('--noise_type', type=str, help='Type of noise for ACERAC',
#                         default='autocor+u', choices=list(autocorrelated_actors))
#     parser.add_argument('--std', type=float,
#                         help='value on diagonal of Normal dist. covariance matrix. If not specified,'
#                              '0.4 * actions_bound is set.',
#                         required=False, default=None)
#     parser.add_argument('--learning_starts', type=int, help='experience replay warm start coefficient',
#                         default=10000)
#     parser.add_argument('--memory_size', type=int,
#                         help='memory buffer size (sum of all of the buffers from every env',
#                         required=False, default=1e6)
#     parser.add_argument('--actor_layers', nargs='+', type=int,
#                         help='List of BaseActor\'s neural network hidden layers sizes',
#                         required=False, default=(100, 100))
#     parser.add_argument('--critic_layers', nargs='+', type=int,
#                         help='List of Critic\'s neural network hidden layers sizes',
#                         required=False, default=(100, 100))
#     parser.add_argument('--num_parallel_envs', type=int,
#                         help='Number of environments to be run in a parallel',
#                         default=1)
#     parser.add_argument('--batches_per_env', type=int,
#                         help='Number of batches sampled from one environment buffer in one'
#                              'backward pass',
#                         default=5)
#     parser.add_argument('--standardize_obs', help='True, if observations should be standarized online'
#                                                   ' (and clipped between -5, 5)',
#                         action='store_true')
#     parser.add_argument('--rescale_rewards',
#                         help='-1 to turn rescaling off, 0 to rescale automatically based on'
#                              'running variance; value greater than 0 rescales the rewards by'
#                              'dividing them by the value',
#                         type=float, default=-1)
#     parser.add_argument('--limit_reward_tanh', help='limits reward to [-value, value] using tanh function'
#                                                     '0 to disable',
#                         type=float, default=None)
#     parser.add_argument('--td_clip', help='Temporal difference clipping threshold (ACERAC only)',
#                         type=float, default=None)
#     parser.add_argument('--gradient_norm',
#                         help='Global gradient clip norm, 0 to use learned median of the gradient',
#                         type=float, default=None)
#     parser.add_argument('--gradient_norm_median_threshold',
#                         help='Number of medians used to clip gradients by their norm',
#                         type=float, default=4)
#     parser.add_argument('--use_v', action='store_true',
#                         help='If true then value instead of noise-value will be used (ACERAC only)')
#     parser.add_argument('--evaluate_time_steps_interval', type=int,
#                         help='Number of time steps between evaluations. '
#                              '-1 to turn evaluation off',
#                         default=10000)
#     parser.add_argument('--num_evaluation_runs', type=int,
#                         help='Number of evaluation runs in a single evaluation',
#                         default=10)
#     parser.add_argument('--max_time_steps', type=int,
#                         help='Maximum number of time steps of agent learning. -1 means no '
#                              'time steps limit',
#                         default=-1)
#     parser.add_argument('--log_dir', type=str, help='Logging directory', default='logs/')
#     parser.add_argument('--no_checkpoint', help='Disable checkpoint saving', action='store_true')
#     parser.add_argument('--no_tensorboard', help='Disable tensorboard logs', action='store_true')
#     parser.add_argument('--experiment_name', type=str, help='Name of the current experiment', default='')
#     parser.add_argument('--save_video_on_kill', action='store_true',
#                         help='True if SIGINT signal should trigger registration of the video')
#     parser.add_argument('--record_time_steps', type=int, default=None,
#                         help='Number of time steps between evaluation video recordings')
#     parser.add_argument('--use_cpu', action='store_true',
#                         help='True if CPU (instead of GPU) should be used')
#     parser.add_argument('--synchronous', action='store_true',
#                         help='True if not use asynchronous envs')
#     parser.add_argument('--timesteps_increase', help='Timesteps per second increase. Affects:'
#                                                      ' gamma, max time steps, memory size, lam, n, alpha, evaluate_time_steps_interval, n_step',
#                         type=int, default=None)
#
#     parser.add_argument('--dump', help='Dump memory and models on given timesteps', nargs='*', type=int)
#
#     return parser
#
#
# def get_other_algorithms_parser() -> ArgumentParserWithoutSystemExit:
#     # Arguments are the same as in this repository: https://github.com/PKramek/rllib_runner
#     algorithms = {'PPO', 'SAC'}
#
#     parser = ArgumentParserWithoutSystemExit(
#         description='Parser for checking parameters for algorithms other than ACER and ACERAC')
#     parser.add_argument('--algo', type=str, help='Algorithm to be used', required=True, choices=algorithms)
#     parser.add_argument('--env', type=str, help='OpenAI Gym environment name', default="Humanoid-v2")
#     parser.add_argument('--max_timesteps', type=int, help='Maximum number of timesteps', default=int(1e6))
#     parser.add_argument('--gamma', type=float, help='Discount factor', required=False, default=0.99)
#     parser.add_argument('--initial_alpha', type=float, help='This is the inverse of reward scale', required=False,
#                         default=1)
#     parser.add_argument('--lambda', type=float, help='The GAE (lambda) parameter', required=False, default=0.95)
#     parser.add_argument('--lr', type=float, help='Learning rate (used in PPO)', required=False, default=0.001)
#     parser.add_argument('--actor_learning_rate', type=float, help='BaseActor learning rate', required=False,
#                         default=0.0003)
#     parser.add_argument('--critic_learning_rate', type=float, help='Critic learning rate', required=False,
#                         default=0.0003)
#     parser.add_argument('--entropy_learning_rate', type=float, help='Critic learning rate', required=False,
#                         default=0.0003)
#     parser.add_argument('--learning_starts', type=int, help='Experience replay warm start coefficient', default=10000)
#     parser.add_argument('--tau', type=float, help='Target smoothing coefficient', required=False, default=0.005)
#     parser.add_argument('--buffer_size', type=int, help='Memory buffer size', required=False, default=int(1e6))
#     parser.add_argument('--fcnet_hiddens', nargs='+', type=int, help='List of neural network hidden layers sizes',
#                         required=False, default=[256, 256])
#     parser.add_argument('--policy_layers', nargs='+', type=int,
#                         help='List of Policy\'s neural network hidden layers sizes',
#                         required=False, default=[256, 256])
#     parser.add_argument('--q_value_layers', nargs='+', type=int,
#                         help='List of Q-Value neural network hidden layers sizes',
#                         required=False, default=[256, 256])
#     parser.add_argument('--num_sgd_iter', type=int, help='Number of SGD iterations in PPO learning', default=10)
#     parser.add_argument('--train_batch_size', type=int,
#                         help='Minibatch size, corresponds to horizon size in PPO algorithm',
#                         default=64)
#     parser.add_argument('--sgd_minibatch_size', type=int, help='Minibatch size in PPO',
#                         default=64)
#
#     # TODO add Target update interval
#     # parser.add_argument('--n_step', type=int, help='Target update interval', default=64)
#     parser.add_argument('--evaluation_interval', help='Number of training iterations between evaluations. None disables'
#                                                       'evaluation', type=int, default=5)
#     parser.add_argument('--evaluation_num_episodes', help='Number of evaluation runs', type=int, default=10)
#     parser.add_argument('--fcnet_activation', type=str, help='Activation function used in hidden layers',
#                         default="tanh", choices={'tanh', 'relu'})
#     parser.add_argument('--kl_target', type=float, help='Target KL in PPO',
#                         default=0.01)
#     parser.add_argument('--vf_clip_param', type=float, help='Value function clipping parameter',
#                         default=10.0)
#     parser.add_argument('--clip_param', type=float, help='Clip parameter used in PPO',
#                         default=0.2)
# #
#     return parser

class ParserFactory:
    PARSER_ALGORITHM_MAPPING = {
        'acer': AcerAceracParser,
        'acerac': AcerAceracParser,
        'PPO': OtherAlgorithmsParser,
        'SAC': OtherAlgorithmsParser
    }

    @staticmethod
    def get_parser(algorithm: str) -> ArgumentParserWithoutSystemExit:
        return ParserFactory.PARSER_ALGORITHM_MAPPING[algorithm]
