from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, Iterable, Iterator, Optional, Sequence, TypeVar
class StateBase(ABC):
    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError
    def __repr__(self) -> str:
        return str(self)
S = TypeVar("S", bound=GameState)
A = TypeVar("A")
class ProblemBase(ABC, Generic[S, A]):
    @abstractmethod
    def start(self) -> S:
        raise NotImplementedError
    @abstractmethod
    def actions(self, state: S) -> Iterable[A]:
        raise NotImplementedError
    @abstractmethod
    def apply(self, state: S, action: A) -> S:
        raise NotImplementedError
    @abstractmethod
    def is_goal(self, state: S) -> bool:
        raise NotImplementedError
@dataclass(frozen=True)
class Move:
    src: int
    dst: int
@dataclass(frozen=True)
class HanoiState(GameState):
    rods: Sequence[Sequence[int]]
    total: int
    def __str__(self) -> str:
        return f"Rods={self.rods}"
class HanoiGame(ProblemBase[HanoiState, Move]):
    def __init__(self, disks: int = 3):
        self.disks = disks
    def start(self) -> HanoiState:
        return HanoiState(rods=(tuple(range(self.disks, 0, -1)), (), ()), total=self.disks)
    def actions(self, state: HanoiState) -> Iterable[Move]:
        for i in range(3):
            if len(state.rods[i]) == 0:
                continue
            for j in range(3):
                if i == j:
                    continue
                yield Move(i, j)
    def apply(self, state: HanoiState, action: Move) -> HanoiState:
        src, dst = action.src, action.dst
        if len(state.rods[src]) == 0:
            raise ValueError("Source rod is empty")
        disk = state.rods[src][-1]
        if len(state.rods[dst]) > 0 and state.rods[dst][-1] < disk:
            raise ValueError("Illegal move: bigger on smaller")
        new_rods = [list(r) for r in state.rods]
        new_rods[src].pop()
        new_rods[dst].append(disk)
        return HanoiState(rods=tuple(tuple(r) for r in new_rods), total=state.total)
    def is_goal(self, state: HanoiState) -> bool:
        return len(state.rods[2]) == state.total
from collections import deque
import heapq
def dfs(problem: ProblemBase):
    stack = [(problem.start(), [])]
    visited = set()
    while stack:
        state, path = stack.pop()
        if problem.is_goal(state):
            return path
        if state in visited:
            continue
        visited.add(state)
        for action in problem.actions(state):
            next_state = problem.apply(state, action)
            stack.append((next_state, path + [action]))
def bfs(problem: ProblemBase):
    queue = deque([(problem.start(), [])])
    visited = set()
    while queue:
        state, path = queue.popleft()
        if problem.is_goal(state):
            return path
        if state in visited:
            continue
        visited.add(state)
        for action in problem.actions(state):
            next_state = problem.apply(state, action)
            queue.append((next_state, path + [action]))
def ids(problem: ProblemBase, max_depth=50):
    def dls(state, path, depth):
        if problem.is_goal(state):
            return path
        if depth == 0:
            return None
        for action in problem.actions(state):
            result = dls(problem.apply(state, action), path + [action], depth - 1)
            if result is not None:
                return result
        return None
    for depth in range(max_depth):
        result = dls(problem.start(), [], depth)
        if result is not None:
            return result
def ucs(problem: ProblemBase, cost_fn=lambda s, a: 1):
    pq = [(0, problem.start(), [])]
    visited = {}
    while pq:
        cost, state, path = heapq.heappop(pq)
        if problem.is_goal(state):
            return path
        if state in visited and visited[state] <= cost:
            continue
        visited[state] = cost
        for action in problem.actions(state):
            next_state = problem.apply(state, action)
            heapq.heappush(pq, (cost + cost_fn(state, action), next_state, path + [action]))
def greedy_best_first(problem: ProblemBase, heuristic):
    pq = [(heuristic(problem.start()), problem.start(), [])]
    visited = set()
    while pq:
        _, state, path = heapq.heappop(pq)
        if problem.is_goal(state):
            return path
        if state in visited:
            continue
        visited.add(state)
        for action in problem.actions(state):
            next_state = problem.apply(state, action)
            heapq.heappush(pq, (heuristic(next_state), next_state, path + [action]))
def astar(problem: ProblemBase, heuristic, cost_fn=lambda s, a: 1):
    pq = [(heuristic(problem.start()), 0, problem.start(), [])]
    visited = {}
    while pq:
        _, cost, state, path = heapq.heappop(pq)
        if problem.is_goal(state):
            return path
        if state in visited and visited[state] <= cost:
            continue
        visited[state] = cost
        for action in problem.actions(state):
            next_state = problem.apply(state, action)
            new_cost = cost + cost_fn(state, action)
            heapq.heappush(pq, (new_cost + heuristic(next_state), new_cost, next_state, path + [action]))
if __name__ == "__main__":
    game = HanoiGame(3)
    s0 = game.start()
    try:
        game.apply(s0, Move(1, 2))
        raise AssertionError("Expected ValueError for moving from empty rod.")
    except ValueError:
        pass
    bad_state = HanoiState(rods=((3,), (2, 1), ()), total=3)
    try:
        game.apply(bad_state, Move(0, 1))
        raise AssertionError("Expected ValueError for illegal placement.")
    except ValueError:
        pass
