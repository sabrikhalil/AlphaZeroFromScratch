#!/usr/bin/env python3
"""
Avalam agent.
Copyright (C) 2023, KHALIL SABRI, HUGO BARRAL
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

from avalam import *


class MyAgent(Agent):

    """My Avalam agent."""

    def play(self, percepts, player, step, time_left ):
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
        print("percept:", percepts)
        print("player:", player)
        print("step:", step)
        print("time left:", time_left if time_left else '+inf')

        
        # TODO: implement your agent and return an action for the current step.
        board = dict_to_board(percepts)
        self.branches_open = 0 
        self.branches_closed_prunning = 0 

        self.printed = False 


        print('step', step, 'player', player)



        """ Ranking actions from importance , since Avalam has very high width , limiting the amount of actions to analyze is necessary for better performance 
            Here are the Heursitics Chosen :
                - If Move yield an isolated pawn : +5 points .
                - If Move result on tours with heigher weight : +Height of new tour -- The higher the height the higher the priority .
                - Penalty on puting your stone on another one of your own stone of : -2.5 points . 
        """

        def get_actions_ranked (board , limit_moves ,max_player): 
            """Yield all valid actions on this board."""
            
            scores = []
            actions = []

            towers = board.get_towers()
            towers_position = {(x,y) for x,y,z in towers}
            
            
            for i, j, h in board.get_towers():
                for action in board.get_tower_actions(i, j):
                    i1, j1, i2, j2 = action
                    h1 = abs(board.m[i1][j1])
                    h2 = abs(board.m[i2][j2])

                    score = 0 
                    visited = {}
                    
                    ###### Heuristic 1 for Isolate Pawns :
                    ## Store position of cells and their current height that will be impacted by the move , so we can undo the move 
                    store_move = []
                    store_move.append(( i1, j1 , board.m[i1][j1])) 
                    store_move.append(( i2, j2 , board.m[i2][j2]))

                    # play action on board
                    board.play_action(action) 

                    # check if move yielded isolated pawns (neighbors of (i,j)cell)
                    for i_ in range(i1-1 , i1+2, 1) :
                        for j_ in range(j1-1, j1+2 ,1) :
                            if (i_,j_) in towers_position : 
                                if not board.is_tower_movable(i_, j_) and board.m[i_][j_] != 0 and abs(board.m[i_][j_]) != 5 :
                                    visited[(i,j)] = True
                                    score += 5 * board.m[i_][j_] / abs(board.m[i_][j_] )    

                    
                    ## Undo the move is restoring the cells that were changed by their old state 
                    board.m[store_move[0][0]][store_move[0][1]] = store_move[0][2]
                    board.m[store_move[1][0]][store_move[1][1]] = store_move[1][2]
                    ########


                    ###### Heuristic 2 : If Move result on tours with heigher weight 
                    if board.m[i1][j1] < 0 and (i,j) not in visited: ## yellow on top
                        score += -(h1 + h2)
                    elif board.m[i1][j1] > 0 and (i,j) not in visited :
                        score += h1 + h2

                    ###### Heuristic 3: Moves where you put your own stone on top of another yours is generally weak
                    if  board.m[i1][j1] * board.m[i2][j2] >= 1 :
                        score -= 2.5 * board.m[i1][j1] / abs(board.m[i1][j1] )
                    


                    # store new score resulted from the action 
                    scores.append(score)
                    actions.append(action) 
            
            return [x for _, x in sorted(zip(scores, actions) ,reverse =  max_player)][:limit_moves] 

        

        """ Evaluation of Board -- Score :
                - Tour : 1.55 points
                - Isolated Pawns : 1.5 points 
                - Other Pawns : 
                    Isolated group of pawns with sum 5 :  1.55 points
                    Isolated group of pawns with sum <5 : 1.5 points 
                    Not belonging to an isolated group of pawns : 1 point
        """
        def score_board(board  ):
        
            score = 0
            visited = set()



            for i in range(board.rows):
                for j in range(board.columns):
                    
                    if board.m[i][j] == 0 :
                        pass
                    
                    ## assign 3 points to Tour 
                    elif board.m[i][j] in (-5,5) :
                        score += 1.55 * board.m[i][j] / abs(board.m[i][j] )

                    ## assign 3 points to isolated Powns 
                    elif not board.is_tower_movable(i, j):
                        score += 1.5 * board.m[i][j] / abs(board.m[i][j] )
                        
                    ## assign 1 point to the rest of the Pawns if not isolated group of pawns , otherwise assign the correct value as explained in the report 
                    else :
                        ## if already visited assign one point to that pawn 
                        if (i,j) in visited :
                            score += board.m[i][j] / abs(board.m[i][j] )
                        
                        ## if never visited , check the existence of isolated group of pawns 
                        else :
                            color = board.m[i][j] / abs(board.m[i][j] )
                            cycle = [(i,j)]
                            cycle_sum = 5 - abs(board.m[i][j])
                            same_color = True 
                            nodes_visited = -1 

                            
                            while ( cycle_sum >= 0 and cycle != [] and same_color ) :

                                current = cycle.pop()

                                 ## look neighbors 
                                for action in board.get_tower_actions(current[0] , current[1]):               
                                    i1, j1, i2, j2 = action
                                    ## if same color , continue 
                                    if board.m[i2][j2] / abs(board.m[i2][j2] ) != color :
                                        same_color = False 
                                        
                                    if current not in visited : 
                                        cycle.append((i2,j2))
                                        visited.add((i2,j2))
                                        cycle_sum -= abs(board.m[i2][j2])
                                
                                nodes_visited += 1 

                            ## if already more than 5 or color is changed , assign one point . 
                            if cycle != [] or same_color == False : 
                                score += board.m[i][j] / abs(board.m[i][j] ) 

                            ## if its one group isolated of pawns , assign 1.55 if their sum is 5 (equivalent to 1 Tour ) 
                            ## and 1.5 if their sum is less than 5 (Equivalent to isolated pawn)   
                            else : 
                                if cycle_sum == 5 : 
                                    score += 1.55 * color - nodes_visited * 1 * color 
                                else :
                                    score += 1.5 * color - nodes_visited * 1 * color 
                            
                        
            return score      


        """ 
            Implementation of Minimax using alpha beta pruning 
        """


        def minimax(board , depth , max_player , alpha , beta , limit_moves  ):

            self.branches_open += 1 

            if depth == 0 or board.is_finished(): 
                return score_board(board ), board , None  

            if max_player : 

                maxEval = float('-inf')
                actions = get_actions_ranked(board , limit_moves , max_player)
                actions  = list(actions)

                
                best_move = None
                
                for action  in actions:
  
                    ## Store position of cells and their current height that will be impacted by the move , so we can undo the move 
                    store_move = []
                    store_move.append((action[0] , action[1] , board.m[action[0]][action[1]])) 
                    store_move.append((action[2] , action[3] , board.m[action[2]][action[3]]))

                    board.play_action(action)            
                    evaluation = minimax(board, depth-1, False ,alpha , beta , limit_moves)[0]

                    ## Undo the move is restoring the cells that were changed by their old state 
                    board.m[store_move[0][0]][store_move[0][1]] = store_move[0][2]
                    board.m[store_move[1][0]][store_move[1][1]] = store_move[1][2]

                    

                    if evaluation > maxEval : 
                        
                        maxEval = evaluation 
                        best_move = action
                        
                    alpha = max(alpha , evaluation)

                    if beta <= alpha : 
                        break 


                                    
                return maxEval, board , best_move 


            else:
                minEval = float('inf')
                actions = get_actions_ranked(board , limit_moves , max_player)
                actions  = list(actions)



                best_move = None

                for action  in actions:

                    ## Store position of cells and their current height that will be impacted by the move , so we can undo the move 
                    store_move = []
                    store_move.append((action[0] , action[1] , board.m[action[0]][action[1]])) 
                    store_move.append((action[2] , action[3] , board.m[action[2]][action[3]]))

                    board.play_action(action)            
                    evaluation = minimax(board, depth-1, True ,alpha , beta , limit_moves)[0]

                    ## Undo the move is restoring the cells that were changed by their old state 
                    board.m[store_move[0][0]][store_move[0][1]] = store_move[0][2]
                    board.m[store_move[1][0]][store_move[1][1]] = store_move[1][2]



                    if evaluation < minEval : 
                        minEval = evaluation 
                        best_move = action
            
                    beta = min(beta , evaluation)
                    
                    if beta <= alpha : 
                        break 
                    

                
                return minEval, board , best_move
                
        
        ## Time management : If time left is less 135 , reduce depth to 6  (moves will be played in seconds)
        if time_left < 135 : 

            if player == 1 : 
                minimax_game =  minimax(board , 6 , True ,float('-inf'),float('inf') , limit_moves= 18)
            else : 
                minimax_game =  minimax(board , 6 , False ,float('-inf'),float('inf') , limit_moves= 18)

        ## Time management : If time left is less 350 , reduce depth to 7 (avoid depth 8 or more )
        elif time_left < 350 :
            if player == 1 : 
                minimax_game =  minimax(board , 7 , True ,float('-inf'),float('inf') , limit_moves= 18)
            else : 
                minimax_game =  minimax(board , 7 , False ,float('-inf'),float('inf') , limit_moves= 18)

        ## Depth starting at 5 and increased by one each 9 steps .
        else :
            if player == 1 : 
                minimax_game =  minimax(board , 5 + int(step / 9) , True ,float('-inf'),float('inf') , limit_moves= 18)
            else : 
                minimax_game =  minimax(board , 5 + int(step / 9) , False ,float('-inf'),float('inf') , limit_moves= 18)


        move , score = minimax_game[2],minimax_game[0]  

        print( "score : " + str(score))
        print("move chosen :" , move )

        

        return move      


if __name__ == "__main__":
    agent_main(MyAgent())


