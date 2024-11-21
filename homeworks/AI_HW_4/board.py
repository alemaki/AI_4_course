from enum import Enum
from copy import deepcopy

class Color(Enum):
    EMPTY = 0
    FIRST = 1
    SECOND = 2

    def get_opposite(color):
        return Color.SECOND if color == Color.FIRST else Color.FIRST


class Board:
    def __init__(self, rows: int, cols: int):
        self.rows: int = rows
        self.cols: int = cols
        self.horizontal_line_rows: list[list[Color]] = []
        self.vertical_line_rows: list[list[Color]] = []
        for _ in range(0, rows + 1):
            self.horizontal_line_rows.append([Color.EMPTY]*cols)
        for _ in range(0, rows):
            self.vertical_line_rows.append([Color.EMPTY]*(cols + 1))

        self.square_colors: list[list[Color]] = []
        for _ in range(0, rows):
            self.square_colors.append([Color.EMPTY]*cols)

        self.first_player_points = 0
        self.second_player_points = 0
    
    def print_board(self):

        for i in range(0, self.rows):
            line_str: str = ""
            for (_, color) in enumerate(self.horizontal_line_rows[i]):
                line_str += "O"
                if color != Color.EMPTY:
                    line_str += "-----"
                else:
                    line_str += "     "
            line_str += "O"
            print(line_str)

            line_strings: list[str] = ["", "", ""]
            for (j, color) in enumerate(self.vertical_line_rows[i]):
                if color != Color.EMPTY:
                    line_strings = list(map(lambda x: x + "|", line_strings))
                else:
                    line_strings = list(map(lambda x: x + " ", line_strings))
                line_strings = list(map(lambda x: x + "     ", line_strings))
                if j < self.cols and self.square_colors[i][j] != Color.EMPTY:
                    line_strings[1] = line_strings[1][0:j*6+3] + ("F" if self.square_colors[i][j] == Color.FIRST else "S") + line_strings[1][j*6+4:]
            print(line_strings[0])
            print(line_strings[1])
            print(line_strings[2])

        line_str: str = ""
        for (_, color) in enumerate(self.horizontal_line_rows[self.rows]):
            line_str += "O"
            if color != Color.EMPTY:
                line_str += "-----"
            else:
                line_str += "     "
        line_str += "O"
        print(line_str)

    def _assert_line_within_bounds(self, row: int, col: int, horizontal: bool = True):
        if horizontal:
            assert(0 <= row < self.rows + 1 and 0 <= col < self.cols)
        else:
            assert(0 <= col < self.cols + 1 and 0 <= row < self.rows)

    """
    Returns points made at placing that line
    """
    def place_line(self, row: int, col: int, color: Color, horizontal: bool = True) -> int:
        self._assert_line_within_bounds(row, col, horizontal)
        if horizontal:
            self.horizontal_line_rows[row][col] = color
        else:
            self.vertical_line_rows[row][col] = color
        points: int = self._get_points_made_at_placed_line(row, col, horizontal)
        self._set_score_at_placed_line(row, col, color, horizontal)
        return points

    def can_place_line_at(self, row: int, col: int, horizontal: bool = True) -> bool:
        if horizontal and not (0 <= row < self.rows + 1 and 0 <= col < self.cols):
                return False
        elif not horizontal and not (0 <= col < self.cols + 1 and 0 <= row < self.rows):
                return False
        
        return not self.check_placed_line(row, col, horizontal)
    
    def check_placed_line(self, row: int, col: int, horizontal: bool = True) -> bool:
        self._assert_line_within_bounds(row, col, horizontal)
        if horizontal:
            return self.horizontal_line_rows[row][col] != Color.EMPTY
        else:
            return self.vertical_line_rows[row][col] != Color.EMPTY


    def _get_points_made_at_placed_line(self, row: int, col: int, horizontal: bool = True) -> int:
        points: int = 0
        if horizontal and (row < self.rows):
            points += 1 if self.is_square_closed(row, col) else 0
        if (not horizontal) and (col < self.cols):
            points += 1 if self.is_square_closed(row, col) else 0

        if horizontal and (row > 0):
            points += 1 if self.is_square_closed(row - 1, col) else 0
        elif (not horizontal) and (col > 0):
            points += 1 if self.is_square_closed(row, col - 1) else 0

        return points
    
    def _set_score_at_placed_line(self, row: int, col: int, color: Color, horizontal: bool = True):
        points: int = self._get_points_made_at_placed_line(row, col, horizontal)
        assert(points >= 0)
        if color == Color.FIRST:
            self.first_player_points += points
        else:
            self.second_player_points += points

        if horizontal and (row < self.rows) and self.is_square_closed(row, col):
            self.square_colors[row][col] = color
        if (not horizontal) and (col < self.cols) and self.is_square_closed(row, col):
            self.square_colors[row][col] = color

        if horizontal and (row > 0) and self.is_square_closed(row - 1, col):
            self.square_colors[row - 1][col] = color
        elif (not horizontal) and (col > 0) and self.is_square_closed(row, col - 1):
            self.square_colors[row][col - 1] = color
        
    def is_square_closed(self, row, col) -> bool:
        assert(0 <= row < self.rows and 0 <= col < self.cols)
        return (self.horizontal_line_rows[row][col] != Color.EMPTY 
                and self.horizontal_line_rows[row + 1][col] != Color.EMPTY
                and self.vertical_line_rows[row][col] != Color.EMPTY 
                and self.vertical_line_rows[row][col + 1] != Color.EMPTY)
    
    def is_game_finished(self) -> bool:
        return (self.first_player_points + self.second_player_points) == (self.rows*self.cols)

    def __eq__(self, other):
        if not isinstance(other, Board):
            return False
        if self.first_player_points != other.first_player_points\
            or self.second_player_points != other.second_player_points:
            return False
        
        for i in range(0, self.rows + 1): # do not care who placed the specific line, only if both are empty or both are filled
            for j in range(0, self.cols):
                if (self.horizontal_line_rows[i][j] == Color.EMPTY) != (other.horizontal_line_rows[i][j] == Color.EMPTY):
                    return False

        for i in range(0, self.rows):
            for j in range(0, self.cols + 1):
                if (self.vertical_line_rows[i][j] == Color.EMPTY) != (other.vertical_line_rows[i][j] == Color.EMPTY):
                    return False

        return True

    def __hash__(self):
        horizontal_lines_hash = tuple(tuple(color != Color.EMPTY for color in row) for row in self.horizontal_line_rows)
        vertical_lines_hash = tuple(tuple(color != Color.EMPTY for color in row) for row in self.vertical_line_rows)

        return hash((
            self.first_player_points,
            self.second_player_points,
            horizontal_lines_hash,
            vertical_lines_hash,
        ))

# board = Board(3, 3)
# board.print_board()
# print("\n\n\n")
# print("made point:", board.place_line(0, 0, Color.FIRST))
# board.print_board()
# print("\n\n\n")
# print("made point:", board.place_line(0, 0, Color.FIRST, False))
# board.print_board()
# print("\n\n\n")
# print("made point:", board.place_line(1, 0, Color.FIRST))
# board.print_board()
# print("\n\n\n")
# print("made point:", board.place_line(0, 1, Color.FIRST, False))
# board.print_board()
# print("\n\n\n")
# print("made point:", board.place_line(1, 1, Color.FIRST))
# board.print_board()
# print("\n\n\n")
# print("made point:", board.place_line(1, 0, Color.FIRST, False))
# board.print_board()
# print("\n\n\n")
# print("made point:", board.place_line(2, 0, Color.FIRST))
# board.print_board()
# print("\n\n\n")


# board2 = deepcopy(board)
# board.place_line(2, 1, Color.FIRST)
# board2.place_line(2, 1, Color.SECOND)
# print(f"Hash for board1: {hash(board)}")
# print(f"Hash for board2: {hash(board2)}")
# print(f"Equality check: {board == board2}")

# color1 = Color.FIRST
# color2 = Color.FIRST
# print(f"Hash for color1: {hash(color1)}")
# print(f"Hash for color2: {hash(color2)}")
# print(f"Equality check: {color1 == color2}")


# print(f"Hash for board1, color1: {hash((board, color1))}")
# print(f"Hash for board1, color1: {hash((board2, color2))}")
# print(f"Equality check: {(board, color1) == (board2, color2)}")
