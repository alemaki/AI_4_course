from board import Board
from board import Color
from queue import Queue
from math import inf
import copy

class Node:
    def __init__(self, board: Board, color_to_play: Color):
        self.board: Board = copy.deepcopy(board)
        self.row: int = -1
        self.col: int = -1 
        self.horizontal: int = -1
        self.points_made: int = 0
        self.children: list[Node] = []
        self.alpha = -inf
        self.beta = inf
        self.should_generate_new_children: list[bool] = []
        self.color_to_play: bool = color_to_play
        self.generated_children = False

        self.evaluation: int = 0 

    def set_move_on_node(self, row: int, col: int, horizontal: bool):
        assert(self.board.can_place_line_at(row, col, horizontal))
        self.row = row
        self.col = col
        self.horizontal = horizontal
        self.points_made = self.board.place_line(row, col, self.color_to_play, horizontal)
        self.evaluate_move()

    def evaluate_move(self):
        if self.points_made == 0:
            self.color_to_play = Color.get_opposite(self.color_to_play)

    def generate_children(self):
        self.generated_children = True
        for i in range(0, self.board.rows + 1):
            for j in range(0, self.board.cols):
                if self.board.can_place_line_at(i, j, True):
                    node: Node = Node(self.board, self.color_to_play)
                    self.children.append(node)
                    node.set_move_on_node(i, j, True)

        for i in range(0, self.board.rows):
            for j in range(0, self.board.cols + 1):
                if self.board.can_place_line_at(i, j, False):
                    node: Node = Node(self.board, self.color_to_play)
                    self.children.append(node)
                    node.set_move_on_node(i, j, False)
        

        
class ComputerPlayer:
    def __init__(self, initial_board: Board, first_to_play: bool):
        self.visited_boards: dict[tuple[Board, Color], Node] = {} # Have to encode who is next to play, because it is different cases even if boards are the same.
        self.color = Color.FIRST if first_to_play else Color.SECOND
        self.player_color = Color.get_opposite(self.color)
        self.tree = Node(initial_board, Color.FIRST) 
        self.generate_all_nodes() 
        # before optimisation. when generating entire tree. 3 2 runs with time: 58 seconds.

        # Ugly code but that way the board is always initialised in the beggining. No need to think after that.
        # if first_to_play:
        #     print("Computer estimates getting", self.max_value(self.tree, -inf, inf), "score (computer's points - player's points).")
        # else:
        #     print("Computer estimates getting", self.min_value(self.tree, -inf, inf), "score (computer's points - player's points).")
        # Now with alpha beta pruning the code runs for less than 15 seconds for 3 by 2 board.

    def generate_all_nodes(self):
        q: Queue = Queue()
        q.put(self.tree)

        while not q.empty():
            node: Node = q.get()
            color_to_play: Color = node.color_to_play

            if ((node.board, color_to_play) in self.visited_boards):
                children = self.visited_boards[node.board, color_to_play].children
                node.children = children # ref
                continue
            else:
                node.generate_children()
                for child in node.children:
                    q.put(child)

            self.visited_boards[(node.board, color_to_play)] = node


    def generate_children_for_node(self, node: Node, color_to_play: Color):
        if node.generated_children:
            return
        
        if ((node.board, color_to_play) in self.visited_boards):
            children = self.visited_boards[node.board, color_to_play].children
            node.children = children # ref
        else:
            node.generate_children()
        self.visited_boards[(node.board, color_to_play)] = node
 
    def get_move_for_board(self, board: Board) -> tuple[int, int, bool]:
        assert((board, self.color) in self.visited_boards) # remove this because now we do not generate all the possible moves the player might do, because of alpha beta pruning
        assert(not board.is_game_finished())
        node: Node = self.visited_boards[board, self.color]
        _ = self.max_value(node, -inf, inf)
        needed_child: Node
        max_stat = -inf
        for child in node.children:
            if child.color_to_play == self.color and child.alpha > max_stat:
                needed_child = child
                max_stat = child.alpha
            elif child.color_to_play != self.color and child.beta > max_stat and child.beta != inf:
                needed_child = child
                max_stat = child.beta
        print("Computer estimates getting", max_stat, "score (computer's points - player's points).")
        return (needed_child.row, needed_child.col, needed_child.horizontal)
    

    def max_value(self, node: Node, alpha, beta):
        self.generate_children_for_node(node, self.color)
        v = -inf
        if node.board.is_game_finished():
            points = node.board.first_player_points - node.board.second_player_points if self.color == Color.FIRST\
                     else node.board.second_player_points - node.board.first_player_points
            node.alpha = points
            return points

        if node.alpha != -inf:
            return node.alpha

        for child in node.children:
            if (child.color_to_play == self.color):
                v = max(v, self.max_value(child, alpha, beta))
            else:
                v = max(v, self.min_value(child, alpha, beta))
            if v >= beta:
                node.alpha = v
                return v
            alpha = max(alpha, v)
            node.alpha = alpha
        return v
    
    def min_value(self, node: Node, alpha, beta):
        self.generate_children_for_node(node, self.color.get_opposite())
        v = inf
        if node.board.is_game_finished():
            points = node.board.first_player_points - node.board.second_player_points if self.color == Color.FIRST\
                     else node.board.second_player_points - node.board.first_player_points
            node.beta = points
            return points

        if node.beta != inf:
            return node.beta

        for child in node.children:
            if (child.color_to_play == self.color):
                v = min(v, self.max_value(child, alpha, beta))
            else:
                v = min(v, self.min_value(child, alpha, beta))
            if v <= alpha:
                node.beta = v
                return v
            beta = min(beta, v)
            node.beta = beta
        return v

