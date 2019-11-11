import random

from config import logger
from showdown.evaluate import evaluate
from showdown.engine.objects import StateMutator
from showdown.engine.find_state_instructions import get_all_state_instructions
from showdown.engine.select_best_move_util import *

def make_a_choice(battles):
    # Battles is a list of possible states the opponent's team might be in
    # The list is based on guesses done by the framework, one battle per guess
    # There's always at least one battle
    # The probability of each battle/state can be assumed to be equal

    # Below a battle is transformed into a StateMutator
    # We can apply choices to the StateMutator in order to create new states
    a_battle = battles[0]
    a_state = a_battle.to_object()
    a_mutator = StateMutator(a_state)

    # Fetch possible options for you and your opponent by calling get_all_options on a StateMutator
    # user_options includes using one of your four moves or switching to a remaining Pokémon
    # opponent_options is based on assumptions about what the opponent might be able to do
    user_options, opponent_options = get_all_options(a_mutator)

    # We can evaluate a state using the pre-defined evaluate method
    # The method is already fine-tuned in order to save us some time
    # But you can play around with it by checking out evaluate.py
    a_score = evaluate(a_mutator.state)

    # By picking an option and assuming the opponent's option, we can generate a list of low-level state instructions
    # Because certain moves can lead to several different states (because of randomness), the list of possible instructions might be long
    # Applying one of the possible instructions to the StateMutator mutates the state
    # After evaluating the score of the new state, we might want to reverse the changes and try something else
    all_possible_instructions = get_all_state_instructions(a_mutator, user_options[0], opponent_options[0])
    a_mutator.apply(all_possible_instructions[0].instructions)
    a_mutator.reverse(all_possible_instructions[0].instructions)

    # Logging data might be handy
    logger.debug("User's options: {}".format(user_options))
    logger.debug("Opponent's options: {}".format(opponent_options))
    logger.debug("Current state's score: {}".format(a_score))

    # For now, let's just return a random choice
    a_random_choice = random.choice(user_options)
    logger.debug("Move chosen: {}".format(a_random_choice))
    return a_random_choice
