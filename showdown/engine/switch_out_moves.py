import constants


def switch_out_move_triggered(move, damage_amounts):
    if move[constants.ID] in constants.SWITCH_OUT_MOVES:
        if move[constants.ID] == 'partingshot' and move[constants.ACCURACY]:
            return True
        else:
            return damage_amounts is not None and all(damage_amounts)


def get_best_switch_pokemon(mutator, instructions, attacker, attacking_side, defending_move, first_move):
    from .select_best_move_util import get_payoff_matrix
    from .select_best_move_util import get_possible_switches
    switches = get_possible_switches(attacking_side)
    if not switches or instructions.frozen:
        return None

    if first_move:
        other_move = defending_move[constants.ID]
    else:
        other_move = constants.DO_NOTHING_MOVE

    if attacker == constants.SELF:
        best_switch = max(get_payoff_matrix(mutator, depth=1, forced_options=(switches, [other_move])).items(), key=lambda x: x[1])[0][0]
    else:
        best_switch = min(get_payoff_matrix(mutator, depth=1, forced_options=([other_move], switches)).items(), key=lambda x: x[1])[0][1]

    return best_switch.split()[-1].strip()
