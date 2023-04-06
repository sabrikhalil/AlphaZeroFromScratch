"""
Heuristics collections for Avalam.
Copyright (C) 2022, Hugo Barral, Khalil Sabri
Polytechnique Montréal

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.

"""

from avalam import Board

from utils import is_positive


def predict_score(board: Board, action: 'tuple[int, int, int, int]') -> float:
    """
    The board evaluation heuristic used in simuations for MCTS.
    """
    undo = (board.m[action[0]][action[1]],board.m[action[2]][action[3]])
    board.play_action(action)

    v = board.m[action[2]][action[3]]
    sign = is_positive(v)
    sign_undo = is_positive(undo[1])

    # Penalize covering a pawn from the same color as the player
    penality = 1
    if sign == sign_undo:
        penality = -1

    score = 0
    if abs(board.m[action[2]][action[3]]) == 5:
        score = 1.55 * sign
    elif not board.is_tower_movable(action[2],action[3]):
        score = 1.5 * sign
    else:
        # Diminish the action value in the pawn can be captured during the next turn
        capture = 0
        others = [(a[2],a[3]) for a in board.get_tower_actions(action[2],action[3])]
        for o in others:
            if is_positive(board.m[o[0]][o[1]]) != sign:
                capture = 1
                break
        if capture == 0:
            score = sign * penality
        else:
            score = 0.5 * sign * penality

    board.m[action[0]][action[1]] = undo[0]
    board.m[action[2]][action[3]] = undo[1]

    return score

def middle_game_wait(time_left: float, step: int, step_threshold: int=10) -> float:
    """
    Time allocation heuristic
    Inspired by Huang et al. - 2010 - Time Management for Monte-Carlo Tree Search Applied to the Game of Go 
    """
    return time_left / (4  + max(step_threshold-step,0))