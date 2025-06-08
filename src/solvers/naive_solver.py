from src.model.grid import SudokuGrid
from src.utils.recursion_limit import recursion_limit_set_to  # noqa
from timeit import default_timer as timer


class NaiveSudokuSolver:
    """
    A naive sudoku solver inspired by https://www.geeksforgeeks.org/sudoku-backtracking-7/.

    Attributes:
    -----------
    puzzle: SudokuGrid | None
        a currently solved puzzle, has value set only when called the `solve` method
    solution: SudokuGrid | None
        a current solution, has value set only after called the `solve` method
    deadline: float | None
        a current deadline, has value set only after called the `solve` method

    Methods:
    --------
    solve(puzzle: SudokuGrid, time_limit: float) -> SudokuGrid | None:
        solves the given sudoku puzzle within a specified time limit
    """

    puzzle: SudokuGrid | None
    solution: SudokuGrid | None
    deadline: float | None

    def solve(self, puzzle: SudokuGrid, time_limit: float) -> SudokuGrid | None:
        """
        Solves the given sudoku puzzle within a specified time limit.

        Parameters:
        -----------
        puzzle: SudokuGrid
            a sudoku puzzle to be solved
        time_limit: float
            amount of time (in seconds) available to the solver

        Returns:
        --------
        solution: SudokuGrid | None:
            - a sudoku solution if it has been found
            - `None` if the solution has not been found

        Raises:
        -------
        timeout_error: TimeoutError
            when the available time runs out
        """
        self.deadline = timer() + time_limit
        self.puzzle = puzzle
        self.solution = puzzle.copy()

        if self._dfs(0, 0):
            return self.solution
        return None

    def _timeout(self) -> bool:
        """
        Checks whether the available time has run out.

        Returns:
        --------
        timeout: bool
            - `True` if solver has missed the deadline
            - `False` otherwise
        """
        return timer() > self.deadline

    def _increment_coordinates(self, row: int, col: int) -> tuple[int, int]:
        """
        Increments the coordinates (moves to the next cell).

        Parameters:
        -----------
        row: int
            a row coordinate
        col: int
            a column coordinate

        Returns:
        --------
        next_coords: tuple[int,int]
            coordinates (row, col) of the next cell
        """
        # TODO:
        # Implement the method according to the docstring
        #
        # tip. first you increment the `col`, only when when you reach the end
        #      increment the row and reset col to 0
        if col >= self.solution.size - 1:
            # koniec wiersza -> następny wiersz, kolumna 0
            return row + 1, 0
        else:
            # kolejna kolumna w tym samym wierszu
            return row, col + 1

    def _is_excluded(self, row: int, col: int, val: int) -> bool:
        """
        Checks whether a given value can be put in the specified cell.

        Parameters:
        -----------
        row: int
            a row coordinate
        col: int
            a column coordinate
        val: int
            a value to be stored in the cell

        Returns:
        --------
        excluded: bool
            - `True` if the value can**not** be put in the cell
            - `False` otherwise
        """
        # TODO:
        # Implement the method according to the docstring
        #
        # tip 1. check if val is already in the row, col and block of the cell
        # tip 2. use array slicing to get row and column
        #        https://www.w3schools.com/python/numpy/numpy_array_slicing.asp
        # tip 2. use `self.solution.block_index` and `self.solution.block`
        #        to get the block
        size = self.solution.size

        # 1) Sprawdź wiersz
        if any(self.solution[row, j] == val for j in range(size)):
            return True

        # 2) Sprawdź kolumnę
        if any(self.solution[i, col] == val for i in range(size)):
            return True

        # 3) Sprawdź blok
        idx = self.solution.block_index(row, col)
        block_vals = self.solution.block(idx)
        # block_vals to tablica 2D; iterujemy po wartościach
        if any(x == val for row_vals in block_vals for x in row_vals):
            return True

        return False

    def _dfs(self, row: int, col: int) -> bool:
        """
        Performs a depth-first-search to solve the sudoku puzzle.
        Basically, it tries to put any acceptable value at the current cell
        and then moves to the next cell recursively.

        It may happen that it is impossible to find any
        acceptable value for the given cell.
        In such a case we check other values for the **previous**
        cells. This is called backtracking.

        - https://en.wikipedia.org/wiki/Backtracking
        - https://www.geeksforgeeks.org/introduction-to-backtracking-2/

        Parameters:
        -----------
        row: int
            row coordinate of the currently considered cell
        col: int
            column coordinate of the currently considered cell

        Returns:
        --------
        solved: bool
            `True` - if method found the soluton
            `False` - otherwise
        """
        # TODO:
        # Implement the method according to the docstring
        #
        # - if `row` is outside the grid, we have explored all the cells
        #   it means, we have solved the puzzle!
        # - if the time has run out (`self._timeout` method)
        #   raise the TimeoutError
        # - if the value of the current cell in the original puzzle is not 0
        #   it means, we don't have to do anything with the cell
        #   just increment the coordinates (`self._increment_coordinates`)
        #   and call _dfs recursively
        # - otherwise we have to loop over all the possible sudoku values:
        #   * ignore values that are already excluded (`self._is_excluded`)
        #   * put value in the current cell
        #   * run recursively _dfs on the next cell
        #       - if the recursive call returns True, we have solved the puzzle!
        #       - otherwise we reset value of the current cell to 0
        # - if we finish the loop without success, the puzzle is infeasible
        #   so we should return `False`
        size = self.solution.size
        # Jeśli skończyliśmy przeszukiwać ostatni wiersz, rozwiązano zagadkę
        if row >= size:
            return True
        # Sprawdź limit czasu
        if self._timeout():
            raise TimeoutError("Solver time limit exceeded")
        # Jeśli komórka była zapełniona oryginalnie, pomiń ją
        if self.puzzle._array[row, col] != 0:
            nxt_row, nxt_col = self._increment_coordinates(row, col)
            return self._dfs(nxt_row, nxt_col)
        # W przeciwnym razie spróbuj wstawić do komórki wszystkie wartości od 1 do size
        for val in range(1, size + 1):
            if not self._is_excluded(row, col, val):
                self.solution[row, col] = val
                nxt_row, nxt_col = self._increment_coordinates(row, col)
                if self._dfs(nxt_row, nxt_col):
                    return True
                # Cofnij ruch
                self.solution[row, col] = 0
        # Jeśli żadna wartość nie działa, to puzzle jest niespełnialny na tej ścieżce
        return False
