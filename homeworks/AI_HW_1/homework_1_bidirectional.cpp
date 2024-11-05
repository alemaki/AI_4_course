#include <iostream>
#include <chrono>
#include <vector>
#include <memory>
#include <cmath>
#include <unordered_map>
#include <unordered_set>
#include <stack>

struct Board
{
    std::vector<std::vector<int64_t>> data;
    std::pair<int64_t, int64_t> space_index;

    bool operator==(const Board& other) const
    {
        return this->data == other.data;
    }
};

struct BoardHash //tbh, no idea how this works, read it online
{
    std::size_t operator()(const Board& board) const
    {
        std::size_t hash = 0;
        for (const auto& row : board.data)
            {
            for (int64_t num : row)
            {
                hash ^= std::hash<int64_t>()(num) + 0x9e3779b9 + (hash << 6) + (hash >> 2);
            }
        }
        return hash;
    }
};

enum Move
{
    NONE = 0,
    LEFT = 1,
    RIGHT = 2,
    DOWN = 3,
    UP = 4
};

struct Node
{
    Board current_board;
    std::vector<Node*> children;
    Move current_move = Move::NONE ;
    Node* parent = nullptr;
    int64_t f_score = 0;
    int64_t h_score = 0;
    int64_t g_score = 0;
    bool generated_children = false;
    bool solution = false;

    ~Node()
    {
        for (Node* node : children)
        {
            delete node;
        }
    }
};

int64_t N;
int64_t space_index;
int64_t board_size;
Board current_board;
Board desired_board;
bool solvable = true;
std::unordered_map<int64_t, std::pair<int64_t, int64_t>> desired_board_map;
std::unordered_map<int64_t, std::pair<int64_t, int64_t>> beggining_board_map;
std::unordered_map<Board, Node*, BoardHash> visited_from_start;
std::unordered_map<Board, Node*, BoardHash> visited_from_goal;

void create_desired_board_map(const int64_t board_size, const int64_t space_index)
{
    bool space_index_placed = false;
    desired_board = {std::vector<std::vector<int64_t>>(board_size, std::vector<int64_t>(board_size, 0)), {0,0}};
    for (int64_t i = 0; i < board_size; i++)
    {
        for (int64_t j = 0; j < board_size; j++)
        {
            int current_index = i*board_size + j - (space_index_placed ? 1 : 0);
            if ((!space_index_placed) && space_index == current_index)
            {
                desired_board.data[i][j] = 0;
                desired_board.space_index =  {i, j};
                desired_board_map.insert({0, {i, j}});
                space_index_placed = true;
            }
            else
            {
                desired_board.data[i][j] = current_index + 1;
                desired_board_map.insert({current_index + 1, {i, j}});
            }
        }
    }
}

void print_board(const Board& board)
{

    for (uint64_t i = 0; i < board.data.size(); i++)
    {
        for (uint64_t j = 0; j < board.data[0].size(); j++)
        {
            std::cout << board.data[i][j] << " ";
        }
        std::cout << std::endl;
    }
    std::cout << std::endl;
}


int64_t get_inversion_for_indexes(int64_t row, int64_t col, const Board& board)
{
    int64_t inversions = 0;
    int64_t num = board.data[row][col];
    for (int i = row; i < board.data.size(); i++)
    {
        for (int j = i == row ? col : 0; j < board.data[0].size(); j++)
        {
            if (board.data[i][j] < num && board.data[i][j] != 0)
            {
                inversions++;
            }
        }
    }
    return inversions;
}

bool check_solvable(const Board& board)
{
    int64_t inversions = 0;
    for (int i = 0; i < board.data.size(); i++)
    {
        for (int j = 0; j < board.data[0].size(); j++)
        {
            inversions += get_inversion_for_indexes(i, j, board);
        }
    }
    if (board.data.size() % 2 == 0)
    {
        inversions += board.space_index.first - 1; //make it even so the check is the same in the end
    }
    return inversions % 2 == 0;
}

void input_stuff()
{
    std::cin >> N;
    std::cin >> space_index;

    space_index = space_index < 0 ? N : space_index;

    board_size = std::sqrt(N + 1);

    for (int64_t i = 0; i < board_size; i++)
    {
        current_board.data.push_back(std::vector<int64_t>());
        for (int64_t j = 0; j < board_size; j++)
        {
            int64_t buf;
            std::cin >> buf;
            current_board.data[i].push_back(buf);
            if (buf == 0)
            {
                current_board.space_index = {i, j};
            }
            beggining_board_map.insert({buf, {i,j}});

        }
    }

    solvable = check_solvable(current_board);

    create_desired_board_map(board_size, space_index);
}


#define STEP_WEIGHT 1
#define WRONG_PLACE_WEIGHT 1
void create_fhg_score(Node* node, bool reverse = false)
{
    if (!node)
    {
        return;
    }
    if (node->parent != nullptr)
    {
        node->g_score = node->parent->g_score + STEP_WEIGHT;
    }

    int64_t h_score = 0;
    /* heuristic */
    for (int64_t i = 0; i < node->current_board.data.size(); i++)
    {
        for (int64_t j = 0; j < node->current_board.data[0].size(); j++)
        {
            if (node->current_board.data[i][j] == 0) continue;
            int64_t num  = node->current_board.data[i][j];

            if(reverse)
            {
                h_score += (std::abs(beggining_board_map[num].first - i) + std::abs(beggining_board_map[num].second - j));
            }
            else
            {
                h_score += (std::abs(desired_board_map[num].first - i) + std::abs(desired_board_map[num].second - j));

            }
        }
    }

    if (h_score == 0)
    {
        node->solution = true;
    }

    node->h_score = h_score;
    node->f_score = node->g_score + node->h_score * WRONG_PLACE_WEIGHT;
}

bool check_valid_node_board(Node* node, bool reverse = false)
{
    if (reverse)
    {
        if (visited_from_goal.find(node->current_board) != visited_from_goal.end())
        {
            return false;
        }
        visited_from_goal.insert({node->current_board, node});
        return true;
    }

    if (visited_from_start.find(node->current_board) != visited_from_start.end())
    {
        return false;
    }
    visited_from_start.insert({node->current_board, node});
    return true;
}

Node* create_node_with_move(const Board& board, Move current_move, Node* parent, bool reverse = false)
{

    if (current_move == Move::NONE)
    {
        Node* node(new Node);
        node->current_board = board;
        node->current_move = Move::NONE;
        create_fhg_score(node, reverse);
        return node;
    }

    Board board_copy = board;
    int64_t board_size = board_copy.data.size();
    switch (current_move)
    {
    case Move::LEFT :
        {
            if (board_copy.space_index.second == board_size - 1)
            {
                return nullptr;
            }
            std::swap(board_copy.data[board_copy.space_index.first][board_copy.space_index.second],
                      board_copy.data[board_copy.space_index.first][board_copy.space_index.second + 1]);
            board_copy.space_index.second++;
            break;
        }
    case Move::RIGHT :
        {
            if (board_copy.space_index.second == 0)
            {
                return nullptr;
            }
            std::swap(board_copy.data[board_copy.space_index.first][board_copy.space_index.second],
                      board_copy.data[board_copy.space_index.first][board_copy.space_index.second - 1]);
            board_copy.space_index.second--;
            break;
        }
    case Move::UP :
        {
            if (board_copy.space_index.first == board_size - 1)
            {
                return nullptr;
            }
            std::swap(board_copy.data[board_copy.space_index.first][board_copy.space_index.second],
                      board_copy.data[board_copy.space_index.first + 1][board_copy.space_index.second]);
            board_copy.space_index.first++;
            break;
        }
    case Move::DOWN :
        {
            if (board_copy.space_index.first == 0)
            {
                return nullptr;
            }
            std::swap(board_copy.data[board_copy.space_index.first][board_copy.space_index.second],
                      board_copy.data[board_copy.space_index.first - 1][board_copy.space_index.second]);
            board_copy.space_index.first--;
            break;
        }
    }

    Node* node(new Node);
    if (!node)
    {
        std::cout << "No memory, bruh?" << std::endl;
        return nullptr;
    }

    node->current_move = current_move;
    node->current_board = std::move(board_copy);

    if(!check_valid_node_board(node, reverse))
    {
        delete node;
        return nullptr;
    }

    if (parent)
    {
        parent->children.push_back(node);
        node->parent = parent;
    }

    create_fhg_score(node, reverse);

    return node;
}

void generate_children(Node* root, bool reverse = false)
{
    create_node_with_move(root->current_board, Move::LEFT, root, reverse); // pushes child on it's own
    create_node_with_move(root->current_board, Move::RIGHT, root, reverse);
    create_node_with_move(root->current_board, Move::UP, root, reverse);
    create_node_with_move(root->current_board, Move::DOWN, root, reverse);

    root->generated_children = true;
}


int64_t beidirectional_IDA_search(Node* node, int64_t threshold, Node*& solution, Node*& opposite_solution, bool reverse = false)
{/*
    std::cout << (reverse ? "Rev \n" : "Str \n");
    print_board(node->current_board);
*/
    if (node->f_score > threshold)
    {
        return node->f_score;
    }
    if (node->solution)
    {
        solution = node;
        return 0;
    }

    if (reverse && (visited_from_start.find(node->current_board) != visited_from_start.end()))
    {
        //std::cout << "found from reverse" <<std::endl;
        solution = visited_from_start[node->current_board];
        opposite_solution = node;
        return 0;
    }
    else if (!reverse && (visited_from_goal.find(node->current_board) != visited_from_goal.end()))
    {

        //std::cout << "found from straight" <<std::endl;
        solution = node;
        opposite_solution = visited_from_goal[node->current_board];
        return 0;
    }

    if (!node->generated_children)
    {
        generate_children(node, reverse);
    }

    int64_t _min = INT64_MAX;
    for (Node* child : node->children)
    {
        int64_t result = beidirectional_IDA_search(child, threshold, solution, opposite_solution, reverse);
        if (solution)
        {
            return 0;
        }
        _min = std::min(result, _min);
    }
    return _min;
}

std::pair<Node*, Node*> bidirectional_IDA_star(Node* root, Node* goal)
{
    int64_t threshold = root->f_score;

    Node* solution = nullptr;
    Node* opposite = nullptr;
    visited_from_start.insert({root->current_board, root});
    visited_from_goal.insert({goal->current_board, goal});

    while (true) //bad idea, maybe threshold < 10^5?
    {
        if (solution)
        {
            return {solution, opposite};
        }
        int64_t result = beidirectional_IDA_search(root, threshold, solution, opposite);
        if (!solution) beidirectional_IDA_search(goal, threshold, solution, opposite, true);
        if (result < 0) //Overflow
        {
            return {nullptr, nullptr};
        }
        threshold = result;
    }
}

std::stack<Move> get_moves(std::pair<Node*, Node*> result)
{
    std::stack<Move> moves;
    std::vector<Move> buffer;

    while (result.second != nullptr && result.second->current_move != Move::NONE)
    {
        buffer.push_back(result.second->current_move);
        result.second = result.second->parent;
    }
    //std::cout << buffer.size() << std::endl;

    for (int i = buffer.size() - 1; i >= 0; i--)
    {
        switch (buffer[i])
        {
        case Move::LEFT :
            moves.push(Move::RIGHT);
            break;

        case Move::RIGHT :
            moves.push(Move::LEFT);
            break;

        case Move::UP :
            moves.push(Move::DOWN);
            break;

        case Move::DOWN :
            moves.push(Move::UP);
            break;
        }
    }

    while(result.first->parent != nullptr)
    {
        moves.push(result.first->current_move);
        result.first =(result.first->parent);
    }
    return moves;
}

int main(int argc, char* argv[])
{
    bool time = false;
    if (argc > 1)
    {
        if (std::string(argv[1]) == "-time")
        {
            time = true;
        }
    }

    input_stuff();
    if (!solvable)
    {
        std::cout << "-1" << std::endl;
        return 0;
    }

    auto start = std::chrono::high_resolution_clock::now();
    Node* root = create_node_with_move(current_board, Move::NONE, nullptr);
    Node* goal = create_node_with_move(desired_board, Move::NONE, nullptr, true);

    //std::cout << (root->current_board == goal->current_board) <<std::endl;

    std::pair<Node*, Node*> result = bidirectional_IDA_star(root, goal);

    auto end = std::chrono::high_resolution_clock::now();

    if (time)
    {
        std::cout << "time: " <<  ((double)std::chrono::duration_cast< std::chrono::milliseconds >((end - start)).count())/1000 << "s." << std::endl; // I hate this specifically
    }
    if (!result.first)
    {
        std::cout << "-1" << std::endl;
        return 0;
    }
    if (result.first == root)
    {
        std::cout << "0" << std::endl;
        return 0;
    }

    /*print_board(result.first->current_board);
    if (result.second)
    {
        print_board(result.second->current_board);
    }*/

    std::stack<Move> moves = get_moves(result);
    int64_t steps = moves.size();

    std::cout << steps << std::endl;
    while(!(moves.empty()))
    {
        Move current_move = moves.top();
        moves.pop();
        switch (current_move)
        {
        case Move::LEFT :
            {
                std::cout << "left" <<std::endl;
                break;
            }
        case Move::RIGHT :
            {
                std::cout << "right" <<std::endl;
                break;
            }
        case Move::DOWN :
            {
                std::cout << "down" <<std::endl;
                break;
            }
        case Move::UP :
            {
                std::cout << "up" <<std::endl;
                break;
            }
        default :
            {
                std::cout << "this is bad" <<std::endl;
                break;
            }
        }

    }

    delete root; //windows can deal with this better than I can or am willing to.
    delete goal;

    return 0;
}
/*

-1 st:
8
-1
1 2 3
4 5 6
8 7 0

0 st:
8
5
1 2 3
4 5 0
6 7 8

2 st:
8
5
3 1 2
4 5 0
6 7 8

3 st:
8
5
0 2 3
1 4 5
6 7 8

15
-1
1 2 3 4
5 6 7 8
9 10 11 12
13 14 0 15

-1 st:
8
-1
1 2 3
4 5 6
0 7 8

8
0
1 2 0
3 4 5
6 7 8

46 st:   - 6.0 secs
15
-1
8 4 6 9
7 5 3 0
2 1 12 11
10 13 14 15

46 st:   - 21.7 secs
15
-1
4 1 6 9
7 5 3 0
2 8 12 11
10 13 14 15

41 st:   - 4.792 secs
15
-1
4 1 6 9
2 7 3 11
5 0 8 12
10 13 14 15

39 st:   -  0.655 secs
15
-1
4 0 6 9
2 1 3 11
5 7 8 12
10 13 14 15

36 st:   - 0.172 secs
15
-1
0 4 6 9
2 1 3 11
5 7 8 12
10 13 14 15

28 st: - 0.02 secs
8
-1
8 4 6
7 5 3
2 1 0


22 st:
8
-1
0 5 3
6 4 8
2 7 1

22 st:
8
-1
6 5 3
2 4 8
0 7 1

21 st:
8
-1
6 5 3
2 4 8
7 0 1

14 st:
8
-1
2 6 5
4 0 3
7 1 8


12 st:
8
-1
2 6 5
4 1 3
0 7 8

10 st:
8
-1
2 6 5
1 0 3
4 7 8



8
-1
1 2 3
4 5 6
7 8 0

right
up
up
left
left


*/

