from showdown.sandbox.algpip_plays_pokémon import make_a_choice
from config import logger

def find_best_move(battle):
    battles = battle.prepare_battles(join_moves_together=True)
    logger.debug("")
    choice = make_a_choice(battles)
    logger.debug("")
    return choice
