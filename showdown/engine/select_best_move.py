from showdown.sandbox.algpip_plays_pokémon import make_a_choice

def find_best_move(battle):
    battles = battle.prepare_battles(join_moves_together=True)
    return make_a_choice(battles)
