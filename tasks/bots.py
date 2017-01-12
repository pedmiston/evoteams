import sys
import invoke
from unipath import Path
import bots


@invoke.task
def run(ctx, experiment, output_dir=None):
    """Simulate robotic players playing the totems game."""
    if experiment == '?':
        print('Available experiments:')
        for experiment in bots.paths.EXPERIMENTS.listdir('*.yaml'):
            print(' - ' + experiment.stem)
        return
    elif experiment == '*':
        experiments = bots.paths.EXPERIMENTS.listdir('*.yaml')
    elif Path(experiment).exists():
        experiments = [Path(experiment)]
    else:
        experiment = Path(bots.paths.EXPERIMENTS, experiment + '.yaml')
        assert experiment.exists(), 'experiment %s not found' % experiment
        experiments = [experiment]

    for experiment_yaml in experiments:
        output = Path(output_dir or '.', experiment.stem + '.csv')
        print('Running experiment { %s }' % experiment.stem)
        bots.run_experiment(experiment_yaml, output=output)


@invoke.task
def show_simulations(ctx, experiment):
    if not Path(experiment).exists():
        experiment = Path(bots.paths.EXPERIMENTS, experiment + '.yaml')
        assert experiment.exists(), 'experiment %s not found' % experiment
    experiment = bots.read_experiment_yaml(experiment)
    simulations = experiment.expand_all()
    simulations.to_csv(sys.stdout, index=False)
