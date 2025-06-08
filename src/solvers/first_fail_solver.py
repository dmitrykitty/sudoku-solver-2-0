from __future__ import annotations
from dataclasses import dataclass
from typing import NewType
from src.solvers.solver import SudokuSolver
from src.model.grid import SudokuGrid
from src.utils.recursion_limit import recursion_limit_set_to  # noqa

Variable = NewType("Variable", tuple[int, int, int])
"""Type representing a single variable identifier, it's a tuple with
   the variable's coordinates (row index, col index, block index)"""

Domain = NewType("Domain", set[int])
"""Type representing set of of available values"""


@dataclass(frozen=True, slots=True)
class State:
    """
    Represent the current state of the backtracking solver.

    Attributes:
    -----------
    grid: SudokuGrid
        a current state of the grid
    free_variables: set[Variable]
        set of the variables without assigned values
    row_domains: list[Domain]
        set of values available in the given row, e.g.
            row_domains[5] = {1,2,3,4}
        means the {1,2,3,4} can be assigned in row 5
    col_domains: list[Domain]
        set of values available in the given column
    block_domains: list[Domain]
        set of values available in the given block
    """

    grid: SudokuGrid
    free_variables: set[Variable]
    row_domains: list[Domain]
    col_domains: list[Domain]
    block_domains: list[Domain]

    def domain(self, variable: Variable) -> Domain:
        """
        Return domain (available values) for the given variable.

        Parameters:
        -----------
        variable: Variable
            a variable whose domain we want to get


        Return:
        --------
        domain: Domain
            values available for the given domain
        """

        # TODO:
        # Implement the method as described in the docstring.
        #
        # tip 1. read Variable type documentation
        # tip 2. use self.row_domains, self.col_domains, self.block_domains
        # tip 3. docs: https://docs.python.org/3.13/library/stdtypes.html#set.intersection
        row, col, block = variable

        return Domain(
            self.row_domains[row] & self.col_domains[col] & self.block_domains[block]
        )

    def assign(self, variable: Variable, value: int) -> None:
        """
        Assigns a given value to a given variable.

        Parameters:
        -----------
        variable: Variable
            variable to be assigned to
        value: int
            what value should we assign
        """
        # TODO:
        # Update the state according to the docstring
        # tip. you need to modify:
        #   - self.grid
        #   - self.free_variables
        #   - self.row_domains
        #   - self.col_domains
        #   - self.block_domains
        row, col, block = variable
        # assign value in the grid
        self.grid[row, col] = value
        # variable is no longer free
        self.free_variables.discard(variable)

        self.row_domains[row].discard(value)
        self.col_domains[col].discard(value)
        self.block_domains[block].discard(value)

    def remove_assignment(self, variable: Variable) -> None:
        """
        Removes a value assignment.

        Parameters:
        -----------
        variable: Variable
            an already assigned variable
        """
        # TODO:
        # Update the state according to the docstring.
        # tip 1. you need to modify:
        #   - self.grid
        #   - self.free_variables
        #   - self.row_domains
        #   - self.col_domains
        #   - self.block_domains
        #
        # tip 2. grid contains the current value
        row, col, block = variable
        # current value stored in the grid
        value = int(self.grid[row, col])
        # remove value from grid
        self.grid[row, col] = 0
        # mark variable as free again
        self.free_variables.add(variable)
        # restore domains
        self.row_domains[row].add(value)
        self.col_domains[col].add(value)
        self.block_domains[block].add(value)

    @staticmethod
    def from_grid(grid: SudokuGrid) -> State:
        """
        Creates an initial state for a given grid.

        Parameters:
        -----------
        grid: SudokuGrid
            an initial state of the sudoku grid

        Return:
        --------
        state: State
            a state matching the grid
        """
        # TODO:
        # Create an initial state as stated in the docstring
        #
        # tips.
        # - to enumerate over the grid use:
        #   `for (row, col), val in grid.enumerate():`
        size = grid.size
        copy_grid = grid.copy()
        all_values = set(range(1, size + 1))
        row_domains = [set(all_values) for _ in range(size)]
        col_domains = [set(all_values) for _ in range(size)]
        block_domains = [set(all_values) for _ in range(size)]

        free_vars: set[Variable] = set()
        for (row, col), val in copy_grid.enumerate():
            block = copy_grid.block_index(row, col)
            if int(val) == 0:
                free_vars.add(Variable((row, col, block)))
            else:
                row_domains[row].discard(int(val))
                col_domains[col].discard(int(val))
                block_domains[block].discard(int(val))

        return State(
            copy_grid,
            free_vars,
            [Domain(d) for d in row_domains],
            [Domain(d) for d in col_domains],
            [Domain(d) for d in block_domains],
        )


class FirstFailSudokuSolver(SudokuSolver):
    """
    A first-fail backtracking sudoku solver.
    It first tries to fill cells with smallest number of available values.
    """

    state: State

    def __init__(self, puzzle, time_limit):
        super().__init__(puzzle, time_limit)
        self.state = State.from_grid(puzzle)

    def run_algorithm(self) -> SudokuGrid | None:
        with recursion_limit_set_to(self._puzzle.size**3):
            if self._dfs():
                return self.state.grid
            return None

    def _dfs(self) -> bool:
        """
        Performs a first-fail depth-first-search to solve the sudoku puzzle.
        It always chooses a variable with the smallest domain and tries it first.

        Return:
        --------
        solved: bool
            `True` - if method found the solution
            `False` - otherwise
        """

        # TODO:
        # Implement the search.
        # 1. choose a free variable using `self._choose_variable`
        #   - if there is None, the solver has succeeded
        # 2. if there is a timeout, raise an appropriate exception
        # 3. try to assign a value to the variable and run the method recursively
        #   - take a value from the variable's domain
        #   - use self.state.assign to assign a value
        #   - use self.state.remove_assignment to revert the assignment
        # 4. return `False` if the solution has not been found
        var_dom = self._choose_variable()
        # if there is no variable left, puzzle solved
        if var_dom is None:
            return True

        if self._timeout():
            raise TimeoutError

        variable, domain = var_dom
        for value in domain:
            self.state.assign(variable, value)
            if self._dfs():
                return True
            self.state.remove_assignment(variable)

        return False

    def _choose_variable(self) -> tuple[Variable, Domain] | None:
        """
        Finds a free variable with the smallest domain.

        Return:
        --------
        var_dom: tuple[Variable, Domain] | None:
            if there are no free variables left,returns `None`
            otherwise returns a variable with the smallest domain (together with its domain)
        """
        # TODO:
        # Implement the method according to the docstring.
        # Useful stuff:
        # - self.state.free_variables
        # - self.state.domain
        # - https://docs.python.org/3/library/functions.html#min
        if not self.state.free_variables:
            return None

        def dom_size(var: Variable) -> int:
            return len(self.state.domain(var))

        variable = min(self.state.free_variables, key=dom_size)
        return variable, self.state.domain(variable)
