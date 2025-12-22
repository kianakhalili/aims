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
