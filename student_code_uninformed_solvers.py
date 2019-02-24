
from solver import *
from queue import Queue
from copy import deepcopy

class SolverDFS(UninformedSolver):
    def __init__(self, gameMaster, victoryCondition):
        super().__init__(gameMaster, victoryCondition)

    def solveOneStep(self):
        """
        Go to the next state that has not been explored. If a
        game state leads to more than one unexplored game states,
        explore in the order implied by the GameMaster.getMovables()
        function.
        If all game states reachable from a parent state has been explored,
        the next explored state should conform to the specifications of
        the Depth-First Search algorithm.

        Returns:
            True if the desired solution state is reached, False otherwise
        """
        ### Student code goes here
        if self.currentState.state == self.victoryCondition:
            return True

        curr_moves = self.gm.getMovables()
        # while there are unexplored child states
        while self.currentState.nextChildToVisit < len(curr_moves):
            selected_move = curr_moves[self.currentState.nextChildToVisit]
            self.gm.makeMove(selected_move)
            # traverse deeper if new state is not visited
            new_state = GameState(self.gm.getGameState(), self.currentState.depth+1, selected_move)
            new_state.parent = self.currentState
            if new_state not in self.visited:
                # set next child to be traversed if solution is not found deeper
                self.currentState.nextChildToVisit += 1
                self.currentState = new_state
                # set this state to have been explored
                self.visited[self.currentState] = True
                return False
            else:
                # new state has been traversed, go back up
                self.gm.reverseMove(selected_move)
                self.currentState.nextChildToVisit += 1
        # all child states has been explored, traverse up
        self.gm.reverseMove(self.currentState.requiredMovable)
        self.currentState = self.currentState.parent
        return False

class SolverBFS(UninformedSolver):
    def __init__(self, gameMaster, victoryCondition):
        super().__init__(gameMaster, victoryCondition)
        # queue to implement bfs, keep track of starting point
        self.queue = Queue()
        self.start_gm = gameMaster
        # initiate queue, add the root node's children
        # note: each item in queue is a dict ({state, past_moves}) 
        self.enqueueChildren(self.currentState, [])

    def enqueueChildren(self, parent, past_moves):
        for new_move in self.gm.getMovables():
            self.gm.makeMove(new_move)
            new_state = GameState(self.gm.getGameState(), self.currentState.depth+1, new_move)
            new_state.parent = parent
            if new_state not in self.visited:
                self.queue.put({'state': new_state, 'past_moves': past_moves + [new_move]})
            self.gm.reverseMove(new_move)

    def solveOneStep(self):
        """
        Go to the next state that has not been explored. If a
        game state leads to more than one unexplored game states,
        explore in the order implied by the GameMaster.getMovables()
        function.
        If all game states reachable from a parent state has been explored,
        the next explored state should conform to the specifications of
        the Breadth-First Search algorithm.

        Returns:
            True if the desired solution state is reached, False otherwise
        """
        ### Student code goes here
        if self.currentState.state == self.victoryCondition:
            return True

        if self.queue.empty():
            return False

        # while not empty, pop a state and enqueue every unvisited child of that state
        while not self.queue.empty():
            item = self.queue.get()
            next_state = item['state']
            past_moves = item['past_moves']
            if next_state not in self.visited:
                break

        # check if visited and queue is empty, then done
        if next_state in self.visited and self.queue.empty():
            return False

        # deep copy to avoid modifying start point
        self.gm = deepcopy(self.start_gm)

        # navigate gm to next_state from queue
        for past_move in past_moves:
            self.gm.makeMove(past_move)

        self.visited[next_state] = True
        self.currentState = next_state
        
        self.enqueueChildren(next_state, past_moves)

        return False