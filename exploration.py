import time
from tabulate import tabulate
from poke_env import PlayerConfiguration
from poke_env.player import Player, RandomPlayer, cross_evaluate
import asyncio

my_player_config = PlayerConfiguration("my_username", None)

class MaxDamagePlayer(Player):
    def choose_move(self, battle):
        # If the player can attack, it will
        #print(f""" {battle.active_pokemon} {battle.active_pokemon._type_1} vs {battle.opponent_active_pokemon}""")
        if battle.available_moves:
            # Finds the best move among available ones
            best_move = max(battle.available_moves, key=lambda move: move.base_power)
            #print(best_move)
            return self.create_order(best_move)

        # If no attack is available, a random switch will be made
        else:
            move = self.choose_random_move(battle)
            #print(move)
            return move


async def main():
    # We create three random players
    start = time.time()

    # We create two players.
    random_player = RandomPlayer(
        battle_format="gen1randombattle",
        save_replays = True
    )
    max_damage_player = MaxDamagePlayer(
        battle_format="gen1randombattle",
    )

    # Now, let's evaluate our player
    await max_damage_player.battle_against(random_player, n_battles=1)

    print(
        "Max damage player won %d / 100 battles [this took %f seconds]"
        % (
            max_damage_player.n_won_battles, time.time() - start
        )
    )

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())


