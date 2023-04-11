#!/usr/bin/env python3
"""
Dummy random Avalam agent.
Copyright (C) 2022, Teaching team of the course INF8215 
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
import numpy as np 
from avalam import *
import math 
from Self_Play import *

import torch
import torch.nn as nn
import torch.nn.functional as F

torch.manual_seed(0)

from tqdm.notebook import trange

import random
import math

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def create_action_dictionary():
    action_dict = {}
    index = 0
    for row in range(9):
        for col in range(9):
            for drow in range(-1, 2):
                for dcol in range(-1, 2):
                    if drow == 0 and dcol == 0:
                        continue
                    action_dict[(row, col, row+drow, col+dcol)] = index
                    index += 1
    return action_dict

action_dict = create_action_dictionary()
index_to_action = {index: action for action, index in action_dict.items()}

class Self_Play_Agent(Agent ):


    """A dumb random agent."""
    def play(self, percepts, player, step, time_left):
        board = dict_to_board(percepts)
        actions = list(board.get_actions())
        print('step', step, 'player', player, 'actions', len(actions))

        # ## get model of resnet
        # encoded_board = board.get_encoded_state()

        # tensor_state = torch.tensor(encoded_board).unsqueeze(0).to(device)
        # model = ResNet(4,64, device)

        # policy, value = model(tensor_state)
        # value = value.item()
        # policy = torch.softmax(policy, axis=1).squeeze(0).detach().cpu().numpy()

        args = {
            "num_searches": 100, 
            "C": 1.24
        }

        model = ResNet(9, 128, device)
        model.load_state_dict(torch.load('model_0.pt', map_location=device))
        mcts = MCTS(model,args, device)
        ## Test MCTS 
        action_probs = mcts.search(board)

        best_action_index = np.argmax(action_probs)

        return index_to_action[best_action_index]

    




class MCTS() : 

    def __init__(self, model, args, device) :
        self.args = args
        self.model = model
 
        super().__init__()

    @torch.no_grad()
    def search(self, state):
        # define root 
        root = Node(self.args, state)  ## board and state mean same thing 

        for search in range(self.args["num_searches"]):
            ## Selection 
            node = root 

            while node.is_fully_expanded():
                node = node.select()

            value, is_terminal = -node.board.get_score(), node.board.is_finished()

          
            if not is_terminal: 

                policy, value = self.model(
                    torch.tensor(node.board.get_encoded_state()).unsqueeze(0).to(device)
                )
                policy = torch.softmax(policy, axis=1).squeeze(0).cpu().numpy()
                valid_moves = np.zeros_like(policy)
                for action_index in node.board.get_actions_indices():
                    valid_moves[action_index] = 1.0

                policy *= valid_moves 
                policy /= np.sum(policy)

                value = value.item()


                ## Expansion
                node = node.expand(policy)
                
            ## Backpropagation
            node.backpropagate(value)

        ## return visit counts 
        num_actions = len(index_to_action)
        action_probs = [0] * num_actions

        for child in root.children:
            action_probs[child.action_taken] = child.visit_count

        total_visit_count = sum(action_probs)
        action_probs = [prob / total_visit_count for prob in action_probs]
        return action_probs

class Node: 
    def __init__(self, args, board, parent=None, action_taken=None ,prior=0):
        self.args = args 
        self.board = board 
        self.parent = parent 
        self.action_taken = action_taken 
        self.prior = prior 

        self.children = []
        self.expandable_moves = list(board.get_actions_indices())

        self.visit_count = 0 
        self.value_sum = 0 


    def is_fully_expanded(self):
        return  len(self.children)>0 
    
    def select(self):
        best_child = None 
        best_ucb = -np.inf 

        for child in self.children : 
            ucb = self.get_ucb(child)
            if ucb > best_ucb :
                best_child = child 
                best_ucb = ucb 

        return best_child 
    
    def get_ucb(self, child):
        if child.visit_count == 0:
            q_value = 0
        else:
            q_value = 1 - ((child.value_sum / child.visit_count) + 1) / 2
        return q_value + self.args['C'] * (math.sqrt(self.visit_count) / (child.visit_count + 1)) * child.prior

    def expand(self, policy):

        for action_ind, prob in enumerate(policy):
            if prob >0 : 
                ## Store position of cells and their current height that will be impacted by the move , so we can undo the move 
                store_move = []
                action = index_to_action[action_ind]
                store_move.append((action[0] , action[1] , self.board.m[action[0]][action[1]])) 
                store_move.append((action[2] , action[3] , self.board.m[action[2]][action[3]]))

                ## play move 
                self.board.play_action(action)  

                ## change perspective 
                self.board.m = -1 * np.array(self.board.m)
                child_board = self.board.clone()
                child = Node(self.args, child_board, self, action_ind, prob)
                self.children.append(child)

                ## Undo the move is restoring the cells that were changed by their old state 
                self.board.m = -1 * self.board.m
                self.board.m[store_move[0][0]][store_move[0][1]] = store_move[0][2]
                self.board.m[store_move[1][0]][store_move[1][1]] = store_move[1][2]

            
        return child

    # def simulate(self):
    #     value, is_terminal = self.board.get_score(), self.board.is_finished()
    #     value = - value 
        
    #     if is_terminal:
    #         return value
        
    #     rollout_state = self.board.clone()
    #     rollout_player = 1
    #     while True:
    #         valid_actions = list(rollout_state.get_actions())
    #         action = random.choice(valid_actions)
    #         ## play action and go to next state
    #         rollout_state.play_action(action)   
    #         value, is_terminal = rollout_state.get_score(), rollout_state.is_finished()
    #         if is_terminal:
    #             if rollout_player == -1:
    #                 value = -value 
    #             return value    
            
    #         rollout_player = - rollout_player   # change player 

    def backpropagate(self, value):
        self.value_sum += value
        self.visit_count += 1
        
        value = - value 
        if self.parent is not None:
            self.parent.backpropagate(value)  


if __name__ == "__main__":
    agent_main(Self_Play_Agent())
