import subprocess
import heapq
import pickle
import random
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
    #folder_path = r"C:\Users\diana\Documents\Python projects\pokemon\pokemon-showdown"
    folder_path = r"C:/Users/Robert/Downloads/Cheating is learning/pokemon-showdown"
    gen_node_command = f'node pokemon-showdown generate-team {battle_format}'
    val_node_command = f'node pokemon-showdown validate-team {battle_format} '
    
    while True:
        team = subprocess.check_output(f'cd /d {folder_path} && {gen_node_command}', shell=True)
        try:
            subprocess.check_output(f'cd /d {folder_path} && {val_node_command} ', shell=True, input=team).decode()
            return team.decode()
        except:
            print("invalid team")
            pass


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

def generate_players(player_list:list,n_new:int):
    ''' Generate new random players '''
    for _ in range(n_new):
            team = MyTeamBuilder(generate_random_team_showdown())
            player = SimpleHeuristicsPlayer(
                    battle_format="gen1ubers",
                    team=team,
                    max_concurrent_battles=10,
                    save_replays = True)
            player_list.append(player)
    return player_list

async def big_tournament(n_big_group:int = 25, n_small_group:int =5, n_big_rounds=10 ):
    ''' overarching rules for tournement'''
    big_tournament_players = []
    for big_n in range(n_big_rounds):
        logger.info(f"big round {big_n}")
        #generate new players to fill the gaps
        big_tournament_players  =  generate_players(big_tournament_players, n_new=n_big_group-len(big_tournament_players))
        random.shuffle(big_tournament_players)
        #create smaller brackets
        n_brackets = int(n_big_group/n_small_group)
        brackets_list = []
        for _ in range(n_brackets):
            small_bracket = []
            while len(small_bracket) <  n_small_group:
                try:
                    small_bracket.append(big_tournament_players.pop(0))
                except IndexError:
                    small_bracket.append(big_tournament_players[0])
            brackets_list.append(small_bracket)
        #run mini tournements and get winners
        small_winner_list = []
        for bracket in brackets_list:
            small_winners = await n_man_tournament(bracket,n_rounds=1,n_players=len(bracket), top_n=2, each_fights_n=2  )
            small_winner_list += small_winners
        
        big_winner_list = await n_man_tournament(small_winner_list,n_rounds=1, n_players=len(small_winner_list), top_n = n_small_group, each_fights_n=2, log=True)
        big_tournament_players = big_winner_list
    with open("hall_of_fame/top_n_players", 'wb') as file:
        	pickle.dump(big_tournament_players, file)
                


async def n_man_tournament(player_list=[],n_rounds:int =100, n_players:int = 5, top_n:int = 2, each_fights_n:int=1, log:bool = False) -> list:
    ''' create small n man tournment where they battle eachother and top_2 survives'''
    for n in range(n_rounds):
        player_list = generate_players(player_list,n_new= n_players - len(player_list))
        results = await asyncio.wait_for(cross_evaluate(player_list,each_fights_n), timeout=n_players**3)
        #get top n players
        parsed_results = {key:sum(value for value in results[key].values() if value is not None) for key in results}
        top_n_players = [item[0] for item in heapq.nlargest(top_n, parsed_results.items(), key=lambda item: item[1])]
        winner_list = [player for player in player_list if player.username in top_n_players]
        #logger.print(parsed_results)
        player_list = winner_list
    if log:
        logger.info(parsed_results)
        logger.info(top_n_players)
    return player_list



async def simple_tournament(n_rounds:int = 1000,):
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
        try: 
            #if battle lags p1 wins
            asyncio.wait_for(await player_1._handle_threaded_coroutines( player_1._battle_against(player_2, 1) ), timeout=10 )

        except Exception as e:
            logger.info("exception time")
            logger.info(e)
            pass
        current_round +=1
    logger.info(f"final champion won {player_1.n_won_battles}")





async def main():
    start_time = time.time()

    #await simple_tournament(1000)
    await big_tournament(n_big_group= 50, n_small_group =5, n_big_rounds=100 )
    logger.info(f"total time: {time.time() - start_time}")
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
