import random
import subprocess
import asyncio
import heapq
import io
import time
import  pickle
from loguru import logger
from poke_env.player import RandomPlayer, SimpleHeuristicsPlayer, Player

from game_setup import MyPokedex
from poke_env.teambuilder import Teambuilder
from poke_env.player.utils import cross_evaluate, background_cross_evaluate
from team_generator import Team
from showdown_api import generate_random_team_showdown, validate_team

class MyTeamBuilder(Teambuilder):
    def __init__(self, team:str):
        #self.team = self.join_team(self.parse_showdown_team(team))
        self.team = team
    def yield_team(self):
        return self.team

def replay_saving(player:Player,to_save:bool) -> Player:
    player._save_replays = to_save
    return player


        
async def return_player_with_team(pokedex:MyPokedex) -> Player:
    #team = MyTeamBuilder(await generate_random_team_showdown())
    team = Team()
    await team.create_random_team(pokedex)
    player = SimpleHeuristicsPlayer(
            battle_format="gen1ubers",
            team=team,
            max_concurrent_battles=20,
            save_replays = False)
    return player

async def generate_players(player_list:list,n_new:int, pokedex:MyPokedex):
    ''' Generate new random players '''
    if n_new >0:
        tasks = [return_player_with_team(pokedex) for i in range(0, n_new)]
        results = await asyncio.gather(*tasks)
        player_list += results
    return player_list

async def n_man_tournament(player_list=[],n_rounds:int =100, n_players:int = 5, top_n:int = 2, each_fights_n:int=1, log:bool = False, pokedex:MyPokedex=None) -> list:
    ''' create small n man tournment where they battle eachother and top_2 survives'''
    for n in range(n_rounds):
        player_list = await generate_players(player_list,n_new= n_players - len(player_list), pokedex=pokedex)
        results = await asyncio.wait_for(cross_evaluate(player_list,each_fights_n), timeout=n_players**3)
        #get top n players
        parsed_results = {key:sum(value for value in results[key].values() if value is not None) for key in results}
        top_n_players = [item[0] for item in heapq.nlargest(top_n, parsed_results.items(), key=lambda item: item[1])]
        winner_list = [player for player in player_list if player.username in top_n_players]
        #logger.print(parsed_results)
        player_list = winner_list
    if log:
        #logger.info(parsed_results)
        #logger.info(top_n_players)
        pass
    return player_list

async def big_tournament(n_big_group:int = 25, n_small_group:int =5, n_big_rounds=10 ) -> list:
    ''' overarching rules for tournement'''
    big_tournament_players = []
    pokedex = MyPokedex()
    for big_n in range(n_big_rounds):
        logger.info(f"big round {big_n}")
        #generate new players to fill the gaps
        start_generation = time.time()
        big_tournament_players  =   await generate_players(big_tournament_players, n_new=n_big_group-len(big_tournament_players), pokedex=pokedex)
        logger.info(f"It took {time.time()-start_generation} secs to generate teams")
        big_tournament_players = [replay_saving(player,False) for player in big_tournament_players]
        random.shuffle(big_tournament_players)
        start_bracket = time.time()
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
        logger.info(f"It took {time.time()-start_bracket} secs to generate brackets")
        #run mini tournements and get winners
        start_mini_tour = time.time()
        small_winner_list = []
        #for bracket in brackets_list:
        #    small_winners = await n_man_tournament(bracket,n_rounds=1,n_players=len(bracket), top_n=2, each_fights_n=4  )
        #    small_winner_list += small_winners
        #run tournaments simulatniusly
        tasks = [n_man_tournament(bracket,n_rounds=1,n_players=len(bracket), top_n=2, each_fights_n=4 ) for bracket in brackets_list]
        results = await asyncio.gather(*tasks)
        #flatten list
        big_tournament_players = [item for sublist in results for item in (sublist if isinstance(sublist, list) else [sublist])]
        logger.info(f"It took {time.time()-start_mini_tour} secs to play mini tournaments")
        #run big tournament
        #start_big_tour = time.time()
        #small_winner_list = [replay_saving(player,True) for player in small_winner_list]
        #big_winner_list = await n_man_tournament(small_winner_list,n_rounds=1, n_players=len(small_winner_list), top_n = n_small_group, each_fights_n=3, log=False)
        #big_tournament_players = big_winner_list
        #logger.info(f"It took {time.time()-start_big_tour} secs to play big tournaments")
        #save winners every 10 big rounds
        if big_n % 100 ==0:
            big_tournament_players = [replay_saving(player, True) for player in big_tournament_players]
            hall_of_fame_winner = await n_man_tournament(big_tournament_players,n_rounds=1,n_players=len(big_tournament_players), top_n=1, each_fights_n=1 )
            save_teams = [winner._team.rooster for winner in hall_of_fame_winner ] 
            big_tournament_players = [replay_saving(player, False) for player in big_tournament_players]
            with open(f"hall_of_fame/my_generator/round_{big_n}_winner.pkl", 'wb') as file:
                pickle.dump(save_teams, file)

    return big_tournament_players                

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