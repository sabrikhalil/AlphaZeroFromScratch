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
        self.player: int = player
        self.successors: list[Node] = None
        self.parent: Node = parent
        self.action: tuple[int, int, int, int] = action
        self.undo: tuple[int, int] = undo
        self.depth: int = depth
        self.U: float = 0
        self.N: int = 0
        self.UCB: float = Q
        self.Q: float = Q
        self.used_C: float = used_C

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
    def selection(self, board: 'Board') -> 'Node':
        if self.successors is not None and len(self.successors) > 0:
            board = board.play_action(self.successors[0].action)
            return self.successors[0].selection(board)
        else:
            return self
    
    """
    Expand a node without any successors using the function in parameters.
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

    """
    Run a simulation on the given board using the function in parameters.
    """
    def simulation(self, simul_fun: Callable[[int,'Board'],float], board: Board) -> float:
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
        return select