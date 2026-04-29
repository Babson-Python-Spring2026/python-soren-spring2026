'''
Notes and comments:

'''

import random


MINE = "💣"
HIDDEN = "♦"


def get_integer(prompt, minimum, maximum):
    while True:
        user_input = input(prompt)

        try:
            number = int(user_input)
            if minimum <= number <= maximum:
                return number
            else:
                print(f"Must be an integer between ({minimum}-{maximum})")
        except ValueError:
            print(f"Must be an integer between ({minimum}-{maximum})")


def create_mine_locations(height, width, mine_count):
    all_locations = []

    for row in range(height):
        for col in range(width):
            all_locations.append((row, col))

    return set(random.sample(all_locations, mine_count))


def count_neighboring_mines(row, col, height, width, mines):
    count = 0

    for row_change in [-1, 0, 1]:
        for col_change in [-1, 0, 1]:
            if row_change == 0 and col_change == 0:
                continue

            neighbor_row = row + row_change
            neighbor_col = col + col_change

            if 0 <= neighbor_row < height and 0 <= neighbor_col < width:
                if (neighbor_row, neighbor_col) in mines:
                    count += 1

    return count


def create_number_board(height, width, mines):
    board = []

    for row in range(height):
        board_row = []

        for col in range(width):
            if (row, col) in mines:
                board_row.append(MINE)
            else:
                neighboring_mines = count_neighboring_mines(row, col, height, width, mines)

                if neighboring_mines == 0:
                    board_row.append("")
                else:
                    board_row.append(str(neighboring_mines))

        board.append(board_row)

    return board


def print_board(number_board, revealed, reveal_all=False):
    height = len(number_board)
    width = len(number_board[0])

    print()

    print("    ", end="")
    for col in range(width):
        print(f"  {col}  ", end="")
    print()

    divider = "    " + "- " * (width * 3 - 1)
    print(divider.rstrip())

    for row in range(height):
        print(f"  {row} |", end="")

        for col in range(width):
            if reveal_all or (row, col) in revealed:
                value = number_board[row][col]

                if value == "":
                    print("    |", end="")
                elif value == MINE:
                    print(f" {value} |", end="")
                else:
                    print(f" {value}  |", end="")
            else:
                print(f" {HIDDEN}  |", end="")

        print()
        print(divider.rstrip())

    print()


def all_safe_places_revealed(height, width, mines, revealed):
    safe_count = height * width - len(mines)
    return len(revealed) == safe_count


def main():
    height = get_integer("You must enter an integer (2 - 10) : ", 2, 10)
    width = get_integer("Board width (2 - 10) : ", 2, 10)

    max_mines = height * width
    mine_count = get_integer(f"How many mines (less then {max_mines}) : ", 1, max_mines - 1)

    mines = create_mine_locations(height, width, mine_count)
    number_board = create_number_board(height, width, mines)

    revealed = set()

    while True:
        print_board(number_board, revealed)

        over = get_integer("How many over would you like to dig? : ", 0, width - 1)
        down = get_integer("How many down would you like to dig? : ", 0, height - 1)

        row = down
        col = over

        if (row, col) in revealed:
            continue

        if (row, col) in mines:
            print_board(number_board, revealed, reveal_all=True)
            break

        revealed.add((row, col))

        if all_safe_places_revealed(height, width, mines, revealed):
            print_board(number_board, revealed, reveal_all=True)
            print("Congratulations! You Won!")
            break


main()