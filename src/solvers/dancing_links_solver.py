from ctypes import CDLL, c_int, Array
from multiprocessing import Queue, Process  # noqa
from pathlib import Path

import numpy as np  # noqa§
from src.solvers.solver import SudokuSolver
from src.model.grid import SudokuGrid


class DancingLinksSudokuSolver(SudokuSolver):
    """
    This solver uses the famous Knuth's Algorithm X.
    We will outsource work to the existing implementation in C:
        https://github.com/nstagman/exact_cover_sudoku
    """

    def run_algorithm(self) -> SudokuGrid | None:
        # TODO:
        # This method will run the C program in a separate process.
        # The new process will communicate with as via a queue.
        # The basic example is shown in documentation:
        # - https://docs.python.org/3/library/multiprocessing.html#exchanging-objects-between-processes
        #
        # 1. create a queue
        # 2. create a process with:
        # - target set to `self._communicate_with_external_solver`
        # - args containing only the queue
        # 3. start the process
        # 4. get the result from the queue:
        # - https://docs.python.org/3/library/queue.html#queue.Queue.get
        # - set timeout to `self._time_limit`
        # 5. the get method can raise an exception, if that happens
        # - check if the process is still alive:
        #   https://docs.python.org/3/library/multiprocessing.html#multiprocessing.Process.is_alive
        # - if it is, terminate it:
        #   https://docs.python.org/3/library/multiprocessing.html#multiprocessing.Process.terminate
        # - raise the TimeoutError
        queue: Queue = Queue()
        proc = Process(target=self._communicate_with_external_solver, args=(queue,))
        proc.start()
        try:
            result = queue.get(timeout=self._time_limit)
        except Exception:
            if proc.is_alive():
                proc.terminate()
            raise TimeoutError
        finally:
            proc.join()

        return result

    def _communicate_with_external_solver(self, queue: Queue) -> None:
        """
        Calls the external solver and returns result via the queue.

        Parameters:
        -----------
        queue: Queue
            queue used to return the result
        """

        # TODO:
        # 1. run the algorithm via `self._run_algorithm`
        # 2. return its result via queue:
        # - https://docs.python.org/3/library/queue.html#queue.Queue.put_nowait
        # 3. if there is an exception, return `None` via the queue
        try:
            res = self._run_algorithm()
            queue.put_nowait(res)
        except Exception:
            queue.put_nowait(None)

    def _get_lib(self) -> CDLL:
        """
        Loads the library containing the solver.

        Return:
        --------
        library: CDLL
            a library containing the algorithm implementation
        """

        # TODO:
        # You don't have to write any code here, but you create the library
        # and put in at the `lib/ss.so` path.
        #
        # How to build the library:
        # - download code from https://github.com/nstagman/exact_cover_sudoku
        # - open the `c` directory
        # - modify the `sudoku_solve.c` file by adding
        #   `#include <Python.h>` somewhere at the top
        #   it is required by the file to be easily called from Python
        # - modify the `makefile`:
        #   0. change EXE to `ss.so`
        #   1. remove two lines starting with `run: $(EXE)`.
        #      we won't run the code directly
        #   2. add `-fPIC -shared` to CFLAGS, so the code would compile to a shared library
        #   3. find location of your python development files,
        #      if you are using `uv`, it should be something like this:
        #      - include_path: /home/user/.local/share/uv/python/cpython-3.13.3-linux-x86_64-gnu/include/python3.13
        #      - lib_path: /home/user/.local/share/uv/python/cpython-3.13.3-linux-x86_64-gnu/lib
        #   4. add `-I<include_path>` to the CFLAGS, e.g.
        #      -I/home/user/.local/share/uv/python/cpython-3.13.3-linux-x86_64-gnu/include/python3.13
        #   5. add `-L<lib_path> to the LFLAGS, e.g.
        #      LFLAGS := -lm -L/home/user/.local/share/uv/python/cpython-3.13.3-linux-x86_64-gnu/lib
        #   6. run `make`
        #   It should create the `ss.so` file you can copy to `lib` directory.
        LIB_PATH = Path("lib").joinpath("ss.so")
        return CDLL(LIB_PATH)

    def _c_args(self) -> tuple[Array[c_int], c_int, Array[c_int]]:
        """
        Translates sudoku puzzle to the arguments used by the solver.

        Return:
        --------
        puzzle_array: Array[c_int]
            a flat array containing the initial state of the puzzle
        size: c_int
            a c_int object with size of the puzzle, `9` for the classical one
        solution_array: Array[c_int]
            a flat array of the same same as puzzle_array, but containing only zeros
        """

        # TODO:
        # Implement the method:
        # - convert self._puzzle.size to `c_int`
        #   https://docs.python.org/3/library/ctypes.html#fundamental-data-types
        # - flatten the puzzle grid
        #   check the `flatten` method of the `SudokuGrid`
        # - and convert it to a C Array
        #   https://docs.python.org/3/library/ctypes.html#arrays
        # - create also an array full of `0`s
        # Return them
        size = c_int(self._puzzle.size)

        flat = [int(v) for v in self._puzzle.flatten()]
        ArrayType = c_int * len(flat)
        puzzle_array = ArrayType(*flat)
        solution_array = ArrayType(*([0] * len(flat)))
        return puzzle_array, size, solution_array

    def _grid_from_array(self, solution: Array[c_int]) -> SudokuGrid:
        """
        Translates the C array into a sudoku grid.

        Parameters:
        ----------
        solution: Array[c_int]
            an array containing the solution

        Return:
        --------
        grid: SudokuGrid
            a sudoku grid corresponding to the array
        """

        # TODO:
        # Implement the method:
        # - convert array to np.array
        #   * np.array can be initialized with anything iterable :)
        # - reshape the new array to correct shape!
        #   * https://numpy.org/doc/stable/reference/generated/numpy.reshape.html
        # Return a new SudokuGrid with the hiven array
        arr = np.array(list(solution), dtype=np.uint)
        arr = arr.reshape((self._puzzle.size, self._puzzle.size))
        return SudokuGrid(arr)

    def _run_algorithm(self) -> SudokuGrid | None:
        """
        Runs the algorithm.

        Return:
        --------
        grid: SudokuGrid | None
            `None` if the algorithm failed, otherwise a solution
        """
        dll = self._get_lib()

        puzzle_array, size, solution_array = self._c_args()
        result = dll.solve_puzzle(puzzle_array, size, solution_array)
        if result == 0:
            return None

        return self._grid_from_array(solution_array)
