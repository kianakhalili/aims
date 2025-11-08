from abc import ABC
from copy import deepcopy
class State(ABC):
    def __eq__(self, other):
        pass
    def __str__(self):
        pass
class Problem(ABC):
    def __init__(self, initial_state):
        self.initial_state = initial_state
    def goal_test(self, state):
        pass
    def successors(self, state):
        pass
class HanoiState(State):
    def __init__(self, pegs):
        self.pegs = pegs
    def __eq__(self, other):
        return self.pegs == other.pegs
    def __str__(self):
        return str(self.pegs)
    def copy(self):
        return HanoiState(deepcopy(self.pegs))
class TowerOfHanoi(Problem):
    def __init__(self, n_disks):
        initial_pegs = [list(range(n_disks, 0, -1)), [], []]
        super().__init__(HanoiState(initial_pegs))
        self.n_disks = n_disks
    def goal_test(self, state):
        return len(state.pegs[2]) == self.n_disks
    def successors(self, state):
        successors = []
        for from_peg in range(3):
            if not state.pegs[from_peg]:
                continue
            disk = state.pegs[from_peg][-1]  
            for to_peg in range(3):
                if from_peg != to_peg and (not state.pegs[to_peg] or state.pegs[to_peg][-1] > disk):
                    new_state = state.copy()
                    new_state.pegs[from_peg].pop()
                    new_state.pegs[to_peg].append(disk)
                    successors.append(new_state)
        return successors
    def generate_state_space(self, limit=100):
        visited = set()
        frontier = [self.initial_state]
        all_states = []
        while frontier and len(all_states) < limit:
            current = frontier.pop()
            state_str = str(current.pegs)
            if state_str in visited:
                continue
            visited.add(state_str)
            all_states.append(current)
            for s in self.successors(current):
                frontier.append(s)
        return all_states
