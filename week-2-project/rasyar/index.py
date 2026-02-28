from flask import Flask  # For creating the web app
from flask_cors import CORS  # For handling cross-origin requests
import random  # For generating random numbers
import heapq  # Priority queue implementation
from datetime import datetime  # For measuring execution time
from flask import jsonify  # For returning JSON responses
from flask import request  # For handling incoming requests

app = Flask(__name__)
CORS(app)  # Allow the react frontend to make requests to this backend


def generate_random_puzzle():
    board = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]

    # Shuffle the goal state to create a random puzzle
    for _ in range(100):
        moves = get_possible_moves(board)
        if moves:
            board = random.choice(moves)

    return board


def get_possible_moves(board):
    """
    This methods takes the current board state and returns a list of new board states that can be reached by moving the empty tile (0) in one of the four possible directions (up, down, left, right). Each new board state is a result of swapping the empty tile with an adjacent tile in the specified direction. The method ensures that the new positions are within the bounds of the 3x3 grid.
    """

    moves = []

    # fine where the empty tile is
    zero_pos = find_zero(board)
    row, col = (
        zero_pos  # Position of the empty tile (e.g. (2, 2) for the initial state)
    )

    # The four possible directions to move the empty tile: up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # Generate new board states by moving the empty tile in each direction
    for dr, dc in directions:
        new_row = row + dr
        new_col = col + dc

        # if the new position is within the bounds of the board, create a new board state by swapping the empty tile with the adjacent tile in that direction and add it to the list of possible moves
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            new_board = [
                row[:] for row in board
            ]  # Deep copy of the board with new memory ref
            temp = new_board[row][col]
            new_board[row][col] = new_board[new_row][new_col]
            new_board[new_row][new_col] = temp
            moves.append(new_board)

    return moves


def find_zero(board):
    # Find the position of the empty tile
    for i in range(3):
        for j in range(3):
            if board[i][j] == 0:
                return (i, j)
    return None


def board_to_tuple(board):
    # Convert the board to a tuple of tuples for immutability and hashing
    return tuple(tuple(row) for row in board)


def manhattan_distance(board):
    """
    This method calculates the Manhattan distance heuristic for the 8-puzzle problem. The Manhattan distance is the sum of the absolute differences of the row and column indices of each tile from its goal position. The method iterates through each tile in the current board state, calculates its current position and its goal position, and accumulates the total distance. The empty tile (0) is not included in the calculation.
    """

    distance = 0
    goal_positions = {
        1: (0, 0),
        2: (0, 1),
        3: (0, 2),
        4: (1, 0),
        5: (1, 1),
        6: (1, 2),
        7: (2, 0),
        8: (2, 1),
        0: (2, 2),
    }

    for i in range(3):
        for j in range(3):
            tile = board[i][j]

            if tile != 0:
                goal_i, goal_j = goal_positions[tile]
                distance += abs(i - goal_i) + abs(j - goal_j)

    return distance


def best_first_search(start_board):
    """
    This method implements the Best-First Search algorithm to solve the 8-puzzle problem. It uses a priority queue (min-heap) to explore the board states based on their Manhattan distance heuristic. The algorithm starts with the initial board state and repeatedly explores the most promising board state (the one with the lowest Manhattan distance) until it reaches the goal state. It also keeps track of visited states to avoid cycles and ensures that it does not revisit previously explored board configurations.
    """

    goal = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]

    frontier = []
    heapq.heappush(
        frontier, (manhattan_distance(start_board), start_board, [start_board])
    )

    # Track visited states to avoid cycles
    visited = set()
    visited.add(board_to_tuple(start_board))

    while frontier:
        _, current_board, path = heapq.heappop(frontier)

        # Check if we reached goal state
        if current_board == goal:
            return path

        # Expolore neighbors
        for next_board in get_possible_moves(current_board):
            board_tuple = board_to_tuple(next_board)

            if board_tuple not in visited:
                visited.add(board_tuple)
                new_path = path + [next_board]
                priority = manhattan_distance(next_board)
                heapq.heappush(frontier, (priority, next_board, new_path))

    return None  # No solution which is rarely the case


def save_solution_file(initial_board, solution_steps):
    """
    Save solution to solution.txt in a nice format.
    """
    with open("solution.txt", "w", encoding="utf-8") as f:
        f.write("=" * 50 + "\n")
        f.write("        8-PUZZLE SOLUTION - BEST-FIRST SEARCH\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Initial board
        f.write("INITIAL BOARD:\n")
        f.write("-" * 13 + "\n")
        for row in initial_board:
            f.write("| " + " | ".join(str(x) if x != 0 else " " for x in row) + " |\n")
        f.write("-" * 13 + "\n\n")

        # Solution steps
        f.write(f"SOLUTION (Total Cost: {len(solution_steps) - 1} moves):\n\n")

        for step_num, board in enumerate(solution_steps):
            f.write(f"Step {step_num}:\n")
            f.write("-" * 13 + "\n")
            for row in board:
                f.write(
                    "| " + " | ".join(str(x) if x != 0 else " " for x in row) + " |\n"
                )
            f.write("-" * 13 + "\n\n")

        f.write("=" * 50 + "\n")
        f.write(f"GOAL REACHED IN {len(solution_steps) - 1} MOVES!\n")
        f.write("=" * 50 + "\n")


@app.route("/generate", methods=["GET"])
def generate():
    board = generate_random_puzzle()
    return jsonify({"board": board, "message": "Random puzzle generated successfully"})


@app.route("/solve", methods=["POST"])
def solve():
    try:

        # Get the board from the request body
        data = request.get_json()
        board = data.get("board")

        # Validate the input board
        if not board:
            return jsonify({"error": "Board is required"}), 400

        print("[Backend] Solving puzzle...")
        solution_steps = best_first_search(board)

        if solution_steps is None:
            return jsonify({"error": "No solution found"}), 500

        # Save to file
        save_solution_file(board, solution_steps)
        print(f"[Backend] Solution found! Cost: {len(solution_steps) - 1} moves")

        return jsonify(
            {
                "initial_board": board,
                "steps": solution_steps,
                "total_cost": len(solution_steps) - 1,
                "message": "Solution saved to solution.txt",
            }
        )

    except Exception as e:
        print(f"[Backend] Error: {str(e)}")
        return jsonify({"error": "An error occurred while solving the puzzle"}), 500


if __name__ == "__main__":
    print("Flask app is running on http://localhost:3500")
    app.run(debug=True, port=3500)
