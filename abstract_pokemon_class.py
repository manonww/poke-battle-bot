import numpy as np
import random
class AbstractPokemon():
    def __init__(self, name:str, types:list, possible_abilities:list, possible_moves:list ) -> None:
        self.name = name
        self.types = types
        self.possible_abilities = possible_abilities
        self.possible_moves = possible_moves
        self.held_item = None
        self.ability = None
        self.moves = None
        self.evs = None

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:

        return (
            f"{self.name} {self.types} "
            f"[ability: {self.ability}] "
            f"[moves: {self.moves}] "
            f"nature : {self.nature} "
            f"item : {self.held_item} "
        )
    
    def randomize_ability(self) -> None:
        ''' Choose and set random ability from possible abilities'''
        self.ability =  np.random.choice(self.possible_abilities)
    
    def randomize_evs(self) -> None:
        ''' Choose random EVS to max '''
        ev_list = ["Atk", "Def", "SpA", "SpD", "Spe"]
        max_ev1 = ev_list.pop(random.randint(0,(len(ev_list)-1)))
        max_ev2 = ev_list.pop(random.randint(0,(len(ev_list)-1)))
        min_ev = ev_list.pop(random.randint(0,(len(ev_list)-1)))
        self.evs = {max_ev1:252, max_ev2:252, min_ev:4}

    def randomize_moveset(self) -> None:
        ''' Choose 4 random moves for pokemon'''
        possible_moves = self.possible_moves
        self.moves = []
        #choose 4 random moves 
        for _ in range(4):
            move = np.random.choice(possible_moves)
            self.moves.append(move)
            possible_moves.remove(move)
        
        assert len(self.moves) ==4

    def randomize_all(self, item_list:list, nature_list:list, ):
        ''' Choose random ability, evs, moveset, nature and held item'''
        self.randomize_ability()
        self.randomize_evs()
        self.randomize_moveset()
        self.held_item = np.random.choice(item_list)
        self.nature = np.random.choice(nature_list)