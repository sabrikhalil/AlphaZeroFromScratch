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

from typing import Callable
import math
import heapq

from avalam import *

"""
Node representing the state of the game.
Used to construct Monte-Carlo Trees.
"""
class Node():

<<<<<<< Updated upstream
    C = math.sqrt(2)

    def __init__(self, player: int, parent: 'Node', action: 'tuple[int, int, int, int]', undo: 'tuple[int, int]', depth: int, UCB: float = 0) -> None:
=======
    """
    Global C exploration parameter.
    Base value of sqrt(2).
    """
    C = math.sqrt(2)

    """
    Static method to modify the C parameter.
    """
    @staticmethod
    def update_C(C:float) -> None:
        Node.C = C

    """
    Init a new node
    - player : the player during this node turn
    - parent : the node from which it's the successor
    - action : the action played to reach this node
    - undo : the coordinates values before the action
    - depth : the node's depth
    - Q : a base Q value pre-evaluated
    - used_C : the C value used to create the Q value
    """
    def __init__(self, player: int, parent: 'Node'=None, action: 'tuple[int, int, int, int]'=None,
                undo: 'tuple[int, int]' = None, depth: int = 0, Q: float = 0, used_C: float = 0) -> None:
>>>>>>> Stashed changes
        self.player: int = player
        self.successors: list[Node] = None
        self.parent: Node = parent
        self.action: tuple[int, int, int, int] = action
        self.undo: tuple[int, int] = undo
        self.depth: int = depth
        self.U = 0
        self.N: int = 0
<<<<<<< Updated upstream
        self.UCB: float = UCB
=======
        self.UCB: float = Q
        self.Q: float = Q
        self.used_C: float = used_C
>>>>>>> Stashed changes

    """
    We use UCB to differenciate and order our nodes.
    """
    def __eq__(self, __o: 'Node') -> bool:
        return self.UCB == __o.UCB

    def __lt__(self,  __o: 'Node') -> bool:
        return self.UCB < __o.UCB

    def __hash__(self) -> int:
        return hash(self.UCB)

    def __repr__(self) -> str:
        return str(self.UCB)

    def __str__(self) -> str:
        return str(self.UCB)

    """
    The modified UCB1 formula.
    We take into account the player wich will select the node and if the node was never played into account.
    """
    def compute_UCB1(self) -> None:
        if self.N != 0:
<<<<<<< Updated upstream
            self.UCB = self.U/self.N + self.parent.player * Node.C * math.sqrt(math.log(self.parent.N)/self.N)

=======
            self.Q = self.U/self.N
            self.UCB = self.Q + self.parent.player * Node.C * math.sqrt(math.log(self.parent.N)/self.N)
        elif self.used_C != 0 and Node.C != self.parent.player * self.used_C:
            self.UCB = self.Q - self.used_C + self.parent.player * Node.C
            self.used_C = self.parent.player * Node.C

    """
    Select nodes recursively until we found one without successors.
    Player 1 nodes select a successor with the highest UCB value.
    Player -1 nodes select a successor with the lowest UCB value.
    """
>>>>>>> Stashed changes
    def selection(self, board: 'Board') -> 'Node':
        if self.successors is not None and len(self.successors) > 0:
            board = board.play_action(self.successors[0].action)
            return self.successors[0].selection(board)
        else:
            return self
    
    """
    Expend a node without any successors using the function in parameters.
    Order its successors depending on the current player.
    """
    def expansion(self, get_successors: Callable[['Node', 'Board'],'list[Node]'], board: Board) -> bool:
        if (self.successors is None or len(self.successors) > 0) and self.N > 0:
            self.successors = get_successors(self, board)
            if self.player > 0:
                heapq._heapify_max(self.successors)
            else:
                heapq.heapify(self.successors)
            return True
        return False

<<<<<<< Updated upstream
    def simulation(self, simul_fun: Callable[[int],int], board: Board) -> float:
=======
    """
    Run a simulation on the given board using the function in parameters.
    """
    def simulation(self, simul_fun: Callable[[int,'Board'],float], board: Board) -> float:
>>>>>>> Stashed changes
        return simul_fun(self.player, board)

    """
    Backpropagate the given value and recalculate the UCB of the successors.
    """
    def backpropagation(self, add: float) -> None:
        self.U += add
        self.N += 1
        if not self.parent is None:
            self.parent.backpropagation(add)
        if not self.successors is None:
            for i in range(len(self.successors)):
                self.successors[i].compute_UCB1()
            if self.player > 0:
                heapq._heapify_max(self.successors)
            else:
                heapq.heapify(self.successors)
    
    """
    Select the best action based on Max-Robust child criterion.
    """
    def best_action(self) -> 'Node':
        select = Node(None,0,None,None,0,0)
        if not self.successors is None:
            for n in self.successors:
                if n.N > select.N:
                    select = n
<<<<<<< Updated upstream
        return select

def is_positive(x):
    if x > 0:
        return 1
    else:
        return -1

def all_successors(current: Node, board: 'Board') -> 'list[Node]':
    actions = board.get_actions()
    successors = []
    for a in actions:
        undo = (board.m[a[0]][a[1]],board.m[a[2]][a[3]])
        successors.append(Node(-current.player,current,a,undo,current.depth+1))
    return successors

def successors_with_relative_score(current: Node, board: 'Board') -> 'list[Node]':
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
    dumb_filter = (current.depth < 8)

    actions = board.get_actions()
    successors = []
    for a in actions:
        if dumb_filter and is_positive(board.m[a[2]][a[3]]) == current.player:
            continue
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

        successors.append(Node(-current.player,current,a,undo,current.depth+1,score))

        board.m[a[0]][a[1]] = undo[0]
        board.m[a[2]][a[3]] = undo[1]
            
    return successors

def get_neighbours(i: int, j: int, board: Board) -> 'list[int]':
    return [board.m[a[2]][a[3]] for a in board.get_tower_actions(i,j)]


def random_simulation(player: int, board: 'Board') -> int:
    if not board.is_finished():
        actions = list(board.get_actions())
        select = random.choice(actions)
        board = board.play_action(select)
    else:
        return board.get_score()
    return random_simulation(-player, board)


def quick_random_simulation(player: int, board: 'Board') -> int:
    if not board.is_finished():
        t = (random.randint(0,board.rows-1),random.randint(0,board.columns-1))
        while not board.is_tower_movable(t[0],t[1]):
            t = (random.randint(0,board.rows-1),random.randint(0,board.columns-1))        
        action = random.choice(list(board.get_tower_actions(t[0],t[1])))

        board = board.play_action(action)
    else:
        return board.get_score()
    return quick_random_simulation(-player, board)

def predict_score(board: Board, action: 'tuple[int, int, int, int]') -> int:
    undo = (board.m[action[0]][action[1]],board.m[action[2]][action[3]])
    board.play_action(action)


    v = board.m[action[2]][action[3]]
    sign = is_positive(v)
    sign_undo = is_positive(undo[1])

    penality = 1
    if sign == sign_undo:
        penality = -1

    score = 0
    if abs(board.m[action[2]][action[3]]) == 5:
        score = 1.5 * sign
    elif not board.is_tower_movable(action[2],action[3]):
        score = 1.25 * sign
    else:
        # capture = 0
        # others = [(a[2],a[3]) for a in board.get_tower_actions(action[2],action[3])]
        # for o in others:
        #     if is_positive(board.m[o[0]][o[1]]) != sign:
        #         capture = 1
        #         break
        # if capture == 0:
        #     score = 0.75 * sign * penality
        # else:
        #     score = 0.25 * sign * penality
        score = sign * penality

    board.m[action[0]][action[1]] = undo[0]
    board.m[action[2]][action[3]] = undo[1]

    return score

def quick_random_greedy_simulation(player: int, board: 'Board') -> int:
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
    return quick_random_greedy_simulation(-player, board)

k = 10
eps = 0.65

def multiple_quick_random_greedy_simulation(player: int, board: 'Board') -> int:
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
    return multiple_quick_random_greedy_simulation(-player, board)

def quick_e_greedy_simulation(player: int, board: 'Board') -> int:
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
=======
        return select
>>>>>>> Stashed changes
