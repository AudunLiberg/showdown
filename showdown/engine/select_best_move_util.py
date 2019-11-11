import constants
import config
from config import logger

from showdown.evaluate import evaluate
from showdown.decide import pick_safest
from showdown.helpers import battle_is_over

from .objects import StateMutator
from .find_state_instructions import get_all_state_instructions

def get_possible_switches(side):
    switches = []
    for pkmn_name, pkmn in side.reserve.items():
        if pkmn.hp > 0:
            switches.append("{} {}".format(constants.SWITCH_STRING, pkmn_name))
    return switches


def get_user_options(side, force_switch):
    if force_switch:
        possible_moves = []
    else:
        possible_moves = [m[constants.ID] for m in side.active.moves if not m[constants.DISABLED]]

    if side.trapped:
        possible_switches = []
    else:
        possible_switches = get_possible_switches(side)

    return possible_moves + possible_switches


def get_opponent_options(side):
    if side.active.hp <= 0:
        possible_moves = []
    else:
        possible_moves = [m[constants.ID] for m in side.active.moves if not m[constants.DISABLED]]

    possible_switches = get_possible_switches(side)

    return possible_moves + possible_switches


def get_all_options(mutator: StateMutator):
    force_switch = mutator.state.force_switch or mutator.state.self.active.hp <= 0
    wait = mutator.state.wait or mutator.state.opponent.active.hp <= 0

    # double faint or team preview
    if force_switch and wait:
        mutator.state.self.trapped = False
        mutator.state.force_switch = False
        mutator.state.wait = False
        user_options = get_user_options(mutator.state.self, force_switch) or [constants.DO_NOTHING_MOVE]
        opponent_options = get_opponent_options(mutator.state.opponent) or [constants.DO_NOTHING_MOVE]
        return user_options, opponent_options

    if force_switch:
        opponent_options = [constants.DO_NOTHING_MOVE]
        mutator.state.force_switch = False
        mutator.state.self.trapped = False
        wait = False
    else:
        opponent_options = get_opponent_options(mutator.state.opponent)

    if wait:
        user_options = [constants.DO_NOTHING_MOVE]
    else:
        user_options = get_user_options(mutator.state.self, force_switch)

    if not user_options:
        user_options = [constants.DO_NOTHING_MOVE]

    if not opponent_options:
        opponent_options = [constants.DO_NOTHING_MOVE]

    return user_options, opponent_options
