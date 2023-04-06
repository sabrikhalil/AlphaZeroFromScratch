 #!/usr/bin/env python3
"""
Avalam agent.
Copyright (C) 2023, Hugo Barral, Khalil Sabri
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

import random
import heapq

from avalam import Board

from heuristics import predict_score

def random_simulation(player: int, board: 'Board') -> float:
    """
    Launch a complete random simulation on a board until we reach a final board.
    """
    if not board.is_finished():
        actions = list(board.get_actions())
        select = random.choice(actions)
        board = board.play_action(select)
    else:
        return board.get_score()
    return random_simulation(-player, board)

def quick_random_simulation(player: int, board: 'Board') -> float:
    """
    Launch a quicker simulation by randomly selecting one pawn and action at each turns.
    """
    if not board.is_finished():
        t = (random.randint(0,board.rows-1),random.randint(0,board.columns-1))
        while not board.is_tower_movable(t[0],t[1]):
            t = (random.randint(0,board.rows-1),random.randint(0,board.columns-1))        
        action = random.choice(list(board.get_tower_actions(t[0],t[1])))

        board = board.play_action(action)
    else:
        return board.get_score()
    return quick_random_simulation(-player, board)

def semi_greedy_simulation(player: int, board: 'Board') -> float:
    """
    Launch a semi-greedy simulation by randomly selecting pawn and choosing a greedy action each turns.
    """
    if not board.is_finished():
        t = (random.randint(0,board.rows-1),random.randint(0,board.columns-1))
        while not board.is_tower_movable(t[0],t[1]):
            t = (random.randint(0,board.rows-1),random.randint(0,board.columns-1))
        
        actions = [(predict_score(board,a),a) for a in board.get_tower_actions(t[0],t[1])]
        if player > 0:
            heapq._heapify_max(actions)
        else:
            heapq.heapify(actions)

        board = board.play_action(actions[0][1])
    else:
        return board.get_score()
    return semi_greedy_simulation(-player, board)

def multiple_semi_greedy_simulation(player: int, board: 'Board', k: int=5) -> float:
    """
    Find k multiple semi-greedy actions and keep the best evaluated one at each turns.
    """
    if not board.is_finished():
        tws = []
        for i in range(k):
            t = (random.randint(0,board.rows-1),random.randint(0,board.columns-1))
            while not board.is_tower_movable(t[0],t[1]):
                t = (random.randint(0,board.rows-1),random.randint(0,board.columns-1))
            tws.append(t)
        
        actions = []
        for i in range(k):
            actions += [(predict_score(board,a),a) for a in board.get_tower_actions(tws[i][0],tws[i][1])]
        
        if player > 0:
            heapq._heapify_max(actions)
        else:
            heapq.heapify(actions)

        board = board.play_action(actions[0][1])
    else:
        return board.get_score()
    return multiple_semi_greedy_simulation(-player, board)

def quick_e_greedy_simulation(player: int, board: 'Board', k: int=5, eps: float=0.4) -> float:
    """
    Inspired by the e-greedy policy in reinforcement learning.
    Randomly launch k multiple semi-greedy selection or one random action each turns.
    """
    if not board.is_finished():
        if random.random() < eps:
            tws = []
            for i in range(k):
                t = (random.randint(0,board.rows-1),random.randint(0,board.columns-1))
                while not board.is_tower_movable(t[0],t[1]):
                    t = (random.randint(0,board.rows-1),random.randint(0,board.columns-1))
                tws.append(t)
        
            actions = []
            for i in range(k):
                actions += [(predict_score(board,a),a) for a in board.get_tower_actions(tws[i][0],tws[i][1])]
        
            if player > 0:
                heapq._heapify_max(actions)
            else:
                heapq.heapify(actions)

            board = board.play_action(actions[0][1])
        else:
            t = (random.randint(0,board.rows-1),random.randint(0,board.columns-1))
            while not board.is_tower_movable(t[0],t[1]):
                t = (random.randint(0,board.rows-1),random.randint(0,board.columns-1))
            action = random.choice(list(board.get_tower_actions(t[0],t[1])))

            board = board.play_action(action)
    else:
        return board.get_score()
    return quick_e_greedy_simulation(-player, board)