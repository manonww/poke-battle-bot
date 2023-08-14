import subprocess
import time
from typing import Union, Any
import asyncio
import tabulate
from loguru import logger
import numpy as np
from game_setup import MyPokedex
from driver import Driver
from poke_env.player.internals import POKE_LOOP
from poke_env.player.utils import cross_evaluate, background_cross_evaluate
from poke_env.teambuilder import Teambuilder
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
    
class MyTeamBuilder(Teambuilder):
    def __init__(self, team:str):
        #self.team = self.join_team(self.parse_showdown_team(team))
        self.team = team
    def yield_team(self):
        return self.team

from poke_env.player import RandomPlayer, SimpleHeuristicsPlayer

def generate_random_team_showdown(battle_format:str = "gen1ou") ->str:
    ''' Generate a random team directly from showdown server '''
    folder_path = r"C:\Users\diana\Documents\Python projects\pokemon\pokemon-showdown"
    gen_node_command = f'node pokemon-showdown generate-team {battle_format}'
    val_node_command = f'node pokemon-showdown validate-team {battle_format} '

    return subprocess.check_output(f'cd /d {folder_path} && {gen_node_command}', shell=True).decode()

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

async def simple_tournament(n_rounds:int = 200,):
    current_round = 0
    team1 = MyTeamBuilder(generate_random_team_showdown())
    team2 = MyTeamBuilder(generate_random_team_showdown())
    player_1 = SimpleHeuristicsPlayer(
    battle_format="gen1ubers",
    team=team1,
    max_concurrent_battles=10,
    save_replays = True)

    player_2 = SimpleHeuristicsPlayer(
    battle_format="gen1ubers",
    team=team2,
    max_concurrent_battles=10)
    await player_1.battle_against(player_2)
    player_1.n_lost_battles
    while n_rounds > current_round:
        logger.info(f"round: {current_round}")
        if player_1.n_lost_battles == 0:
            player_1._save_replays = True
        else: 
            player_1 = player_2
        #player_1 is winning mon
        player_2 = SimpleHeuristicsPlayer(
        battle_format="gen1ubers",
        team=MyTeamBuilder(generate_random_team_showdown()),
        max_concurrent_battles=10)

        await player_1.battle_against(player_2)
        current_round +=1
    logger.info(f"final champion won {player_1.n_won_battles}")





async def main():
    start_time = time.time()

    await simple_tournament(200)

    logger.info(f"total time: {time.time() - start_time}")
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
