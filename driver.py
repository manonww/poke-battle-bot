from poke_env.environment import Battle, Move, Pokemon
from poke_env.environment.status import Status
from poke_env.environment.pokemon_type import PokemonType
from poke_env.environment.move_category import MoveCategory
from loguru import logger
from neural_network import DriverNetwork
from poke_env.player import Player
from poke_env.player.battle_order import DefaultBattleOrder
import numpy as np
from numba import jit
from typing import Union
import tensorflow as tf
from typing import Dict
import warnings
from numba.core.errors import NumbaWarning

warnings.simplefilter('ignore', category=NumbaWarning)

from poke_env.data.gen_data import  GenData
gen_data = GenData(1)
TYPE_CHART = gen_data.type_chart 
class Driver(Player):
    
    def random_nn(self):
        self.nn = DriverNetwork()
        self.nn.initilize_random((40,1),5)

    ##@jit(nopython=True)
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


    #@jit(nopython=True)
    def transform_boosts(self, boosts:Dict[str,int]) -> np.array:
        ''' Transforms boosts such as atk into array'''
        boosts_array = np.zeros(7)
        n = 0
        for key, value in boosts.items():
            if value != 0:
                #normalize value
                boosts_array[n] = value/6
            n +=1
        return boosts_array
    
    #@jit(nopython=True)
    def transform_type(self,type:int) -> np.array:
        ''' One hot encodes type '''
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
    
    #@jit(nopython=True)
    def parse_move_category(self,category:MoveCategory) -> int:
        ''' Parse move category to see if its status '''
        if category == MoveCategory.STATUS:
            return 1
        else: 
            return 0
    
    
    def parse_move_effectiveness(self, move:Move, battle:Battle):
        ''' Take a move and check how effective it is '''
        moves_dmg_multiplier = move.type.damage_multiplier(
            battle.opponent_active_pokemon.type_1,
            battle.opponent_active_pokemon.type_2,
            type_chart=TYPE_CHART)


        return moves_dmg_multiplier

    ##@jit
    def transform_move(self,move:Move, battle:Battle):
        ''' Transform move info such as expected damage, accuracy, status, boost '''
        #logger.info(move)
        move_effectiveness = 1
        try: 
            move_effectiveness = self.parse_move_effectiveness(move, battle)
        except:
            pass
        expected_damage = move.base_power * move.accuracy * move.expected_hits * move_effectiveness/100
        status_category = self.parse_move_category(move.category)
        #status can be move like bulk up or thunder wave. TODO: clarify
        #logger.info(f"expected_damage: {expected_damage}")
        #logger.info(f"inflicting_status: {status_category}")
        return np.array([expected_damage, status_category]) 


    ##@jit
    def parse_active_pokemons_input(self,my_pokemon:Pokemon, opponent_pokemon:Pokemon, battle:Battle) -> np.array:
        ''' parse input of active pokemons in existing turn'''
        if my_pokemon is not None:
            hp = my_pokemon.current_hp_fraction
            status = my_pokemon.status
            boosts = my_pokemon.boosts
            types = my_pokemon.types
            moves:list[Move] = list(my_pokemon.moves.values())

            hp_array= np.array([hp])
            status_array = self.transform_status(status)
            boosts_array = self.transform_boosts(boosts)
            #type_1_array = self.transform_type(types[0])
            #type_2_array = np.zeros(15)
            #if len(types) ==2:
            #    type_2_array = self.transform_type(types[1])
            #i should sum type arrays
            move_array = np.array([])
            for move in moves:
                if len(move_array) > 0:
                    move_array = np.concatenate((move_array,self.transform_move(move,battle)))
                else:
                    move_array = self.transform_move(move,battle)
            #if pokemon doesnt have 4 moves
            if len(move_array) != 8:
                move_array = np.concatenate((move_array,np.zeros(8-len(move_array))))
            
            my_pokemon_array = np.concatenate((hp_array,status_array,boosts_array,move_array))

        else:
            total = 2 + 7 + 7 + 8 #hp + status + boost  + moves
            my_pokemon_array = np.zeros(total) 

        if opponent_pokemon is not None:
            hp = opponent_pokemon.current_hp_fraction
            status = opponent_pokemon.status
            boosts = opponent_pokemon.boosts

            hp_array= np.array([hp])
            status_array = self.transform_status(status)
            boosts_array = self.transform_boosts(boosts)
            opponent_pokemon_array = np.concatenate((hp_array,status_array,boosts_array))
        else:
            total = 2 + 7 + 7  #hp + status + boost
            opponent_pokemon_array = np.zeros(total) 

        return np.concatenate((my_pokemon_array,opponent_pokemon_array))
            
        
    def parse_input(self,battle:Battle) -> np.array:
        ''' Take in input of the battle and parse it to make an
        array for nn input '''
        active_input = self.parse_active_pokemons_input(battle.active_pokemon, battle.opponent_active_pokemon, battle )
        #self.parse_bench_pokemons()
        #logger.info(active_input.shape)
        return active_input
    
    def choose_top_legal_move(self,move_priority:np.array, battle:Battle) -> Union[Pokemon, Move]:
        ''' Choose the top legal move 
            Move1, Move2, Move3, Move4, Random switch'''
        
        move_chosen = 0
        available_moves = [move._id  for move in battle.available_moves]
        move_priority = move_priority.reshape(5)
        #logger.info(f"status:{battle.active_pokemon.status} available {(available_moves)} moves and {len(battle.available_switches)}, recharge:{battle.active_pokemon.must_recharge}")
        
        #if we have to have to recharge
        if battle.active_pokemon.must_recharge and len(available_moves)>0:
            #logger.info(f"im gonna recharge: {type(available_moves[0])}:")
            return self.create_order(battle.available_moves[0])
            
        if battle.turn>100 and battle.active_pokemon.current_hp >0:
            move_priority[4] = -999
        while move_chosen == 0:
            loop_counter = 0
            best_move = move_priority.argmax()
            #switch random pokemon
            if loop_counter > 5:
                logger.info("Loop over 5, choosing random")
                self.choose_random_move()

            if best_move == 4:
                loop_counter += 1
                if len(battle.available_switches) > 0:
                    move_chosen=1
                    return self.create_order(np.random.choice(battle.available_switches))
                else:
                    move_priority[4] = -999

            #use a pokemon attack move
            else: 
                loop_counter += 1
                my_moves = list(battle.active_pokemon.moves.values())

                if battle.active_pokemon.species.lower() == "ditto":
                    if len(battle.available_moves) >0:
                        move_chosen = 1
                        return self.create_order(battle.available_moves[0])
                    else:
                        return self.create_order(np.random.choice(battle.available_switches))
                    
                move_to_use:Move = my_moves[best_move]
                if (move_to_use._id in available_moves) and (move_to_use.current_pp >0) :
                    move_chosen = 1
                    return self.create_order(move_to_use)
                else:
                    move_priority[best_move] = -999

        return best_move

    def choose_move(self, battle:Battle) -> Union[ Move, Pokemon]:
        ''' Take in input about the current state of the battle and 
        decide on which move to play / which pokemon to switch '''

        move_priority = self.nn.model.predict(self.parse_input(battle).reshape(1,38), verbose = 0)
        move = self.choose_top_legal_move(move_priority, battle)
        #logger.info(f" {self.username} {move}")
        
        #logger.info(f"turn {battle.turn}, {battle.player_role} {move} finished: {battle.finished} trapped {battle.trapped} fswitch: {battle.force_switch}")
        
        return move
