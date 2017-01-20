import bots


def test_team_initial_inventory():
    team = bots.models.create_team()
    assert len(team.inventory) == 6

def test_experiment_default_args():
    exp = bots.main.Experiment()
    assert exp.player_memory == [False]
    assert exp.team_memory == [False]
