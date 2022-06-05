# General parameters related to the gameplay

from enum import Enum


# allowed type of players
class Role(str, Enum):
    goalkeeper = 'goalkeeper'
    defender = 'defender'
    midfielder = 'midfielder'
    attacker = 'attacker'


# team composition
team_size = {
    'goalkeeper': 3,
    'defender': 6,
    'midfielder': 6,
    'attacker': 5
}

# team stats
budget = 5000000
initial_player_value = 1000000

# player markup after exchange
markup = {'min': 10, 'max': 100}
