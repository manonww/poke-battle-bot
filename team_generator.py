import time
from typing import Union, Any
import asyncio
import random
from loguru import logger
import numpy as np
from game_setup import MyPokedex
from driver import Driver
from poke_env.player.internals import POKE_LOOP
from poke_env.player import SimpleHeuristicsPlayer
from poke_env.teambuilder import TeambuilderPokemon, Teambuilder
from showdown_api import validate_team
from typing import Union,List
import pickle
class Team(Teambuilder):
    ''' Parent class that contains the pokemon rooster and the driver which is agent '''

    def __init__(self, rooster:Union[None, str] = None, driver:Union[None, Any] =None, battle_format:str = "gen1ou") -> None:
        self.rooster = rooster
        self.driver = driver
        self.battle_format = battle_format

    
    async def validate_pokemon(self, pokemon:TeambuilderPokemon) ->bool:
        ''' Checks if individual pokemon is valid for showdown'''
        valid = await validate_team(pokemon.formatted, "gen1ou")
        return valid
    
    async def create_random_pokemon(self,i:int, options:List[str], pokedex:MyPokedex) ->TeambuilderPokemon:
        ''' Creates and validates random pokemon based on int and options '''
        valid = False
        while not valid:
            pokemon = pokedex.pokedex[options[i]]
            #choose random ability, evs, and moveset,
            pokemon.randomize_all()
            tbpokemon = TeambuilderPokemon(species=pokemon.name, moves=pokemon.moves, level=100)
            valid = await self.validate_pokemon(tbpokemon)
            #if pokemon is not valid we choose another one
            i += 10
        return tbpokemon
    

    async def create_random_team(self, pokedex:MyPokedex):
        ''' Create a random team and validates it'''
        valid_team = False
        while not valid_team:
            self.rooster = []
            options = list(pokedex.pokedex.keys())
            random.shuffle(options)
            # create and validate random pokemons async
            tasks = [asyncio.create_task(self.create_random_pokemon(i, options, pokedex)) for i in range(6)]
            results = await asyncio.gather(*tasks)
            self.rooster = self.join_team(results)
            valid_team = await validate_team(self.rooster, "gen1ou")

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

