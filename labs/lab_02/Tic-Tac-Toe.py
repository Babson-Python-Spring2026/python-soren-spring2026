"""
TIC TAC TOE — FUNCTION SCAFFOLD

Board Representation Rules:
- Board is a list of 9 integers.
- 1-9  → open squares
- 10   → X
- -10  → O

Winning rule:
- Any row, column, or diagonal that sums to:
    30   → X wins
   -30   → O wins


Assume:
- X plays first
- X is human
-O is computer
"""


def create_board() -> list[int]:
    """
    Create and return a new Tic-Tac-Toe board.

    Returns:
        A list containing the numbers 1 through 9.
    """
    return [1, 2, 3, 4, 5, 6, 7, 8, 9]
    pass


def display_board(board: list[int]) -> None:
    """
    Display the Tic-Tac-Toe board in a 3x3 format.

    Requirements:
    - Show X for value 10
    - Show O for value -10
    - Show the square number (1-9) for open squares
    - Format the board clearly with rows and separators
    """    
    
    def cell(value: int) -> str:
        if value == 10: return 'X'
        elif value == -10: return 'O'
        else: return str(value)
            
    print()

    for row in range(3):
        row_values = [cell(board[row * 3 + col]) for col in range(3)]
        print('   |   |   ')
        print(f' {row_values[0]} | {row_values[1]} | {row_values[2]} ')
        print('   |   |   ')
        if row < 2:
            print('-----------')
    print()


def check_tie(board: list[int]) -> bool:
    """
    Determine whether the board is full.

    Returns:
        True  → if no open squares remain
        False → otherwise
    """
    return all(value in (10, -10) for value in board)

    pass




def check_winner(board: list[int]) -> str | None:
    """
    Determine if a player has won.

    Requirements:
    - Check all rows
    - Check all columns
    - Check both diagonals
    - Use the board sum rule (30 / -30)

    Returns:
        'X', 'O', or None
    """
    winning_lines = [
        # Rows
        [board[0], board[1], board[2]],
        [board[3], board[4], board[5]],
        [board[6], board[7], board[8]],
        # Columns
        [board[0], board[3], board[6]],
        [board[1], board[4], board[7]],
        [board[2], board[5], board[8]],
        # Diagonals
        [board[0], board[4], board[8]],
        [board[2], board[4], board[6]],
    ]

    for line in winning_lines:
        total = sum(line)
        if total == 30:
            return "X"
        if total == -30:
            return "O"

    return None

    pass


def game_over(board: list[int], x_moves: bool) -> str | None:
    """
    Determine if the game has ended.

    Rules:
    - If a player has won, return 'X' or 'O'
    - If the board is full and no winner, return 'TIE'
    - Otherwise return None
    """
    winner = check_winner(board)
    if winner is not None:
        return winner

    if check_tie(board):
        return "TIE"

    return None
    pass


def get_human_move(board: list[int]) -> str:
    """
    Prompt the human player to select a square.

    Returns:
        The raw input string entered by the user.
    """
    return input("Choose an open square (1-9): ")

    pass


def get_computer_move(board: list[int]) -> int:
    """
    Determine the computer's move.

    Requirements:
    - Select an open square.
    - For now, may choose the first available open square.

    Returns:
        An integer representing the chosen square number.
    """
    for value in board:
        if value not in (10, -10):
            return value

    raise ValueError("No open squares available.")

    pass


def is_valid_move(board: list[int], move: str) -> tuple[bool, int | None]:
    """
    Validate a player's move.

    Steps:
    - Convert input to integer.
    - Ensure it is between 1 and 9.
    - Ensure the square is not already taken.

    Returns:
        (True, index)  → if valid
        (False, None)  → otherwise
    """
    try:
        square = int(move)
    except ValueError:
        return (False, None)

    if square < 1 or square > 9:
        return (False, None)

    index = square - 1

    if board[index] in (10, -10):
        return (False, None)

    return (True, index)

    pass


def place_move(board: list[int], index: int, x_moves: bool) -> None:
    """
    Place a move on the board.

    Rules:
    - If x_moves is True, place 10
    - If x_moves is False, place -10
    - Modify the board in place
    """
    board[index] = 10 if x_moves else -10
    pass

def play_game() -> None:
    """
    Run the full Tic-Tac-Toe game loop.

    Responsibilities:
    - Create a fresh board using create_board()
    - Track whose turn it is (X goes first)
    - Loop until the game ends:
        - Clear the screen (optional, if you have a helper)
        - Display the board each turn
        - If it is X's turn:
            - Get human input via get_human_move(board)
          Else:
            - Get computer move via get_computer_move(board)
        - Validate the move using is_valid_move(board, move)
            - If invalid: show an error message (if your validator doesn’t) and continue
        - Apply the move using place_move(board, index, x_moves)
        - Check for end-of-game using game_over(board, x_moves)
            - If it returns 'X' or 'O': announce winner and stop
            - If it returns 'TIE': announce tie and stop
        - Switch turns (toggle x_moves)

    Output:
    - Prints the game progression and final result to the console.
    """
    board = create_board()
    x_moves = True

    while True:
        display_board(board)

        if x_moves:
            move = get_human_move(board)
        else:
            computer_square = get_computer_move(board)
            print(f"Computer chooses square {computer_square}")
            move = str(computer_square)

        valid, index = is_valid_move(board, move)

        if not valid or index is None:
            print("Invalid move. Try again.")
            continue

        place_move(board, index, x_moves)

        result = game_over(board, x_moves)
        if result is not None:
            display_board(board)
            if result == "TIE":
                print("It's a tie!")
            else:
                print(f"{result} wins!")
            break

        x_moves = not x_moves


if __name__ == "__main__":
    play_game()
