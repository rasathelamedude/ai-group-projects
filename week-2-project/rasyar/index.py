from flask import Flask  # For creating the web app
from flask_cors import CORS  # For handling cross-origin requests
import random  # For generating random numbers
import heapq  # Priority queue implementation
from datetime import datetime  # For measuring execution time
from flask import jsonify  # For returning JSON responses

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
    Get all valid next states from current board.
    Returns list of new board states.
    """

    moves = []
    zero_pos = find_zero(board)
    row, col = zero_pos  # Position of the empty tile

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right

    # Generate new board states by moving the empty tile in each direction
    for dr, dc in directions:
        new_row = row + dr
        new_col = col + dc

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


@app.route("/generate", methods=["GET"])
def generate():
    board = generate_random_puzzle()
    return jsonify({"board": board, "message": "Random puzzle generated successfully"})


@app.route("/solve", methods=["POST"])
def solve():
    pass


if __name__ == "__main__":
    print("Flask app is running on http://localhost:3500")
    app.run(debug=True, port=3500)
