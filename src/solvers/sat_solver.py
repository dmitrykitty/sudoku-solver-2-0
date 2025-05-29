from __future__ import annotations
from dataclasses import dataclass
import itertools
from threading import Timer
from typing import Iterable
from src.solvers.solver import SudokuSolver
from src.model.grid import SudokuGrid
from pysat.formula import CNF  # type: ignore[import-untyped]
from pysat.solvers import Solver  # type: ignore[import-untyped]
from src.utils.group_by import group_by


@dataclass(frozen=True)
class Coordinates:
    """
    Represent coordinates of a sudoku variable (empty cell).
    """

    row: int
    col: int
    block: int


@dataclass(frozen=True)
class Proposition:
    """
    A single proposition:
    "Sudoku cell at coordinates: `coords` has value `val`"
    """

    coords: Coordinates
    val: int
    id: int


@dataclass
class SudokuCNF:
    """
    Represents a sudoku puzzle using a `Conjunctive Normal Form`:
    - https://en.wikipedia.org/wiki/Conjunctive_normal_form
    - https://equaeghe.github.io/ecyglpki/cnfsat.html

    Usage
    -----
    Given a sudoku `grid: SudokuGrid` one should use static method `encode`
    to create a CNF representation:

        `sudoku_cnf = SudokuCNF.encode(grid)`

    To pass the representation into a SAT solver, one should use the `cnf` property:

        `with Solver(bootstrap_with=sudoku_cnf.cnf) as solver`

    Given a solution from a SAT solver (e.g. `solution = solver.get_model()`)
    one can translate it to a SudokuGrid via the `decode` method:

        `solution_grid =  sudoku_cnf.decode()`

    """

    cnf: CNF
    """a `Conjunctive Normal Form` encoding as used by a SAT solver"""
    propositions: dict[int, Proposition]
    """mapping from propositions identifiers (as used in the CNF)
       to the propositions themselves"""
    puzzle: SudokuGrid
    """a puzzle encoded in the CNF"""

    def __post_init__(self) -> None:
        # TODO:
        # Fill `self.cnf` with correct clauses.
        # tip. just call `self._every_*` methods :)
        raise NotImplementedError("not implemented yet")

    def _at_least_one(self, propositions: Iterable[Proposition]) -> None:
        # TODO:
        # Add to `self.cnf` a clause saying that at least one
        # of the passed propositions has to be true.
        #
        # tip 1. clause is represented as a list, e.g.,
        #   `[1, 3, 5]` means `1 or 3 or 5`, where `1`, `3`, `5`
        #   are identifiers of the propositions
        # tip 2. `self.cnf` has an append method:
        #   https://pysathq.github.io/docs/html/api/formula.html#pysat.formula.CNF
        # tip 3. given propositions `p`, `q`,` s` you just want to add a clause:
        #   `p or q or s`
        raise NotImplementedError("not implemented yet")

    def _at_most_one(self, propositions: Iterable[Proposition]) -> None:
        # TODO:
        # Add to `self.cnf` clauses saying that at most one
        # of the passed propositions has to be true.
        #
        # tip 1. read tips from `_at_least_one`
        # tip 2. if `1` is identifier of proposition `p`, then
        #   `-1` represents `~p` (not `p`).
        # tip 3. given propositions `p`, `q`,` s` you want to add following clauses
        #   ~p or ~q
        #   ~p or ~s
        #   ~s or ~q
        #   This way only one proposition can be true. For example, if `p` is true
        #   then ~q and ~s also have to be true.
        raise NotImplementedError("not implemented yet")

    def _exactly_one(self, propositions: Iterable[Proposition]) -> None:
        # TODO:
        # Add to `self.cnf` clauses saying that exactly one of the passed
        # proposition is true.
        #
        # tip. you can use other already implemented methods :)
        raise NotImplementedError("not implemented yet")

    def _every_cell_has_a_single_value(self):
        # This method is implemented to show the idea, how the encoding works.
        # It modifies the `self.cnf`, so each sudoku cell holds exactly one value.
        #
        # First, it uses `group_by` method from `src.utils.group_by` (already imported)
        #   to group `self.propositions` into propositions for each cell.
        #   In other words, `cell_propositions` hold propositions:
        #       `cell at coords C has value 1`
        #       `cell at coords C has value 2`
        #       `cell at coords C has value 3`
        #       ...
        # Then it uses `self._exactly_one` to modify the CNF.
        # Now every empty cell has to have a single assigned value.
        for cell_propositions in group_by(
            self.propositions.values(), lambda p: p.coords
        ).values():
            self._exactly_one(cell_propositions)

    def _every_row_contains_unique_values(self):
        # TODO:
        # Modify `self.cnf`, so each sudoku row holds every value **at most once**.
        #
        # tip 1. read comment in `_every_cell_has_a_single_value`
        # tip 2. group propostion by `row` and `val`
        #   We want to have propositions for each row R and value V:
        #       `cell at coord R,0 has value V`
        #       `cell at coords R,1, has value V`
        #       `cell at coords R,2 has value V`
        #       ...
        #   And **at most one** of them can be true.
        raise NotImplementedError("not implemented yet")

    def _every_col_contains_unique_values(self):
        # TODO:
        # Modify `self.cnf`, so each sudoku column holds every value **at most once**.
        #
        # tip 1. read comment in `_every_cell_has_a_single_value`
        #        just replace rows with columns
        raise NotImplementedError("not implemented yet")

    def _every_block_contains_unique_values(self):
        # TODO:
        # Modify `self.cnf`, so each sudoku column holds every value **at most once**.
        #
        # tip 1. read comment in `_every_cell_has_a_single_value`
        #        just replace rows with blocks
        raise NotImplementedError("not implemented yet")

    @staticmethod
    def encode(puzzle: SudokuGrid) -> SudokuCNF:
        """
        Encodes a given sudoku puzzle into its Conjunctive Normal Form
        suitable for SAT solvers.

        Parameters
        ----------
        puzzle: SudokuGrid
            a sudoku puzzle to be encoded

        Returns
        -------
        encoding: SudokuCNF
            Conjunctive Normal Form encoding of the specified puzzle
        """
        cnf = CNF()
        propositions = SudokuCNF._possible_propositions(puzzle)
        return SudokuCNF(cnf, propositions, puzzle)

    def decode(self, results: list[int]) -> SudokuGrid:
        """
        Decodes a SAT solution into a filled sudoku grid.

        Parameters
        ----------
        results: list[int]
            list of true propositions (their identifiers, to be exact)
            [1,-2,3,-4,5] would mean, that propositions 1,3,5 are true
            and 2 and 5 are false.

        Returns
        -------
        solution: SudokuGrid
            a sudoku grid filled according the SAT results
        """
        # TODO:
        # Implement the method according to the docstring.
        # 1. remember to copy `self.puzzle`
        # 2. for every **true** proposition in the results
        #    assign a corresponding value at the corresponding coordinates
        #    in the puzzle copy
        # 3. return the filled grid
        raise NotImplementedError("not implemented yet")

    @staticmethod
    def _possible_propositions(puzzle: SudokuGrid) -> dict[int, Proposition]:
        # TODO:
        # This method should return all the valid propositions
        # in the sudoku puzzle.
        #
        # Every proposition is of type Proposition
        # and has a given semantics:
        #   cell at coordinates {coords} has value {value}.
        #
        # The propositions are to be returned as a dictionary:
        # ```
        # {
        #   id_1 : proposition_with_id_1,
        #   id_2 : proposition_with_id_2,
        #   ...
        # }
        # ```
        #
        # The proposition identifier are supposed to be consecutive integer numbers: 1, 2, 3, ...
        # For example, a result could look like:
        #
        # ```
        # {
        #   1: Proposition(coords=Coordinates(0,0,0), val=0, id=1),
        #   2: Proposition(coords=Coordinates(0,0,0), val=1, id=2)
        # }
        # ```
        #
        # tip 1. we create propositions only for **valid** value assignments:
        #    you may want to look at your code `State.from_grid` in `first_fail_solver.py`
        #    to look how to calculate cells' valid values.
        raise NotImplementedError("not implemented yet")


class SatSudokuSolver(SudokuSolver):
    """
    A SAT-based sudoku solver using the python-sat library:
    - what is a SAT-solver: https://en.wikipedia.org/wiki/SAT_solver

    - python-sat basic usage: https://pysathq.github.io/usage/
      look especially at an example starting with `formula = CNF()`

    - python-sat docs: https://pysathq.github.io/docs/html/index.html#supplementary-examples-package
    """

    def __init__(self, puzzle, time_limit):
        super().__init__(puzzle, time_limit)

    def run_algorithm(self) -> SudokuGrid | None:
        # TODO:
        # Use python-sat to solve to sudoku!
        #
        # General tip: read SudokuCNF documentation at the top of this file
        #
        # 1. encode `self._puzzle` into a CNF
        #    via `SudokuCNF.encode`
        # 2. build solver via context manager
        #    - a basic example is shown here:
        #       https://pysathq.github.io/docs/html/api/solvers.html#pysat.solvers.Solver.accum_stats
        #    - `cnf` is a property of the SudokuCNF you have already built
        #    - we don't need the `accum_stats()`
        # 3. handle timeout as stated here:
        #    - https://pysathq.github.io/docs/html/api/solvers.html#pysat.solvers.Solver.interrupt
        #    - in other words:
        #       * use solve_limited expecting an interrupt
        #       * run Timer with self._timelimit to interrupt the solver
        #       * the example on the page is missing a single line.
        #         After solver finds a solution one should cancel the timer via `timer.cancel()`.
        #         Otherwise the timer will interrupt the already finished solver.
        # 4. `solve_limited` returns status:
        #   - `None` means there was an interruption/timeout
        #      * we should raise a TimeoutError
        #   - `False` means the solver failed to find a solution
        #      * we should also return `None`
        #   - `True` means the solver found a solution
        #      * we should return "decoded" solution.
        #        * use `decode` method of the SudokuCNF object.
        #        * `solver.get_model()` returns the solution, 
        #           a list of true propositions
        raise NotImplementedError("not implemented yet")
