from board import Board
from board import Color

class DotsAndBoxesGame:
    def __init__(self, rows: int, columns: int, computer_first: bool = False):
        self.board: Board = Board(rows, columns)
        self.computer_first: bool = computer_first
        self.computer_to_play: bool = computer_first
        self.current_turn: int = 0
        self.player_color: Color = Color.FIRST if not computer_first else Color.SECOND
        self.computer_color: Color = Color.FIRST if computer_first else Color.SECOND

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
        return    
        
    def turn(self):
        self.current_turn += 1
        if not self.computer_to_play:
            self.player_turn()
            self.computer_to_play = True
        else:
            #self.computer_turn()
            self.computer_to_play = False

    def player_turn(self):
        while True: 
            (row, col, horizontal) = self._get_player_input()
            points: int = self.board.place_line(row, col, self.player_color, horizontal)
            print("Player plays on turn", self.current_turn, "and earns", points, "points:\n")
            self.board.print_board()
            if points == 0:
                break


    def _get_player_input(self) -> tuple[int, int, bool]:
        print("Please put your input (row, col, horizontal) as space-separated values:")
        while True:
            try:
                user_input = input().strip().split()
                row = int(user_input[0])
                col = int(user_input[1])
                horizontal = bool(int(user_input[2]))
                if self.board.can_place_line_at(row, col, horizontal):
                    break
                print("Impossible move, try again!")
            except (ValueError, IndexError):
                print("Invalid input, try again! Format: row col horizontal")
        return (row, col, horizontal)
                


game = DotsAndBoxesGame(2, 2)
game.play()