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
from monte_carlo_tree_search import Node

def all_successors(current: Node, board: 'Board') -> 'list[Node]':
    """
    Generate all possible successors from the current node.
    """
    actions = board.get_actions()
    successors = []
    for a in actions:
        undo = (board.m[a[0]][a[1]],board.m[a[2]][a[3]])
        successors.append(Node(-current.player,current,a,undo,current.depth+1))
    return successors

def successors_with_relative_score(current: Node, board: 'Board') -> 'list[Node]':
    """
    Generate all possible successors from the current node and evaluate them depending on the action used.
    """
    actions = board.get_actions()
    successors = []
    for a in actions:
        undo = (board.m[a[0]][a[1]],board.m[a[2]][a[3]])
        board = board.play_action(a)

        new_tower_val = board.m[a[2]][a[3]]

        old_tower_sign = is_positive(undo[1])
        new_tower_sign = is_positive(board.m[a[2]][a[3]])

        if old_tower_sign == new_tower_sign:
            successors.append(Node(-current.player,current,a,undo,current.depth+1,-1/new_tower_val))
        else:
            successors.append(Node(-current.player,current,a,undo,current.depth+1,new_tower_val))
        
        board.m[a[0]][a[1]] = undo[0]
        board.m[a[2]][a[3]] = undo[1]
            
    return successors

def successors_with_tower_score(current: Node, board: 'Board') -> 'list[Node]':
    """
    Generate all possible successors from the current node and evaluate them depending on the board evaluation.
    """
    actions = board.get_actions()
    successors = []
    for a in actions:
        undo = (board.m[a[0]][a[1]],board.m[a[2]][a[3]])
        board = board.play_action(a)

        score = 0
        for i,j,v in board.get_towers():
            if abs(board.m[i][j]) == 5:
                score += 1.55 * is_positive(v)
            elif not board.is_tower_movable(i,j):
                score += 1.5 * is_positive(v)
            else:
                score += is_positive(v)

        score = score + current.player * current.C

        successors.append(Node(-current.player,current,a,undo,current.depth+1,score, current.player * current.C))

        board.m[a[0]][a[1]] = undo[0]
        board.m[a[2]][a[3]] = undo[1]
            
    return successors