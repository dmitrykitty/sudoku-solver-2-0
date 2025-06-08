import argparse
import sys
from src.model.grid import SudokuGrid
import concurrent.futures
from src.solvers.solver_type import SudokuSolverType


def parse_args():
    parser = argparse.ArgumentParser(
        prog="python main.py", description="Sudolver - yet another sudoku solver."
    )
    parser.add_argument(
        "puzzle_path", help="Path to the file containing a sudoku puzzle"
    )
    parser.add_argument(
        "--algorithm",
        "-a",
        dest="algorithm",
        type=SudokuSolverType,
        choices=list(SudokuSolverType),
        default=SudokuSolverType.NAIVE,
        help="algorithm used to solver the sudoku",
    )
    parser.add_argument(
        "-t",
        "--time-limit",
        type=float,
        default=60.0,
        help="Time limit for the solver (in seconds)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        with open(args.puzzle_path, "r") as f:
            puzzle_data = f.read()
    except Exception as e:
        print(f"Error reading puzzle file: {e}")
        sys.exit(1)

    try:
        puzzle = SudokuGrid.from_text(puzzle_data.strip().splitlines())
    except Exception as e:
        print(f"Invalid puzzle format: {e}")
        sys.exit(1)
    try:
        solution = args.algorithm.solve(puzzle, args.time_limit)
        if solution is not None:
            print(solution)
            sys.exit(0)
        else:
            print("INFEASIBLE")
            rows = puzzle._array.tolist()
            print("    - puzzle grid:")
            for row in rows:
                print(",".join(str(int(x)) for x in row))
            sys.exit(1)
    except (TimeoutError, concurrent.futures.TimeoutError):
        print("TIMEOUT")
        sys.exit(2)
    except Exception as e:
        print(f"Solver error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
