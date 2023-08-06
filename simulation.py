import time
from poke_env import PlayerConfiguration
from poke_env.player import Player, RandomPlayer, cross_evaluate
import asyncio
from loguru import logger

async def main(iterrations:int = 5, n_teams:int = 100, top_n:int = 10):
    logger.info("Get started")
    #Create Random Teams

    #Create Create Random Drivers

    #Match teams to drivers

    ### LOOP

    # Create League

    # Play Matches

    # Get Top Drivers and mutate nns

    # Create League

    # Play Matches

    # Get top Teams and mutate pokemons
    


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())