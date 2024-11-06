#include <iostream>
#include <string>
#include <vector>
#include <random>
#include <cmath>
#include <algorithm>

using namespace std;

typedef vector<int64_t> Path;


#define TEST_PRINT 1

random_device dev;
mt19937 rng(dev());

double get_random_real(const double min, const double max)
{
    uniform_real_distribution<double> dist(min, max);
    return dist(rng);
}

double get_random_int(const int64_t min, const int64_t max)
{
    uniform_int_distribution<int> dist(min, max);
    return dist(rng);
}

inline double get_euclidean_distance(pair<double, double> point1, pair<double, double> point2)
{
    return sqrt((point1.first - point2.first)*(point1.first - point2.first)
                + (point1.second - point2.second)*(point1.second - point2.second));
}

template <typename T>
vector<int64_t> get_sorted_indices(const vector<T>& vec)
{
    vector<int64_t> indices(vec.size());
    iota(indices.begin(), indices.end(), 0);
    sort(indices.begin(), indices.end(), [&](int a, int b)
    {
        return vec[a] < vec[b];
    });
    return indices;
}


class TravelingSalesmanSolver
{
    vector<string> point_names;
    vector<pair<double, double>> points;


public:
    TravelingSalesmanSolver(vector<string> point_names, vector<pair<double, double>> points);
    TravelingSalesmanSolver(int64_t n);

    inline double get_distance(int64_t point1_index, int64_t point2_index) const
    {
        return get_euclidean_distance(this->points[point1_index], this->points[point2_index]);
    }

    void print_init_info() const;
    int64_t get_best_path_index(const vector<Path>& paths) const;
    double path_length(const Path& path) const;
    Path generate_random_path() const;
    vector<Path> generate_random_paths(int64_t size) const;
    vector<Path> tournament_select_paths(const vector<Path>& paths, int64_t select_size) const;
    vector<Path> generate_children(const vector<Path>& parents) const;
    /* Partially mapped crossover */
    pair<Path, Path> PMX_crossover(const Path& parent1, const Path& parent2) const;
    void mutate(Path& path) const;
    Path find_solution() const;

};

TravelingSalesmanSolver::TravelingSalesmanSolver(vector<string> point_strings, vector<pair<double, double>> points){}

TravelingSalesmanSolver::TravelingSalesmanSolver(int64_t n)
{
    if (!((n > 0) && (n <= 100)))
    {
        throw "Bad n error.";
    }

    this->points.resize(n);
    this->point_names.resize(n);

    for (int64_t i = 0; i < n; i++)
    {
        this->points[i] = {get_random_real(0, 500),  get_random_real(0, 500)};
        string point_mame = "(" + to_string(this->points[i].first) + ", " + to_string(this->points[i].second) + ")";
        this->point_names[i] = move(point_mame);
    }
}

int64_t TravelingSalesmanSolver::get_best_path_index(const vector<Path>& paths) const
{
    double min = INT64_MAX;
    int64_t index = 0;
    for (int i = 0; i < paths.size(); i++)
    {
        double length = this->path_length(paths[i]);
        if (length < min)
        {
            min = length;
            index = i;
        }
    }
    return index;
}

void TravelingSalesmanSolver::print_init_info() const
{
    cout << "points: " << endl;
    for (const string& point_name : this->point_names)
    {
        cout << point_name << " ";
    }
    cout << endl;

    for (int64_t i = 0; i < this->points.size(); i++)
    {
        for (int64_t j = i + 1; j < this->points.size(); j++)
        {
            cout << point_names[i] << " to " << point_names[j] << ": " << get_distance(i, j) << endl;
        }
    }
}

double TravelingSalesmanSolver::path_length(const Path& path) const
{
    double result;
    for (int64_t i = 0; i < path.size() - 1; i++)
    {
        result += this->get_distance(path[i], path[i+1]);
    }
    return result;
}

Path TravelingSalesmanSolver::generate_random_path() const
{
    Path path(this->points.size());
    iota(path.begin(), path.end(), 0);
    shuffle(path.begin(), path.end(), rng);
    return path;
}

vector<Path> TravelingSalesmanSolver::generate_random_paths(int64_t size) const
{
    vector<Path> generation(size);
    for (int64_t i = 0; i < size; i++)
    {
        generation[i] = this->generate_random_path();
    }
    return generation;
}

vector<Path> TravelingSalesmanSolver::tournament_select_paths(const vector<Path>& paths, int64_t select_size) const
{
     vector<Path> selected_paths(select_size);
     vector<double> paths_length(paths.size());

     for (int i = 0; i < paths.size(); i++)
     {
         paths_length[i] = this->path_length(paths[i]);
     }

     vector<int64_t> sorted_paths_length_indices = get_sorted_indices(paths_length);

     for (int i = 0; i < select_size; i++)
     {
         selected_paths[i] = paths[sorted_paths_length_indices[i]];
     }

     return selected_paths;
}

vector<Path> TravelingSalesmanSolver::generate_children(const vector<Path>& parents) const
{
    vector<Path> result;
    vector<int64_t> indices_for_crossover(parents.size());
    iota(indices_for_crossover.begin(), indices_for_crossover.end(), 0);
    shuffle(indices_for_crossover.begin(), indices_for_crossover.end(), rng);


    for (size_t i = 0; i < indices_for_crossover.size() - 1; i += 2)
    {
        const Path& parent1 = parents[indices_for_crossover[i]];
        const Path& parent2 = parents[indices_for_crossover[i + 1]];

        pair<Path, Path> offspring = PMX_crossover(parent1, parent2);

        Path child1 = {offspring.first};
        Path child2 = {offspring.second};

        result.push_back(child1);
        result.push_back(child2);
    }

    /* when last parent doesn't get make offspring */
    if (indices_for_crossover.size() % 2 != 0)
    {
        result.push_back(parents[indices_for_crossover.size() - 1]);
    }

    return result;
}

/* Partially mapped crossover */
pair<vector<int64_t>, Path> TravelingSalesmanSolver::PMX_crossover(const Path& parent1, const Path& parent2) const
{
    Path parent1_map(parent1.size());
    vector<int64_t> parent2_map(parent2.size());

    pair<Path, Path> result;

    result.first.resize(parent1.size(), -1);
    result.second.resize(parent1.size(), -1);

    pair<vector<bool>, vector<bool>> placed_numbers;
    placed_numbers.first.resize(parent1.size(), false);
    placed_numbers.second.resize(parent1.size(), false);

    for (int i = 0; i < parent1.size(); i++)
    {
        parent1_map[parent1[i]] = i;
        parent2_map[parent2[i]] = i;
    }

    int64_t start = get_random_int(0, parent1.size() - 1);
    int64_t end = get_random_int(0, parent1.size() - 1);
    if (end < start)
    {
        swap(start, end);
    }

    for (int64_t i = start; i <= end; i++)
    {
        result.first[i] = parent1[i];
        result.second[i] = parent2[i];
        placed_numbers.first[parent1[i]] = true;
        placed_numbers.second[parent2[i]] = true;
    }

    for (int64_t i = 0; i < parent1.size(); i++)
    {
        if (!placed_numbers.first[i])
        {
            int64_t gene_index = parent2_map[i];

            while (result.first[gene_index] != -1)
            {
                gene_index = parent2_map[result.first[gene_index]];
            }
            result.first[gene_index] = i;
            placed_numbers.first[i] = true;
        }
    }

    for (int64_t i = 0; i < parent2.size(); i++)
    {
        if (!placed_numbers.second[i])
        {
            int64_t gene_index = parent1_map[i];

            while (result.second[gene_index] != -1)
            {
                gene_index = parent1_map[result.second[gene_index]];
            }
            result.second[gene_index] = i;
            placed_numbers.second[i] = true;
        }
    }

    return result;

}

void TravelingSalesmanSolver::mutate(Path& path) const
{
    // do nothing for now
}

#define INITIAL_PATHS_SCALAR 1
#define SELECT_WINNERS_DELIM 2
#define NEW_RANDOM_GENERATIONS_DELIM 4
#define GENERATIONS 10

Path TravelingSalesmanSolver::find_solution() const
{
    int64_t n = this->points.size();
    vector<Path> current_paths = this->generate_random_paths(n*INITIAL_PATHS_SCALAR);
    int64_t select_winners_size = current_paths.size()/SELECT_WINNERS_DELIM;
    int64_t current_best_index = this->get_best_path_index(current_paths);

    cout << this->path_length(current_paths[current_best_index]) << endl;

    for (int i = 1; i < GENERATIONS; i++)
    {
        current_paths = this->tournament_select_paths(current_paths, select_winners_size);
        vector<Path> children = this->generate_children(current_paths);
        vector<Path> new_generation = this->generate_random_paths(n/NEW_RANDOM_GENERATIONS_DELIM);

        current_paths.insert(current_paths.end(), children.begin(), children.end());
        int64_t current_best_index = this->get_best_path_index(current_paths);
        cout << this->path_length(current_paths[current_best_index]) << endl;
        current_paths.insert(current_paths.end(), new_generation.begin(), new_generation.end());
    }
}

int main()
{
    TravelingSalesmanSolver solver(5);

#if TEST_PRINT
    solver.print_init_info();

    vector<Path> paths = solver.generate_random_paths(2);

    Path first = paths[0];
    Path second = paths[1];

    cout << endl << "First path: ";
    for (int i = 0; i < first.size(); i++)
    {
        cout << first[i] << ", ";
    }
    cout << endl << "Second path: ";
    for (int i = 0; i < second.size(); i++)
    {
        cout << second[i] << ", ";
    }

    pair<Path, Path> children = solver.PMX_crossover(first, second);

    cout << endl << "First crossover: ";
    for (int i = 0; i < children.first.size(); i++)
    {
        cout << children.first[i] << ", ";
    }
    cout << endl << "Second crossover: ";
    for (int i = 0; i < children.second.size(); i++)
    {
        cout << children.second[i] << ", ";
    }
    cout << endl << endl;

    vector<Path> all_paths = {first, second, children.first, children.second};
    int64_t best_index = solver.get_best_path_index(all_paths);

    cout << "First path length: " << solver.path_length(first) << endl;
    cout << "Second path length: " << solver.path_length(second) << endl;
    cout << "First crossover length: " << solver.path_length(children.first) << endl;
    cout << "Second crossover length: " << solver.path_length(children.second) << endl;
    cout << "Best: " << solver.path_length(all_paths[best_index]) << endl;
    cout << endl;



#endif // TEST_PRINT

    solver.find_solution();
}
