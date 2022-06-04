# General parameters related to the gameplay

from enum import Enum

# allowed type of players

class Role(str, Enum):
    goalkeeper = 'goalkeeper'
    defender = 'defender'
    midfielder = 'midfielder'
    attacker = 'attacker'

team_size = {
    'goalkeeper': 3,
    'defender': 6,
    'midfielder': 6,
    'attacker': 5
    }

budget = 5000000
initial_player_value = 1000000
markup = {'min': 110, 'max': 200}