from board import Board
from board import Color
from computer import ComputerPlayer
class DotsAndBoxesGame:
    def __init__(self, rows: int, columns: int, computer_first: bool = False):
        self.board: Board = Board(rows, columns)
        self.computer_first: bool = computer_first
        self.computer_to_play: bool = computer_first
        self.current_turn: int = 0
        self.player_color: Color = Color.FIRST if not computer_first else Color.SECOND
        self.computer_color: Color = Color.FIRST if computer_first else Color.SECOND
        self.computer: ComputerPlayer = ComputerPlayer(self.board, computer_first)

    def play(self):
        self.board.print_board()
        
        while (not self.board.is_game_finished()):
            self.turn()

        print("Winner:")
        if self.board.first_player_points == self.board.second_player_points:
            print("Noone")
        else:
            print("Computer" if ((self.computer_first and self.board.first_player_points > self.board.second_player_points)
                                    or (not self.computer_first and self.board.first_player_points < self.board.second_player_points))
                    else "Player")
        best_player_points = self.board.first_player_points
        other_player_points = self.board.second_player_points
        if best_player_points < other_player_points:
            best_player_points, other_player_points = other_player_points, best_player_points
        print(best_player_points, "to", other_player_points)

        return    
        
    def turn(self):
        self.current_turn += 1
        if not self.computer_to_play:
            self.player_turn()
            self.computer_to_play = True
        else:
            self.computer_turn()
            self.computer_to_play = False

    def player_turn(self):
        while True: 
            if self.board.is_game_finished():
                break
            (row, col, horizontal) = self._get_player_input()
            points: int = self.board.place_line(row, col, self.player_color, horizontal)
            print("Player plays on turn", self.current_turn, "and earns", points, "points:\n")
            self.board.print_board()
            if points == 0:
                break


    def _get_player_input(self) -> tuple[int, int, bool]:
        print("Please put your input (row, col for the two points, indexed from 1.) as space-separated values:")
        while True:
            try:
                user_input = input().strip().split()
                dot_row1 = int(user_input[0]) - 1
                dot_col1 = int(user_input[1]) - 1
                dot_row2 = int(user_input[2]) - 1
                dot_col2 = int(user_input[3]) - 1
                if dot_row2 < dot_row1:
                    dot_row1, dot_row2 = dot_row2, dot_row1
                    dot_col1, dot_col2 = dot_col2, dot_col1
                if dot_row2 - dot_row1 != 1 and dot_row2 - dot_row1 != 0:
                    raise IndexError("Invalid rows.")
                if dot_col2 - dot_col1 != 1 and dot_col2 - dot_col1 != 0:
                    raise IndexError("Invalid cols.")
                if dot_row2 - dot_row1 + dot_col2 - dot_col1 != 1:
                    raise IndexError("Diagonal lines are invalid.")
                row = dot_row1
                col = dot_col1
                horizontal = (dot_row2 - dot_row1 == 0)

                if self.board.can_place_line_at(row, col, horizontal):
                    break
                print("Impossible move, try again!")
            except (ValueError, IndexError):
                print("Invalid input, try again! Format: row col row col (indexed from 1)")
        return (row, col, horizontal)
    
    def computer_turn(self):
        while True: 
            if self.board.is_game_finished():
                break
            (row, col, horizontal) = self.computer.get_move_for_board(self.board)
            points: int = self.board.place_line(row, col, self.computer_color, horizontal)
            print("Computer plays on turn", self.current_turn, "and earns", points, "points:\n" if points == 0 else "point")
            self.board.print_board()
            if points == 0:
                break
                



print("Would you like to play first? (yes/y or _)")
user_input: str = input()
computer_first = True 
if user_input.lower() in ["yes", "y"]:
    computer_first = False 

game = DotsAndBoxesGame(3, 2, computer_first)
game.play()