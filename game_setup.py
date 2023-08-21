from poke_env.data import GenData
from abstract_pokemon_class import AbstractPokemon
from loguru import logger
from typing import Dict
import pandas as pd
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
        learnset = self.get_moves()
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
            possible_moves = list(set(learnset[pokemon]))
            new_pokedex[pokemon] = AbstractPokemon(name, types, possible_abilities, possible_moves)

        new_pokedex = self.apply_exclusion(new_pokedex)
        self.pokedex = new_pokedex
        logger.info(f"New pokedex length: {len(self.pokedex)}")

    def get_moves(self,):
        ''' Get all legal moves for gen 1 and map them to pokemon that can learn it in gen 1'''
        moves = pd.read_csv("data/moves/moves.csv")
        moves = moves.loc[moves["generation_id"]==1]
        moves["identifier"] = moves["identifier"].str.replace("-","")
        moves_dict = moves.loc[:,["id","identifier"]].set_index("id").to_dict()["identifier"]
        pokemon_species = pd.read_csv("data/moves/pokemon_species.csv")
        pokemon_species = pokemon_species.loc[pokemon_species["generation_id"]==1]
        pokemon_species["identifier"] = pokemon_species["identifier"].str.replace("-","")
        species_dict = pokemon_species.loc[:,["id","identifier"]].set_index("id").to_dict()["identifier"]

        learnset = pd.read_csv("data/moves/pokemon_moves.csv")
        learnset = learnset.loc[(learnset["version_group_id"]==1) & (learnset["pokemon_move_method_id"] !=5)]
        learnset = learnset.loc[:,["pokemon_id", "move_id"]]
        learnset["move_id"] = learnset["move_id"].map(moves_dict)
        learnset["pokemon_id"] = learnset["pokemon_id"].map(species_dict)
        pokemon_moves_dict = learnset.groupby('pokemon_id')['move_id'].agg(list).to_dict()
        return pokemon_moves_dict

    def apply_exclusion(self, pokedex:dict) -> dict:
        ''' Remove banned items moves and pokemon in this gen format '''
        with open(f"data/banned/{self.battleformat}.json") as json_file:
            exclusions = json.load(json_file)
        self.banned_moves = exclusions["moves"]
        self.banned_pokemons = exclusions["pokemon"]
        self.banned_items = exclusions["items"]
        
        new_pokedex = {key: value for key, value in pokedex.items() if key not in self.banned_pokemons}
        for key,pokemon in new_pokedex.items():
            pokemon.possible_moves = [move for move in pokemon.possible_moves if move not in self.banned_moves]

        return new_pokedex

