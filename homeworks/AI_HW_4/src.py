from enum import Enum

class Color(Enum):
    EMPTY = 0
    FIRST = 1
    SECOND = 2

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
            self.vertical_line_rows.append([Color.EMPTY]*cols)

        self.first_player_points = 0
        self.second_player_points = 0
        self.current_turn = 0
    
    def print_board(self):

        for i in range(0, self.rows):
            line_str: str = ""
            for (_, color) in enumerate(self.horizontal_line_rows[i]):
                line_str += "O"
                if color != Color.EMPTY:
                    line_str += "---"
                else:
                    line_str += "   "
            line_str += "O"
            print(line_str)

            line_strings: list[str] = ["", "", ""]
            for (_, color) in enumerate(self.vertical_line_rows[i]):
                if color != Color.EMPTY:
                    line_strings = list(map(lambda x: x + "|", line_strings))
                else:
                    line_strings = list(map(lambda x: x + " ", line_strings))
                line_strings = list(map(lambda x: x + "   ", line_strings))

            print(line_strings[0])
            print(line_strings[1])
            print(line_strings[2])

        line_str: str = ""
        for (_, color) in enumerate(self.horizontal_line_rows[self.rows]):
            line_str += "O"
            if color != Color.EMPTY:
                line_str += "---"
            else:
                line_str += "   "
        line_str += "O"
        print(line_str)

    def _assert_line_within_bounds(self, row: int, col: int, horizontal: bool = True):
        if horizontal:
            assert(0 <= row < self.rows + 1 and 0 <= col < self.cols)
        else:
            assert(0 <= col < self.cols + 1 and 0 <= row < self.rows)

    """
    Returns true if point is made
    """
    def place_line(self, row: int, col: int, color: Color, horizontal: bool = True):
        self._assert_line_within_bounds(row, col, horizontal)
        if horizontal:
            self.horizontal_line_rows[row][col] = color
        else:
            self.vertical_line_rows[row][col] = color
        points: int = self.get_points_made_at_placed_line(row, col, horizontal)
        self._set_score_at_placed_line(row, col, horizontal)
        if color == Color.FIRST:
            self.first_player_points += points
        else:
            self.second_player_points += points
        self.current_turn += 1
        return points > 0

    def can_place_line_at(self, row, col, horizontal: bool = True):
        if horizontal:
            if not (0 <= row < self.rows + 1 and 0 <= col < self.cols):
                return False
        else:
            if not (0 <= col < self.cols + 1 and 0 <= row < self.rows):
                return False
        if horizontal:
            return (0 <= row < self.rows + 1 and 0 <= col < self.cols)
        else:
            return (0 <= col < self.cols + 1 and 0 <= row < self.rows)


    def get_points_made_at_placed_line(self, row: int, col: int, horizontal: bool = True):
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

        if horizontal and (row < self.rows) and self.is_square_closed(row, col):
            self.square_colors[row][col] = color
        if (not horizontal) and (col < self.cols) and self.is_square_closed(row, col):
            self.square_colors[row][col] = color

        if horizontal and (row > 0) and self.is_square_closed(row - 1, col):
            self.square_colors[row - 1][col] = color
        elif (not horizontal) and (col > 0) and self.is_square_closed(row, col - 1):
            self.square_colors[row][col - 1] = color
        
    def is_square_closed(self, row, col):
        assert(0 <= row < self.rows and 0 <= col < self.cols)
        return (self.horizontal_line_rows[row][col] != Color.EMPTY 
                and self.horizontal_line_rows[row + 1][col] != Color.EMPTY
                and self.vertical_line_rows[row][col] != Color.EMPTY 
                and self.vertical_line_rows[row][col + 1] != Color.EMPTY)

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