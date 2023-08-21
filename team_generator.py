import time
from typing import Union, Any
import asyncio
from loguru import logger
import numpy as np
from game_setup import MyPokedex
from driver import Driver
from poke_env.player.internals import POKE_LOOP
from poke_env.player import SimpleHeuristicsPlayer
from poke_env.teambuilder import TeambuilderPokemon, Teambuilder
from tournament import big_tournament
import pickle
class Team(Teambuilder):
    ''' Parent class that contains the pokemon rooster and the driver which is agent '''

    def __init__(self, rooster:Union[None, str] = None, driver:Union[None, Any] =None, battle_format:str = "gen1ou") -> None:
        self.rooster = rooster
        self.driver = driver
        self.battle_format = battle_format

    def create_random_team(self, pokedex:MyPokedex):
        self.rooster = []
        options = list(pokedex.pokedex.keys())
        for _ in range(6):
            choice = np.random.choice(options)
            pokemon = pokedex.pokedex[choice]
            options.remove(choice)
            #choose random ability, evs, and moveset,
            pokemon.randomize_all()
            self.rooster.append(TeambuilderPokemon(species=pokemon.name, moves=pokemon.moves, level=100))
        self.rooster = self.join_team(self.rooster)

    def yield_team(self):
        #logger.info(self.rooster)
        return self.rooster
    
#custom
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
    pokedex = MyPokedex()
    team = Team()
    team.create_random_team(pokedex)
    #await simple_tournament(1000)
    #await big_tournament(n_big_group= 25, n_small_group =5, n_big_rounds=1 )
    player_1 = SimpleHeuristicsPlayer(
    battle_format="gen1ubers",
    team=team,
    max_concurrent_battles=10,
    save_replays = True)

    player_2 = SimpleHeuristicsPlayer(
    battle_format="gen1ubers",
    team=team,
    max_concurrent_battles=10,
    save_replays = True)

    logger.info(player_1._team.yield_team())

    await player_1.battle_against(player_2)

    
    logger.info(f"total time: {time.time() - start_time}")
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
