from board import Board
from board import Color
import copy

class Node:
    def __init__(self, board: Board, is_comp_to_play: bool = True, is_start_node: bool = False):
        self.board: Board = copy.deepcopy(board)
        self.row: int = -1
        self.col: int = -1 
        self.horizontal: int = -1
        self.points_made: int = 0
        self.children_generated: bool = False
        self.children: list[Node] = []
        self.should_generate_new_children: list[bool] = []
        self.is_comp_to_play: bool = is_comp_to_play
        self.is_start_node = is_start_node

        self.evaluation: int = 0 

    def set_move_on_node(self, row: int, col: int, horizontal: int):
        assert(self.board.can_place_line_at(row, col, horizontal))
        self.row = row
        self.col = col
        self.horizontal = horizontal
        self.points_made = self.board.place_line(row, col, horizontal)
        self.evaluate_move()

    def evaluate_move(self):
        if self.points_made == 0:
            self.is_comp_to_play = not self.is_comp_to_play

    def generate_children(self):
        for i in 0..self.board.rows + 1:
            for j in 0..self.board.cols:
                if self.board.can_place_line_at(i, j, True):
                    node: Node = Node(self.board, self.is_comp_to_play)
                    self.children.append(node)
                    node.set_move_on_node(i, j, True)

        for i in 0..self.board.rows:
            for j in 0..self.board.cols + 1:
                if self.board.can_place_line_at(i, j, False):
                    node: Node = Node(self.board, self.is_comp_to_play)
                    self.children.append(node)
                    node.set_move_on_node(i, j, False)
        

        
class ComputerPlayer:
    def __init__(self, initial_board: Board, first_to_play: bool):
        self.visisted_boards: dict[tuple[Board, Color], Node] = {} # Have to encode who is next to play, because it is different cases even if boards are the same.
        self.tree: Node = Node(initial_board, first_to_play, True)
        self.color = Node
