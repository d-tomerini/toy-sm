import schemas
import models
import names
import pycountry
from random import choice, randint
import params


def generate_team(user: models.User):
    """
    Create a Team object to add to the database
    :param user: the user owning the team, database object
    :return: the team object
    """
    return schemas.Team(
        user_id=user.id,
        name=f'Team of {user.email}',
        country=random_country(),
        budget=params.budget
    )


def generate_players(team: models.Team):
    """
    Generate a standard team of players according to params
    :param team: database team object
    :return: a list of players
    """

    players = []
    for role, n in params.team_size.items():
        for i in range(0, n):
            player = schemas.MarketPlayer(
                name=names.get_first_name(gender='male'),
                surname=names.get_last_name(),
                country=random_country(),
                age=randint(18, 40),
                value=params.initial_player_value,
                role=role,
                team_id=team.id,
                on_market=False,
            )
            players.append(player)
    return players


def random_country():
    return choice(list(pycountry.countries)).name


def random_markup(price: int):
    markup = randint(params.markup['min'], params.markup['max'])
    return int(price * (1 + markup/100))
