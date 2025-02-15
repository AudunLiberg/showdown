import constants
import config
from config import logger

from showdown.evaluate import evaluate
from showdown.decide import pick_safest
from showdown.helpers import battle_is_over

from .objects import StateMutator
from .find_state_instructions import get_all_state_instructions

def move_item_to_front_of_list(l, item):
    all_indicies = list(range(len(l)))
    this_index = l.index(item)
    all_indicies.remove(this_index)
    all_indicies.insert(0, this_index)
    return [l[i] for i in all_indicies]

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

def get_payoff_matrix(mutator, depth=2, forced_options=None, prune=None):
    """
    :param mutator: a StateMutator object representing the state of the battle
    :param depth: the remaining depth before the state is evaluated
    :param forced_options: options that can be forced instead of using `get_all_options`
    :param prune: specify whether or not to prune the tree
    :return: a dictionary representing the potential move combinations and their associated scores
    """
    if prune is None:
        prune = True

    winner = battle_is_over(mutator.state)
    if winner:
        return {(constants.DO_NOTHING_MOVE, constants.DO_NOTHING_MOVE): evaluate(mutator.state) + WON_BATTLE*depth*winner}

    depth -= 1
    if forced_options:
        user_options, opponent_options = forced_options
    else:
        user_options, opponent_options = get_all_options(mutator)

    # if the battle is not over, but the opponent has no moves - we want to return the user options as moves
    # this is a special case in a random battle where the opponent's pokemon has fainted, but the opponent still
    # has reserves left that are unseen
    if opponent_options == [constants.DO_NOTHING_MOVE] and mutator.state.opponent.active.hp == 0:
        return {(user_option, constants.DO_NOTHING_MOVE): evaluate(mutator.state) for user_option in user_options}

    state_scores = dict()

    best_score = float('-inf')
    for i, user_move in enumerate(user_options):
        worst_score_for_this_row = float('inf')
        skip = False

        # opponent_options can change during the loop
        # using opponent_options[:] makes a copy when iterating to ensure no funny-business
        for j, opponent_move in enumerate(opponent_options[:]):
            if skip:
                state_scores[(user_move, opponent_move)] = float('nan')
                continue

            score = 0
            state_instructions = get_all_state_instructions(mutator, user_move, opponent_move)
            if depth == 0:
                for instructions in state_instructions:
                    mutator.apply(instructions.instructions)
                    t_score = evaluate(mutator.state)
                    score += (t_score * instructions.percentage)
                    mutator.reverse(instructions.instructions)

            else:
                for instructions in state_instructions:
                    this_percentage = instructions.percentage
                    mutator.apply(instructions.instructions)
                    safest = pick_safest(get_payoff_matrix(mutator, depth, prune=prune))
                    score += safest[1] * this_percentage
                    mutator.reverse(instructions.instructions)

            state_scores[(user_move, opponent_move)] = score

            if score < worst_score_for_this_row:
                worst_score_for_this_row = score

            if prune and score < best_score:
                skip = True

                # MOST of the time in pokemon, an opponent's move that causes a prune will cause a prune elsewhere
                # move this item to the front of the list to prune faster
                opponent_options = move_item_to_front_of_list(opponent_options, opponent_move)

        if worst_score_for_this_row > best_score:
            best_score = worst_score_for_this_row

    return state_scores
