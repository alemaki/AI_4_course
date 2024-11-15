from board import Board
from board import Color

class ComputerPlayer:
    def __init__(self, initial_board: Board):
        self.visisted_boards: set[Board]