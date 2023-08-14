from poke_env.teambuilder import Teambuilder
import numpy as np
import time
from typing import Union, Any
import asyncio
from loguru import logger
from poke_env.player.internals import POKE_LOOP
import tabulate
from game_setup import MyPokedex
from driver import Driver
from poke_env.player.utils import cross_evaluate, background_cross_evaluate
class Team:
    ''' Parent class that contains the pokemon rooster and the driver which is agent '''

    def __init__(self, rooster:Union[None, str] = None, driver:Union[None, Any] =None, battle_format:str = "gen1ou") -> None:
        self.rooster = rooster
        self.driver = driver
        self.battle_format = battle_format

    def create_random_team(self, pokedex:MyPokedex):
        self.rooster = []
        for _ in range(6):
            options = list(pokedex.pokedex.keys())
            choice = np.random.choice(options)
            
            pokemon = pokedex.pokedex[choice]
            options.remove(choice)
            #choose random ability, evs, and moveset,
            self.rooster.append(pokemon.randomize_all(item_list = ["leftovers", "lifeorb"], nature_list = ["adamant", "jolly"]) )
            logger.info(pokemon)

    def yield_team(self):
        logger.info(self.rooster)
        return self.rooster
    

#custom_builder = RandomTeamFromPool([team_1, team_2])

from poke_env.player import RandomPlayer

player_1 = RandomPlayer(
    battle_format="gen1randombattle",
#    team=custom_builder,
    max_concurrent_battles=10,
    save_replays = True
)


def generate_random_teams(n:int=10,battle_format:str="gen1randombattle",):
    ''' '''
    teams = []
    for _ in range(n):
        driver = Driver(battle_format=battle_format, save_replays = True)
        driver.random_nn()
        team = Team(driver=driver, battle_format=battle_format)
        teams.append(team)
    
    return teams

#   WIP
def create_battles(players:list, n_battles_each:int):
    for player in players:
        asyncio.gather()
        asyncio.create_task(player.battle_against())

async def main():
    start_time = time.time()
    n_players = 1
    teams = generate_random_teams(n_players)
   
    #players = [player.driver for player in teams]
    #end = (asyncio.run_coroutine_threadsafe( cross_evaluate(players, 2), POKE_LOOP))
    #logger.info(end.result(timeout=10000))
    #create_battles(players, 2)
    #await cross_evaluate(players, 2)


    teams[0].create_random_team(MyPokedex())
    #logger.info(this_gen_pokedex.pokedex["rhydon"])

    logger.info(f"total time: {time.time() - start_time}")
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
