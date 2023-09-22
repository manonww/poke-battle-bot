import time
from poke_env import PlayerConfiguration
from poke_env.player import Player, RandomPlayer, cross_evaluate
from game_setup import MyPokedex
from team_generator import Team
from tournament import big_tournament

import asyncio
from loguru import logger

async def main(iterrations:int = 5, n_teams:int = 100, top_n:int = 10):
    logger.info("Get started")
    import tensorflow as tf
    start_t = time.time()
    print(tf.__version__)
    print(tf.config.list_physical_devices('GPU'))
    import logging
    logging.basicConfig(level=logging.ERROR) 
    await big_tournament(n_big_rounds=3)
    logger.info(f"took in total {time.time()-start_t} seconds")
    ### LOOP

    # Create League

    # Play Matches

    # Get Top Drivers and mutate nns

    # Create League

    # Play Matches

    # Get top Teams and mutate pokemons
    


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())