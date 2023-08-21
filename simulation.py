import time
from poke_env import PlayerConfiguration
from poke_env.player import Player, RandomPlayer, cross_evaluate
from game_setup import MyPokedex
from team_generator import Team

import asyncio
from loguru import logger

async def main(iterrations:int = 5, n_teams:int = 100, top_n:int = 10):
    logger.info("Get started")
    #Create Random Teams
    start_time = time.time()
    pokedex = MyPokedex()
    team1 = Team()
    team2 = Team()
    await team1.create_random_team(pokedex)
    await team2.create_random_team(pokedex)
    logger.info(team1.rooster)
    logger.info(team2.rooster)
    #Create Create Random Drivers
    p1 = RandomPlayer(team=team1, battle_format="gen1ou", save_replays=True)
    p2 = RandomPlayer(team=team2, battle_format="gen1ou", save_replays=True)
    #Match teams to drivers
    await p1.battle_against(p2)
    ### LOOP

    # Create League

    # Play Matches

    # Get Top Drivers and mutate nns

    # Create League

    # Play Matches

    # Get top Teams and mutate pokemons
    


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())