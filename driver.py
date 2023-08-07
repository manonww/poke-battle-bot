from poke_env.environment import Battle, Move, Pokemon
from poke_env.environment.status import Status
from poke_env.environment.pokemon_type import PokemonType
import numpy as np
import tensorflow as tf
from typing import Dict
class Driver():
    def __init__(self) -> None:
        self.nn = None
        self.input_shape = None
    
    def transform_status(self, status)-> np.array:
        ''' Takes in status and one hot encodes it
            shape = n_statuses, '''
        status_array = np.zeros(7)

        if status == Status.FNT:
            status_array[0] = 1
        elif status == Status.BRN:
            status_array[1] = 1
        elif status == Status.FRZ:
            status_array[2] = 1
        elif status == Status.PAR:
            status_array[3] = 1
        elif status == Status.PSN:
            status_array[4] = 1
        elif status == Status.SLP:
            status_array[5] = 1
        elif status == Status.TOX:
            status_array[6] = 1
        
        return status_array

    def transform_boosts(self, boosts:Dict[str,int]) -> np.array:
        ''' Transforms boosts such as atk into array'''
        boosts_array = np.zeroes(7)
        n = 0
        for key, value in boosts.items():
            if value != 0:
                #normalize value
                boosts_array[n] = value/6
            n +=1
        return boosts_array
    
    def transform_type(self,type:int) -> np.array:
        type_array = np.zeros(15)
        type_list = ['BUG', 'DRAGON', 'ELECTRIC', 'FIGHTING', 'FIRE', 'FLYING', 'GHOST', 'GRASS', 'GROUND', 'ICE', 'NORMAL', 'POISON', 'PSYCHIC', 'ROCK', 'WATER']

        if type == PokemonType.BUG:
            type_array[type_list.index('BUG')] = 1
        if type == PokemonType.DRAGON:
            type_array[type_list.index('DRAGON')] = 1
        if type == PokemonType.ELECTRIC:
            type_array[type_list.index('ELECTRIC')] = 1
        if type == PokemonType.FIGHTING:
            type_array[type_list.index('FIGHTING')] = 1
        if type == PokemonType.FIRE:
            type_array[type_list.index('FIRE')] = 1
        if type == PokemonType.FLYING:
            type_array[type_list.index('FLYING')] = 1
        if type == PokemonType.GHOST:
            type_array[type_list.index('GHOST')] = 1
        if type == PokemonType.GRASS:
            type_array[type_list.index('GRASS')] = 1
        if type == PokemonType.GROUND:
            type_array[type_list.index('GROUND')] = 1
        if type == PokemonType.ICE:
            type_array[type_list.index('ICE')] = 1
        if type == PokemonType.NORMAL:
            type_array[type_list.index('NORMAL')] = 1
        if type == PokemonType.POISON:
            type_array[type_list.index('POISON')] = 1
        if type == PokemonType.PSYCHIC:
            type_array[type_list.index('PSYCHIC')] = 1
        if type == PokemonType.ROCK:
            type_array[type_list.index('ROCK')] = 1
        if type == PokemonType.WATER:
            type_array[type_list.index('WATER')] = 1
        
        return type_array
        



    def parse_my_active_pokemon_input(self,my_pokemon:Pokemon) -> np.array:
        ''' parse input of mx active pokemon in existing turn'''
        if my_pokemon is not None:
            hp = my_pokemon.current_hp_fraction
            status = my_pokemon.status
            boosts = my_pokemon.boosts
            types = my_pokemon.types
            moves:list[Move] = my_pokemon.moves
        

    def parse_input(self,battle:Battle) -> np.array:
        ''' Take in input of the battle and parse it to make an
        array for nn input '''
        self.parse_all_active_pokemons_input(battle.active_pokemons )
        self.parse_bench_pokemons()

    def choose_top_legal_move(move_priority:np.array):
        ''' Choose the top legal move '''
        pass

    def make_a_move(self, battle:Battle) -> Move:
        ''' Take in input about the current state of the battle and 
        decide on which move to play / which pokemon to switch '''

        move_priority = self.nn.predict(self.parse_input(battle))
        move = self.choose_top_legal_move(move_priority)
        return move
