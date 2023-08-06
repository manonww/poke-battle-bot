from poke_env.data import GenData
from abstract_pokemon_class import AbstractPokemon
from loguru import logger
from typing import Dict
import json

class MyPokedex():

    def __init__(self, battleformat:str = "gen1ou") -> None:
        
        self.battleformat = battleformat
        self.gen = int(battleformat[3])
        self.moves = {}
        self.pokedex:Dict[str, AbstractPokemon] = {}
        self.load_gen()

    def load_gen(self):
        ''' loads data for current gen and applies banned pokemon '''
        my_gen = GenData(self.gen)
        self.natures = list(my_gen.load_natures().keys())
        learnset = my_gen.load_learnset()
        #load pokedex and exclude fan made pokemons and regional forms
        pokedex = {key: value for key, value in my_gen.load_pokedex(self.gen).items() if (value["num"] >0) & ("forme" not in value)}
        self.moves = my_gen.load_moves(self.gen)

        #logger.info(self.natures)
        #logger.info(self.learnset)
        #logger.info(len(self.pokedex))
        #logger.info(self.moves)
        self.parse_pokedex(pokedex, learnset)

    def parse_pokedex(self,pokedex:dict, learnset:dict):
        ''' Loads pokedex data and only keeps relevants things. Also merges it with learnset'''
        new_pokedex = {}
        for pokemon in pokedex:
            name = pokemon
            types = pokedex[pokemon]["types"]
            possible_abilities = list(pokedex[pokemon]["abilities"].values())
            possible_moves = list(learnset[pokemon]["learnset"].keys())
            new_pokedex[pokemon] = AbstractPokemon(name, types, possible_abilities, possible_moves)

        new_pokedex = self.apply_exclusion(new_pokedex)
        self.pokedex = new_pokedex
        logger.info(f"New pokedex length: {len(self.pokedex)}")

    def apply_exclusion(self, pokedex:dict) -> dict:
        ''' Remove banned items moves and pokemon in this gen format '''
        with open(f"banned/{self.battleformat}.json") as json_file:
            exclusions = json.load(json_file)
        self.banned_moves = exclusions["moves"]
        self.banned_pokemons = exclusions["pokemon"]
        self.banned_items = exclusions["items"]
        
        new_pokedex = {key: value for key, value in pokedex.items() if key not in self.banned_pokemons}
        for key,pokemon in new_pokedex.items():
            pokemon.possible_moves = [move for move in pokemon.possible_moves if move not in self.banned_moves]

        return new_pokedex

