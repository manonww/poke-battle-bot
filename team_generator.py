from poke_env.teambuilder import Teambuilder
import numpy as np
from typing import Union, Any
import numpy as np
import asyncio
from loguru import logger
from game_setup import MyPokedex
class Team:
    ''' Parent class that contains the pokemon rooster and the driver which is agent '''

    def __init__(self, rooster:Union[None, str] = None, driver:Union[None, Any] =None, battle_format:str = "gen1ou") -> None:
        self.rooster = rooster
        self.driver = driver
        self.battle_format = battle_format

    def create_random_team(self, pokedex:MyPokedex):
        for _ in range(6):
            options = list(pokedex.pokedex.keys())
            choice = np.random.choice(options)
            
            pokemon = pokedex.pokedex[choice]
            options.remove(choice)
            #choose random ability, evs, and moveset,
            pokemon.randomize_all(item_list = ["leftovers", "lifeorb"], nature_list = ["adamant", "jolly"])
            logger.info(pokemon)

    def yield_team(self):
        logger.info(self.rooster)
        return self.rooster
    

class RandomTeamFromPool(Teambuilder):
    def __init__(self, teams):
        self.teams = [self.join_team(self.parse_showdown_team(team)) for team in teams]

    def yield_team(self):
        choice= np.random.choice(self.teams)
        logger.info(choice)
        return choice

#custom_builder = RandomTeamFromPool([team_1, team_2])

from poke_env.player import RandomPlayer

player_1 = RandomPlayer(
    battle_format="gen1ou",
#    team=custom_builder,
    max_concurrent_battles=10,
    save_replays = True
)


async def main():
    #await player_1.battle_against(player_2, n_battles=1)
    #team = Team()
    this_gen_pokedex = MyPokedex()
    team = Team()
    team.create_random_team(this_gen_pokedex)
    #logger.info(this_gen_pokedex.pokedex["rhydon"])
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
