from enum import StrEnum, auto

from src.model.grid import SudokuGrid
from src.solvers.first_fail_solver import FirstFailSudokuSolver
from src.solvers.naive_solver import NaiveSudokuSolver
from src.solvers.dancing_links_solver import DancingLinksSudokuSolver


class SudokuSolverType(StrEnum):
    """
    Type representing various solver types.

    Methods:
    --------
    solve(self, puzzle: SudokuGrid, time_limit: float) -> SudokuGrid:
        solves the given puzzle with a time limit
        uses a solver corresponding to the enum value
    """

    NAIVE = auto()
    FIRST_FAIL = auto()
    DANCING_LINKS = auto()

    def solve(self, puzzle: SudokuGrid, time_limit: float) -> SudokuGrid:
        match self:
            case SudokuSolverType.NAIVE:
                solver = NaiveSudokuSolver()
                return solver.solve(puzzle, time_limit)
            case SudokuSolverType.FIRST_FAIL:
                return FirstFailSudokuSolver.solve(puzzle, time_limit)
            case SudokuSolverType.DANCING_LINKS:
                return DancingLinksSudokuSolver.solve(puzzle, time_limit)
            case _:
                raise NotImplementedError()
