#include <vector>
#include <iostream>
#include <random>
#include <chrono>
#include <iomanip>

using namespace std;

#define FAST_SOLUTION 1

struct NQueens
{
    int64_t N;
    vector<int64_t> queen_current_row;
#if not FAST_SOLUTION // this is only for memory purposes. Might cause heap exhaustion with bug numbers.
    vector<int64_t> row_total_queens;
    vector<int64_t> diag1_total_queens;
    vector<int64_t> diag2_total_queens;
#endif // not FAST_SOLUTION

    mt19937 rng;
    uniform_int_distribution<mt19937::result_type> distN;

    NQueens(int64_t N) : N(N),  rng(random_device()()), distN(0, N - 1)
    {
        random_device dev;
        rng = mt19937(dev());
        distN = uniform_int_distribution<mt19937::result_type>(0, N - 1);
    }

private:

    void place_queen(int64_t row, int64_t col) // no index guard, assume it's right!
    {
        this->queen_current_row[col] = row;
#if not FAST_SOLUTION
        this->row_total_queens[row]++;
        this->diag1_total_queens[col - row + this->N - 1]++;
        this->diag2_total_queens[col + row]++;
#endif // not FAST_SOLUTION
    }

    void remove_queen(int64_t col) // no guard, assume it's right!
    {
        int64_t row = this->queen_current_row[col];
        this->queen_current_row[col] = -1;
#if not FAST_SOLUTION
        this->row_total_queens[row]--;
        this->diag1_total_queens[col - row + this->N - 1]--;
        this->diag2_total_queens[col + row]--;
#endif // not FAST_SOLUTION
    }

    int64_t get_place_weight(int64_t row, int64_t col, bool count_current_queen = true) const
    {
        int64_t weight = 0;
#if not FAST_SOLUTION
        weight += this->diag1_total_queens[col - row + this->N - 1] - (count_current_queen ? 1 : 0);
        weight += this->diag2_total_queens[col + row] - (count_current_queen ? 1 : 0);
        weight += row_total_queens[row] - (count_current_queen ? 1 : 0);
#endif // not FAST_SOLUTION
        return weight;
    }

#if FAST_SOLUTION
    void _fill_knight()
    {
        /* 3 types of situations: */
        /* 1. n is odd we just use the other two cases and place queen on (n,n) */
        if ((this->N % 2 == 1))
        {
            this->N--;
            _fill_knight();
            place_queen(this->N, this->N);
            this->N++;

            return;
        }

        /* 2. n is even but modulo of 6 is not 2 (e.g. 8, 14, 20).
        Those are the easiest, just place queens in knight form. Split board in two halves */
        if ((this->N % 6) != 2)
        {
            for (int64_t j = 1; j <= this->N/2; j++)
            {
                int64_t row = j - 1;
                int64_t col = 2*j - 1;
                place_queen(row, col);
                /* second half */
                row = this->N/2 + j - 1;
                col = 2*(j - 1);
                place_queen(row, col);
            }

            return;
        }

        /* 3. In any other case the n modulo 6 is 2. Place queens with offset of 1
        in the first half (will overflow to the other side), and same with the second but in reverse*/
        /* The third point is thanks to Bo Bernhardsson's algorithm. Source  -  https://dl.acm.org/doi/pdf/10.1145/122319.122322 */
        for (int64_t j = 1; j <= this->N/2; j++)
        {
            int64_t row = j - 1;
            int64_t col = ((2*(j - 1) + this->N/2  - 1) % this->N);
            place_queen(row, col);
            /* second half */
            row = this->N - j;
            col = (this->N - 1 - (2*(j - 1) + this->N/2 - 1) % this->N);
            place_queen(row, col);
        }

        return;

    }
#endif // FAST_SOLUTION

    void _fill_random()
    {
        for (int64_t col = 0; col < this->N; col++)
        {
            int64_t row = distN(rng);
            this->place_queen(row, col);
        }
    }

public:
    void initialize_queens()
    {
        this->queen_current_row = vector<int64_t>(N, -1);
#if not FAST_SOLUTION
        this->row_total_queens = vector<int64_t>(N, 0);
        this->diag1_total_queens = vector<int64_t>(2*N - 1, 0);
        this->diag2_total_queens = vector<int64_t>(2*N - 1, 0);
#endif // not FAST_SOLUTION

#if FAST_SOLUTION
        this->_fill_knight();
#else
        this->_fill_random();
#endif // FAST_SOLUTION

        //this->print_info();
    }

    void print_info()
    {
        cout << "queens: ";
        for (int col = 0; col < this->N; col++)
        {
            cout << this->queen_current_row[col] << " ";
        }
#if not FAST_SOLUTION
        cout << endl << "rows: ";
        for (int row = 0; row < this->N; row++)
        {
            cout << this->row_total_queens[row] << " ";
        }
        cout << endl << "diag1: ";
        for (int diag = 0; diag < 2*this->N - 1; diag++)
        {
            cout << this->diag1_total_queens[diag] << " ";
        }
        cout << endl << "diag2: ";
        for (int diag = 0; diag < 2*this->N - 1; diag++)
        {
            cout << this->diag2_total_queens[diag] << " ";
        }
#endif // not FAST_SOLUTION
        cout << endl;
    }

    void swap_queen(int64_t col, int64_t new_row)
    {
        this->remove_queen(col);
        this->place_queen(new_row, col);
    }

    bool move_worst_queen()
    {
        int64_t worst_index = 0;
        int64_t worst_weight = 0;
        for (int64_t i = 0; i < N; i++)
        {
            int64_t weight = get_place_weight(this->queen_current_row[i], i);
            //cout << weight << " ";
            if (worst_weight < weight)
            {
                worst_index = i;
                worst_weight = weight;
            }
            else if (weight == worst_weight && distN(rng) % 2 == 0)
            {
                worst_index = i;
            }
        }
        //cout << endl;
        if (worst_weight == 0)
        {
            return true;
        }

        int64_t best_weight = worst_weight;
        int64_t best_row = worst_index == 0 ? N - 1 : 0;

        for (int64_t row = 0; row < N; row++)
        {
            int64_t weight = this->get_place_weight(row, worst_index, false);
            if (weight < best_weight)
            {
                best_weight = weight;
                best_row = row;
            }
            else if (weight == best_weight && distN(rng) % 2 == 0)
            {
                best_row = row;
            }
        }

        this->swap_queen(worst_index, best_row);

        //this->print_info();
        return false;
    }

#define ITERATIONS 4
    void find_solution()
    {
        while(true)
        {
            this->initialize_queens();
            int count = 0;
            while (count++ < ITERATIONS*this->N)
            {
                if (this->move_worst_queen())
                {
                    return;
                }
            }
        }

    }
};
#define FOREVER 0
int main ()
{
    do
    {

    int64_t N = 0;
    cin >> N;

    if (N == 2 || N == 3)
    {
        cout << -1 <<endl;
        return -1;
    }
    if (N == 1)
    {
        cout << "[0]" <<endl;
        return 0;
    }
    if (N <= 0)
    {
        return -1;
    }

    NQueens n_queens(N);

    auto start = chrono::high_resolution_clock::now();

    //cout << N << endl;
    //return 0;

    n_queens.find_solution();

    auto end = chrono::high_resolution_clock::now();
    if (N <= 100)
    {
        cout << "[";
        for (int i = 0; i < N - 1; i++)
        {
            cout << n_queens.queen_current_row[i] << ", ";
        }
        cout << n_queens.queen_current_row[N - 1];
        cout << "]" << endl;
    }
    else
    {
        cout << fixed << showpoint;
        cout << setprecision(2);
        cout << ((double)chrono::duration_cast<chrono::milliseconds>(end - start).count())/1000;
    }
    cout<<endl;

    } while(FOREVER);

    return 0;
}


/*
first revision with -O3
in secs
10000 - 0.33
20000 - 0.73
30000 - 1.67
40000 - 3.05
50000 - 5.07
60000 - 7.58
70000 - 10.56
80000 - 14.46
90000 - 18.61
100000 - 23.29

second - with knight placement, with -O3
10001 - 0.00
10002 - 0.00
10003 - 0.00
10004 - 0.00
10005 - 0.00
10006 - 0.00
10007 - 0.00
10008 - 0.00
10009 - 0.00
10010 - 0.00
100000 - 0.01
1000000 - 0.02
10000000 - 0.14
100000000 - 1.36
1000000000 - heap exhausting

second - with knight placement, with heap protection, with -O3
100000 - 0.00
1000000 - 0.00
1000004 - 0.01
10000000 - 0.05
10000004 - 0.06
100000000 - 0.40
100000004 - 0.56
1000000000 - heap exhausting
*/
