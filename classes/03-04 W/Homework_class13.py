'''
Soren — 8 / 10

Overall

Solid submission with clear reasoning.

Strengths

Good explanation of state and transitions.
Correct invariants.
Clear explanation of output.

Weaknesses

Some comments slightly repetitive.
A few sections could be more detailed.

AI likelihood

Moderate.

Estimated probability: 30–40%

GRADE 90

'''

"""
Homework: Reading Code with State / Transitions / Invariants (Tic-Tac-Toe)

This program brute-forces tic-tac-toe WITHOUT recursion.

What it actually counts:
- It explores all possible games where X starts and players alternate.
- The search STOPS as soon as someone wins (a terminal state).
- It also records full boards that end in a tie.
- It tracks UNIQUE *terminal* boards “up to symmetry” (rotations + reflections),
  meaning rotated/flipped versions are treated as the same terminal board.

YOUR TASKS:

RULE:  Do not change any executable code (no reformatting logic, no renaming variables, no moving lines). 
       Only add/replace comments and docstrings.
       
1) Define STATE for this program.
   - What variables change as the program runs?
   the changing state variables: board, unique_seen, full_boards, x_wins_on_full_board, draws_on_full_board, x_wins, o_wins, and ties.
2) Explain where TRANSITIONS happen.
   - Where does the state change? (where in the code, which functions)
   in the nested loops transitions happen when a move is put on the board they also happen when the moves are removed.
   transitions also happen in record_unique_board() and record_full_board(). the program updates unique_seen and increments counters.
3) Identify 4 INVARIANTS.
   - What properties remain true as the program runs (and what checks enforce them).
   - For instance: has_winner() is a check; the invariant is “we do not continue exploring after a win.”
   1. moves can only be done on empty spots. enforced by if board[o1] == ' ':
   2. x and o alternate turns (x goes first). enforced by the hardcoded structure of nested loops
   3. search stops after a winning board. enforced by should_continue() and if has_winner() is true:
   4. symmetrical boards are only counted once in the unique total. enforced by standard_form and unique_seen
4) For every function that says ''' TODO ''', replace that docstring with a real explanation
   of what the function does (1-4 sentences).
5) Add inline comments anywhere you see "# TODO" explaining what that code block is doing.
6) DO NOT USE AI. Write 5-8 sentences explaining one non-obvious part (choose one):  
   (a) symmetry logic (what makes a board unique), 
   (b) why we undo moves, 
   (c) why standard_form() produces uniqueness
   the tic tac toe tester (or whatever you want to call it) uses one shared board to test. a move is placed
   and all possible outcomes are tested. then it erases it and tries another move and repeats. this is interesting
   because it reuses the board. the counters work as the tracking device. however, maybe less elegant but I would
   imagine doing it by saving each board when it's found as the board and start fully from the beginning checking for repeats
7) The output from the program is two print statements:
       127872
       138 81792 46080 91 44 3

    explain what each number represents.
    1. total number of full game 'paths' how it can be played
    2. number of unique terminal boards
    3. number of paths or sequences where x wins on the 9th move of the game
    4. number of ways the game ends in a draw
    5. number of unique terminal board for X to win
    6. number of unique terminal boards for O to win
    7. number of unique terminal boards with a tie


Submission:
- Update this file with your answers. Commit and sync

"""

# ----------------------------
# Global running totals (STATE)
# ----------------------------

unique_seen = []             # TODO: What does this list store? Why do we store "standard forms"?
# Saves one standard version of each final board so that rotated or mirrored boards aren’t counted multiple times
board = [' '] * 9            # TODO: What does this represent? Why do we undo moves?
# This is the current board and is a flat list of 9 spaces

full_boards = 0              # TODO: What does this count?
# counts the number of games to reach a full board at move 9
x_wins_on_full_board = 0     # TODO: What does this count?
# count of ways X wins on its last move
draws_on_full_board = 0      # TODO: What does this count?
# count of ways O wins on last move

x_wins = 0                   # TODO: What does this count?
# counts ways for x to win
o_wins = 0                   # TODO: What does this count?
# counts ways for o to win
ties = 0                     # TODO: What does this count?
# counts ways to tie


# ----------------------------
# Board representation helpers
# ----------------------------

def to_grid(flat_board: list[str]) -> list[list[str]]:
    ''' changes the board from a flat list of 9 cells into a 3x3 nested list.
    this makes it easier to rotate or flip the board when checking symmetry.
    the function returns a new grid without changing the original list. '''
    grid = []
    for row in range(3):
        row_vals = []
        for col in range(3):
            row_vals.append(flat_board[row * 3 + col])
        grid.append(row_vals)
    return grid


def rotate_clockwise(grid: list[list[str]]) -> list[list[str]]:
    ''' Returns a new 3x3 grid that is the input grid rotated 90 degrees clockwise.
    This is used when generating all symmetric versions of the board. '''
    rotated = [[' '] * 3 for _ in range(3)]
    for r in range(3):
        for c in range(3):
            rotated[c][2 - r] = grid[r][c]
    return rotated


def flip_vertical(grid: list[list[str]]) -> list[list[str]]:
    ''' Returns a vertically flipped version of the grid by swapping the top and bottom rows.
    This creates a reflected form of the board for symmetry checking. '''
    return [grid[2], grid[1], grid[0]]


def standard_form(flat_board: list[str]) -> list[list[str]]:
    ''' Computes a 'standard' representation of the board under symmetry.
    It generates the 4 rotations of the board and the 4 rotations of its vertical flip,
    then returns the smallest one so symmetry-equivalent boards have the same representation. '''
    grid = to_grid(flat_board)
    flipped = flip_vertical(grid)

    variants = []
    for _ in range(4):
        variants.append(grid)
        variants.append(flipped)
        grid = rotate_clockwise(grid)
        flipped = rotate_clockwise(flipped)

    return min(variants)


def record_unique_board(flat_board: list[str]) -> None:
    ''' Records a final board only if its standard form has not been seen before.
    If the board is new the function stores its form and updates the correct
    unique-terminal counter depending on whether X won, O won, or the board is a tie. '''
    global x_wins, o_wins, ties

    rep = standard_form(flat_board)

    # TODO: Why do we check "rep not in unique_seen" before appending?
    # Only add this board if its symmetrical form is new.
    if rep not in unique_seen:
        unique_seen.append(rep)

        # TODO: This updates counts for unique *terminal* boards. What are the categories?
        # Classify the newly discovered unique terminal board as an X win, O win, or tie.
        winner = who_won(flat_board)
        if winner == 'X':
            x_wins += 1
        elif winner == 'O':
            o_wins += 1
        else:
            ties += 1


# ----------------------------
# Game logic
# ----------------------------

def has_winner(flat_board: list[str]) -> bool:
    ''' Checks whether either player has three in a row on the current board.
    It tests every row, column, and diagonal and returns True as soon as
    it finds a winning line for X or O. '''
    winning_lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # cols
        [0, 4, 8], [6, 4, 2],             # diagonals
    ]

    for line in winning_lines:
        score = 0
        for idx in line:
            if flat_board[idx] == 'X':
                score += 10
            elif flat_board[idx] == 'O':
                score -= 10
        if abs(score) == 30:
            return True

    return False


def who_won(flat_board: list[str]) -> str:
    ''' Determines the result of a terminal board. It returns 'X' if X has a winning line
    'O' if O has a winning line and 'TIE' if no winning line exists. '''
    winning_lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # cols
        [0, 4, 8], [6, 4, 2],             # diagonals
    ]

    for line in winning_lines:
        score = 0
        for idx in line:
            if flat_board[idx] == 'X':
                score += 10
            elif flat_board[idx] == 'O':
                score -= 10

        if score == 30:
            return 'X'
        elif score == -30:
            return 'O'

    return 'TIE'


def should_continue(flat_board: list[str], move_number: int) -> bool:
    ''' Decides whether the search should keep going from the current board.
    If the current move created a winning board that board is recorded as terminal
    and the function returns False. '''
    # TODO: What condition makes us STOP exploring deeper moves?
    # Stop exploring deeper once a winner exists, because that board is already terminal.
    if has_winner(flat_board):
        record_unique_board(flat_board)
        return False
    return True


def record_full_board(flat_board: list[str]) -> None:
    ''' Decides after a terminal board is reached after all 9 squares are filled.
    It records the board as a unique terminal board if needed, counts the full-board game,
    and classifies the result as either an X win on move 9 or a draw. '''
    global full_boards, x_wins_on_full_board, draws_on_full_board

    # TODO: This is a terminal state because the board is full (9 moves). No moves left
    record_unique_board(flat_board)
    full_boards += 1

    # TODO: On a full board, either X has won (last move) or it is a draw.And this updates the counts
    if has_winner(flat_board):
        x_wins_on_full_board += 1
    else:
        draws_on_full_board += 1


# ----------------------------
# Brute force search (9 nested loops)
# ----------------------------

# TODO: In these loops, where are transitions taking place?
# Transitions happen in these loops whenever the program writes a move onto the board and whenever it later erases that move to restore the previous state.
# TODO: Where else do transitions happen?
# Other transitions happen inside record_unique_board() and record_full_board() where the program updates counts and stores newly found terminal boards.

# Move 1: X
for x1 in range(9):
    board[x1] = 'X'
    if should_continue(board, 1):

        # Move 2: O
        for o1 in range(9):
            if board[o1] == ' ':
                board[o1] = 'O'
                if should_continue(board, 2):

                    # Move 3: X
                    for x2 in range(9):
                        if board[x2] == ' ':
                            board[x2] = 'X'
                            if should_continue(board, 3):

                                # Move 4: O
                                for o2 in range(9):
                                    if board[o2] == ' ':
                                        board[o2] = 'O'
                                        if should_continue(board, 4):

                                            # Move 5: X
                                            for x3 in range(9):
                                                if board[x3] == ' ':
                                                    board[x3] = 'X'
                                                    if should_continue(board, 5):

                                                        # Move 6: O
                                                        for o3 in range(9):
                                                            if board[o3] == ' ':
                                                                board[o3] = 'O'
                                                                if should_continue(board, 6):

                                                                    # Move 7: X
                                                                    for x4 in range(9):
                                                                        if board[x4] == ' ':
                                                                            board[x4] = 'X'
                                                                            if should_continue(board, 7):

                                                                                # Move 8: O
                                                                                for o4 in range(9):
                                                                                    if board[o4] == ' ':
                                                                                        board[o4] = 'O'
                                                                                        if should_continue(board, 8):

                                                                                            # Move 9: X
                                                                                            for x5 in range(9):
                                                                                                if board[x5] == ' ':
                                                                                                    board[x5] = 'X'

                                                                                                    # Full board reached (terminal)
                                                                                                    record_full_board(board)

                                                                                                    # undo move 9
                                                                                                    board[x5] = ' '

                                                                                        # undo move 8
                                                                                        board[o4] = ' '

                                                                            # undo move 7
                                                                            board[x4] = ' '

                                                                # undo move 6
                                                                board[o3] = ' '

                                                    # undo move 5
                                                    board[x3] = ' '

                                        # undo move 4
                                        board[o2] = ' '

                            # undo move 3
                            board[x2] = ' '

                # undo move 2
                board[o1] = ' '

    # undo move 1
    board[x1] = ' '


print(full_boards)
print(len(unique_seen), x_wins_on_full_board, draws_on_full_board, x_wins, o_wins, ties)
