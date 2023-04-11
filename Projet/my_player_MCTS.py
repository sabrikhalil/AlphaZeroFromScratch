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
import time
import gc
import math

from avalam import *

from monte_carlo_tree_search import Node
from successors import successors_with_tower_score
from simulation import quick_e_greedy_simulation
from heuristics import middle_game_wait

class MyAgent(Agent):
    def __init__(self) -> None:
        # The step number where we stop diminishing our allocated time
        self.step_threshold = 12
        self.node: Node = None
        self.board = None
        self.old_Q = 0
        super().__init__()

    """My Avalam agent."""
    def initialize(self, percepts, players, time_left):
        self.__init__()

    def play(self, percepts, player, step, time_left):
        """
        This function is used to play a move according
        to the percepts, player and time left provided as input.
        It must return an action representing the move the player
        will perform.
        :param percepts: dictionary representing the current board
            in a form that can be fed to `dict_to_board()` in avalam.py.
        :param player: the player to control in this step (-1 or 1)
        :param step: the current step number, starting from 1
        :param time_left: a float giving the number of seconds left from the time
            credit. If the game is not time-limited, time_left is None.
        :return: an action
            eg; (1, 4, 1 , 3) to move tower on cell (1,4) to cell (1,3)
        """
        # Keeping start time
        start = time.time()
        max_step = 0

        # First play or retrieve corresponding node
        if self.node is None or step <= 2:
            self.node = Node(player, None, None, None, step)
            self.board = Board(percepts=percepts['m'])
            self.old_Q = player
        else:
            found = False
            for n in self.node.successors:
                # Play the action associated to each successors until we find the one played by our opponent
                self.board.play_action(n.action)
                # If it's the right action, we update our current node
                if (self.board.m[n.action[0]][n.action[1]] == percepts['m'][n.action[0]][n.action[1]] and
                    self.board.m[n.action[2]][n.action[3]] == percepts['m'][n.action[2]][n.action[3]]):
                    self.node = n
                    self.node.parent = None
                    found = True
                    print("===== saved node =====")
                    break
                # Else we reverse the action to search another node 
                else:
                    self.board.m[n.action[0]][n.action[1]] = n.undo[0]
                    self.board.m[n.action[2]][n.action[3]] = n.undo[1]
            # If we didn't found it, we recreate a new node and board
            if not found:
                self.node = Node(player, None, None, None, step)
                self.board = Board(percepts=percepts['m'])
                self.old_Q = player
            gc.collect()

        # Calculating allocated time for this turn
        print("player",player,"\ntime left:",time_left)
        if not time_left:
            time_left = 1200
        else:
            # We diminish the allocated time in the first turn to have more during the mid game
            time_left = middle_game_wait(time_left,step,self.step_threshold)
        print("allocated time:",time_left)

        # Modify C parameter if falling behind in last selected node
        Node.update_C(math.exp(max(0,0.25-(self.old_Q/player))) * math.sqrt(2))
        print("C parameter:",Node.C)

        # MCTS algorithm
        while time.time() - start < time_left:
            # Create a copy of the board to play during selection and simulation
            dummy_board = self.board.clone()
            # Select a node based on our UCB formula
            select = self.node.selection(dummy_board)
            # If the node was player, we expand it and select one of the new ones
            if select.expansion(successors_with_tower_score, dummy_board):
                select = select.selection(dummy_board)
            # Start a simulation on the selected node and recover the score for backpropagation
            U = select.simulation(quick_e_greedy_simulation, dummy_board)
            select.backpropagation(U)
            # Update maximum reached depth
            if select.depth > max_step:
                max_step = select.depth
            # Deleting the copy
            del dummy_board

        # Best action selection
        new_node = self.node.best_action()

        # Saving selected action and clearing unused sub-trees
        self.node = new_node
        self.node.parent = None
        self.board = self.board.play_action(new_node.action)
        self.old_Q = new_node.Q
        gc.collect()

        # Returning action
        print("selected action",new_node.action,"with N, U, Q =",str(new_node.N)+",",str(new_node.U)+",",new_node.Q)
        print(step,"->",max_step)
        return new_node.action

    def hasEvolved(self):
        return False
    
if __name__ == "__main__":
    agent_main(MyAgent())

