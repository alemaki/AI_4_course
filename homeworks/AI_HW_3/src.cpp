#include <iostream>
#include <string>
#include <vector>
#include <random>
#include <cmath>
#include <algorithm>
#include <float.h>
#include <unordered_set>

using namespace std;

typedef vector<uint64_t> Path;


#define TEST_PRINT 0
#define TEST_CITIES 1

/* if 1 will use PMX, if 0 TP*/
#define USE_TP_CROSSOVER 1
/* if 1 will use Roulette, if 0 Rank-based*/
#define USE_ROULETTE_SELECTION 0

random_device dev;
mt19937 rng(dev());

double get_random_real(const double min, const double max)
{
    uniform_real_distribution<double> dist(min, max);
    return dist(rng);
}

int64_t get_random_int(const int64_t min, const int64_t max)
{
    uniform_int_distribution<int64_t> dist(min, max);
    return dist(rng);
}

inline double get_euclidean_distance(pair<double, double> point1, pair<double, double> point2)
{
    return sqrt((point1.first - point2.first)*(point1.first - point2.first)
                + (point1.second - point2.second)*(point1.second - point2.second));
}

template <typename T>
vector<uint64_t> get_sorted_indices(const vector<T>& vec)
{
    vector<uint64_t> indices(vec.size());
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
    TravelingSalesmanSolver(uint64_t n);

    inline double get_distance(uint64_t point1_index, uint64_t point2_index) const
    {
        return get_euclidean_distance(this->points[point1_index], this->points[point2_index]);
    }

    void print_path_names(const Path& path) const;
    void print_init_info() const;
    uint64_t get_best_path_index(const vector<Path>& paths) const;
    double path_length(const Path& path) const;
    Path generate_random_path() const;
    vector<Path> generate_random_paths(uint64_t size) const;
    vector<Path> rank_based_selection(const vector<Path>& paths, uint64_t select_size) const;
    vector<Path> roulette_selection(const vector<Path>& paths, uint64_t select_size) const;
    vector<Path> generate_children(const vector<Path>& parents) const;
    /* Partially mapped crossover */
    pair<Path, Path> PMX_crossover(const Path& parent1, const Path& parent2) const;
    /* Two point crossover */
    pair<Path, Path> TP_crossover(const Path& parent1, const Path& parent2) const;
    void mutate(Path& path) const;
    void mutate_paths(vector<Path>& paths) const;
    Path find_solution() const;

};

TravelingSalesmanSolver::TravelingSalesmanSolver(vector<string> point_names, vector<pair<double, double>> points) : point_names(point_names), points(points)
{}

TravelingSalesmanSolver::TravelingSalesmanSolver(uint64_t n)
{
    if (!((n > 0) && (n <= 100)))
    {
        throw "Bad n error.";
    }

    this->points.resize(n);
    this->point_names.resize(n);

    for (uint64_t i = 0; i < n; i++)
    {
        this->points[i] = {get_random_real(0, 500),  get_random_real(0, 500)};
        string point_mame = "(" + to_string(this->points[i].first) + ", " + to_string(this->points[i].second) + ")";
        this->point_names[i] = move(point_mame);
    }
}

uint64_t TravelingSalesmanSolver::get_best_path_index(const vector<Path>& paths) const
{
    double min = this->path_length(paths[0]); // assume paths has something. xD
    uint64_t index = 0;
    for (uint64_t i = 1; i < paths.size(); i++)
    {
        double length = this->path_length(paths[i]);
        //cout << min << " > " << length << endl;
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

    for (uint64_t i = 0; i < this->points.size(); i++)
    {
        for (uint64_t j = i + 1; j < this->points.size(); j++)
        {
            cout << point_names[i] << " to " << point_names[j] << ": " << get_distance(i, j) << endl;
        }
    }
}

void TravelingSalesmanSolver::print_path_names(const Path& path) const
{
    for (uint64_t i = 0; i < path.size() - 1; i++)
    {
        cout << this->point_names[i] << " -> ";
    }
    cout << this->point_names[path.size() - 1];
    cout << endl;
}

double TravelingSalesmanSolver::path_length(const Path& path) const
{
    double result = 0;
    for (uint64_t i = 0; i < path.size() - 1; i++)
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

vector<Path> TravelingSalesmanSolver::generate_random_paths(uint64_t size) const
{
    vector<Path> generation(size);
    for (uint64_t i = 0; i < size; i++)
    {
        generation[i] = this->generate_random_path();
    }
    return generation;
}

vector<Path> TravelingSalesmanSolver::rank_based_selection(const vector<Path>& paths, uint64_t select_size) const
{
     vector<Path> selected_paths(select_size);
     vector<double> paths_length(paths.size());

     for (uint64_t i = 0; i < paths.size(); i++)
     {
         paths_length[i] = this->path_length(paths[i]);
     }

     vector<uint64_t> sorted_paths_length_indices = get_sorted_indices(paths_length);

     for (uint64_t i = 0; i < select_size; i++)
     {
         selected_paths[i] = paths[sorted_paths_length_indices[i]];
     }

     return selected_paths;
}


vector<Path> TravelingSalesmanSolver::roulette_selection(const vector<Path>& paths, uint64_t select_size) const
{
    vector<Path> selected_paths;
    vector<double> cumulative_fitness(paths.size() + 1, 0.0);
    unordered_set<uint64_t> selected_indices;

    double total_fitness = 0;
    for (uint64_t i = 0; i < paths.size(); i++)
    {
        total_fitness += 1.0 / this->path_length(paths[i]);
        cumulative_fitness[i + 1] = total_fitness;
    }

    for (uint64_t i = 0; i < select_size; i++)
    {
        double rand_val = get_random_real(0, total_fitness);
        auto it = lower_bound(cumulative_fitness.begin(), cumulative_fitness.end(), rand_val);
        uint64_t index = it - cumulative_fitness.begin();

        if (index != 0) /* might get actual 0 */
        {
            index --;
        }

        if (selected_indices.find(index) == selected_indices.end())
        {
            selected_paths.push_back(paths[index]);
            selected_indices.insert(index);
        }
    }

    return selected_paths;
}

vector<Path> TravelingSalesmanSolver::generate_children(const vector<Path>& parents) const
{
    vector<Path> result;
    vector<uint64_t> indices_for_crossover(parents.size());
    iota(indices_for_crossover.begin(), indices_for_crossover.end(), 0);
    shuffle(indices_for_crossover.begin(), indices_for_crossover.end(), rng);


    for (uint64_t i = 0; i < indices_for_crossover.size() - 1; i += 2)
    {
        const Path& parent1 = parents[indices_for_crossover[i]];
        const Path& parent2 = parents[indices_for_crossover[i + 1]];

#if USE_TP_CROSSOVER
        pair<Path, Path> offspring = this->TP_crossover(parent1, parent2);
#else
        pair<Path, Path> offspring = this->PMX_crossover(parent1, parent2);
#endif // USE_TP_CROSSOVER

        Path child1 = {offspring.first};
        Path child2 = {offspring.second};

        result.push_back(child1);
        result.push_back(child2);
    }

    return result;
}

/* Partially mapped crossover */
pair<Path, Path> TravelingSalesmanSolver::PMX_crossover(const Path& parent1, const Path& parent2) const
{
    vector<uint64_t> parent1_map(parent1.size());
    vector<uint64_t> parent2_map(parent2.size());

    pair<Path, Path> result;

    result.first.resize(parent1.size(), UINT64_MAX); // we shall assume N is not UINT64_MAX
    result.second.resize(parent1.size(), UINT64_MAX);

    vector<bool> placed_numbers1(parent1.size(), false);
    vector<bool> placed_numbers2(parent2.size(), false);

    for (uint64_t i = 0; i < parent1.size(); i++)
    {
        parent1_map[parent1[i]] = i;
        parent2_map[parent2[i]] = i;
    }

    uint64_t start = get_random_int(0, parent1.size() - 1);
    uint64_t end = get_random_int(0, parent1.size() - 1);
    if (end < start)
    {
        swap(start, end);
    }

    for (uint64_t i = start; i <= end; i++)
    {
        result.first[i] = parent1[i];
        result.second[i] = parent2[i];
        placed_numbers1[parent1[i]] = true;
        placed_numbers2[parent2[i]] = true;
    }

    for (uint64_t i = 0; i < parent1.size(); i++)
    {
        if (!placed_numbers1[i])
        {
            uint64_t gene_index = parent2_map[i];

            while (result.first[gene_index] != UINT64_MAX)
            {
                gene_index = parent2_map[result.first[gene_index]];
            }
            result.first[gene_index] = i;
            placed_numbers1[i] = true;
        }
    }

    for (uint64_t i = 0; i < parent2.size(); i++)
    {
        if (!placed_numbers2[i])
        {
            int64_t gene_index = parent1_map[i];

            while (result.second[gene_index] != UINT64_MAX)
            {
                gene_index = parent1_map[result.second[gene_index]];
            }
            result.second[gene_index] = i;
            placed_numbers2[i] = true;
        }
    }

    return result;

}

/*Two point crossover*/
pair<Path, Path> TravelingSalesmanSolver::TP_crossover(const Path& parent1, const Path& parent2) const
{
    vector<bool> placed_numbers1(parent1.size(), false);
    vector<bool> placed_numbers2(parent2.size(), false);

    pair<Path, Path> result;

    result.first.resize(parent1.size(), UINT64_MAX);
    result.second.resize(parent1.size(), UINT64_MAX);

    uint64_t start = get_random_int(0, parent1.size() - 1);
    uint64_t end = get_random_int(0, parent1.size() - 1);
    if (end < start)
    {
        swap(start, end);
    }

    for (uint64_t i = start; i <= end; i++)
    {
        result.first[i] = parent1[i];
        result.second[i] = parent2[i];
        placed_numbers1[parent1[i]] = true;
        placed_numbers2[parent2[i]] = true;
    }

    uint64_t begin = (end + 1) % parent2.size();
    uint64_t index = begin;
    uint64_t i = begin;
    do
    {
        uint64_t gene = parent2[i];
        if (!placed_numbers1[gene])
        {
            result.first[index] = gene;
            placed_numbers1[gene] = true;
            index = (index + 1) %  parent1.size();
        }
        i = (i + 1) % parent2.size();
    } while (i != begin);

    index = begin;
    i = begin;
    do
    {
        uint64_t gene = parent1[i];
        if (!placed_numbers2[gene])
        {
            result.second[index] = gene;
            placed_numbers2[gene] = true;
            index = (index + 1) %  parent2.size();
        }
        i = (i + 1) % parent1.size();
    } while (i != begin);

    return result;

}

void TravelingSalesmanSolver::mutate(Path& path) const
{
    int mutation_type = get_random_int(1, 3);
    switch (mutation_type)
    {
        case 1: /* Swap Mutation */
        {
            swap(path[get_random_int(0, path.size() - 1)], path[get_random_int(0, path.size() - 1)]);
            break;
        }
        case 2: /* Insertion Mutation */
        {
            uint64_t erase_at = get_random_int(0, path.size() - 1);
            uint64_t insert_at = get_random_int(0, path.size() - 2);
            uint64_t res = path[erase_at];
            path.erase(path.begin() + erase_at);
            path.insert(path.begin() + insert_at, res);
            break;
        }
        case 3: /* Inversion Mutation */
        {
            uint64_t start = get_random_int(0, path.size() - 2);
            uint64_t end = get_random_int(start + 1, path.size() - 1);
            reverse(path.begin() + start, path.begin() + end + 1);
            break;
        }
    }
}

void TravelingSalesmanSolver::mutate_paths(vector<Path>& paths) const
{
    for (auto& path : paths)
    {
        this->mutate(path);
    }
}

#define INITIAL_PATHS_SCALAR 200
#define SELECT_WINNERS_DELIM 5
#define NEW_RANDOM_GENERATIONS_SCALAR 200
#define GENERATIONS 10

Path TravelingSalesmanSolver::find_solution() const
{
    uint64_t n = this->points.size();
    vector<Path> current_paths = this->generate_random_paths(n*INITIAL_PATHS_SCALAR);
    uint64_t current_best_index = this->get_best_path_index(current_paths);

    cout << this->path_length(current_paths[current_best_index]) << endl;

    for (int i = 1; i < GENERATIONS; i++)
    {
#if TEST_PRINT
        cout << "Number of generated paths: " << current_paths.size() << endl;
#endif // TEST_PRINT
        uint64_t select_winners_size = current_paths.size()/SELECT_WINNERS_DELIM;
#if USE_ROULETTE_SELECTION
        current_paths = this->roulette_selection(current_paths, select_winners_size);
#else
        current_paths = this->rank_based_selection(current_paths, select_winners_size);
#endif // ROULETTE_SELECTION
        vector<Path> mutated_children1 = this->generate_children(current_paths);
        vector<Path> mutated_children2 = this->generate_children(current_paths);
        vector<Path> children = this->generate_children(current_paths);
        vector<Path> new_generation = this->generate_random_paths(n*NEW_RANDOM_GENERATIONS_SCALAR);

        mutate_paths(mutated_children1);
        mutate_paths(mutated_children2);

#if TEST_PRINT
        cout << "Number of winners: " << current_paths.size() << endl;
        cout << "Number of children: " << children.size() << endl;
        cout << "Number of new_generation: " << new_generation.size() << endl;
#endif // TEST_PRINT
        current_paths.insert(current_paths.end(), mutated_children1.begin(), mutated_children1.end());
        current_paths.insert(current_paths.end(), mutated_children2.begin(), mutated_children2.end());
        current_paths.insert(current_paths.end(), children.begin(), children.end());
        current_paths.insert(current_paths.end(), new_generation.begin(), new_generation.end());

        current_best_index = this->get_best_path_index(current_paths);
        cout << this->path_length(current_paths[current_best_index]) << endl;
    }

    cout << endl << this->path_length(current_paths[current_best_index]) << endl;

    return current_paths[current_best_index];
}

int main()
{
#if TEST_CITIES
    vector<string> city_names =
    {
        "Aberystwyth",
        "Brighton",
        "Edinburgh",
        "Exeter",
        "Glasgow",
        "Inverness",
        "Liverpool",
        "London",
        "Newcastle",
        "Nottingham",
        "Oxford",
        "Stratford"
    };

    vector<pair<double, double>> points =
    {
        {0.190032E-03,-0.285946E-03},
        {383.458,-0.608756E-03},
        {-27.0206,-282.758},
        {335.751,-269.577},
        {69.4331,-246.780},
        {168.521,31.4012},
        {320.350,-160.900},
        {179.933,-318.031},
        {492.671,-131.563},
        {112.198,-110.561},
        {306.320,-108.090},
        {217.343,-447.089},
    };

    TravelingSalesmanSolver solver(city_names, points);
#else
    TravelingSalesmanSolver solver(100);
#endif // TEST_CITIES

#if TEST_PRINT
    solver.print_init_info();

    vector<Path> paths = solver.generate_random_paths(3);

    Path first = paths[0];
    Path second = paths[1];
    Path third = paths[2];

    cout << endl << "First path: ";
    for (uint64_t i = 0; i < first.size(); i++)
    {
        cout << first[i] << ", ";
    }
    cout << endl << "Second path: ";
    for (uint64_t i = 0; i < second.size(); i++)
    {
        cout << second[i] << ", ";
    }
    cout << endl << "Third path: ";
    for (uint64_t i = 0; i < third.size(); i++)
    {
        cout << third[i] << ", ";
    }

    cout << endl << "PMX crossover info:";

    pair<Path, Path> children = solver.PMX_crossover(first, second);

    cout << endl << "Cross between first and second: ";
    cout << endl << "First crossover: ";
    for (uint64_t i = 0; i < children.first.size(); i++)
    {
        cout << children.first[i] << ", ";
    }
    cout << endl << "Second crossover: ";
    for (uint64_t i = 0; i < children.second.size(); i++)
    {
        cout << children.second[i] << ", ";
    }
    cout << endl << endl;

    vector<Path> all_paths = {first, second, third, children.first, children.second};
    uint64_t best_index = solver.get_best_path_index(all_paths);


    cout << "First path length: " << solver.path_length(first) << endl;
    cout << "Second path length: " << solver.path_length(second) << endl;
    cout << "Third path length: " << solver.path_length(third) << endl;
    cout << "First crossover length: " << solver.path_length(children.first) << endl;
    cout << "Second crossover length: " << solver.path_length(children.second) << endl;
    cout << "Best: " << solver.path_length(all_paths[best_index]) << endl;
    cout << endl;

    vector<Path> selected_paths = solver.rank_based_selection(all_paths, 2);

    cout << endl << "Selected paths from rank-based: ";
    cout << endl << "First (not by score): ";
    for (uint64_t i = 0; i < selected_paths[0].size(); i++)
    {
        cout << selected_paths[0][i] << ", ";
    }
    cout << endl << "Second (not by score): ";
    for (uint64_t i = 0; i < selected_paths[1].size(); i++)
    {
        cout << selected_paths[1][i] << ", ";
    }
    cout << endl;

    selected_paths = solver.roulette_selection(all_paths, 2);

    cout << endl << "Selected paths from roulette: ";
    cout << endl << "First (not by score): ";
    for (uint64_t i = 0; i < selected_paths[0].size(); i++)
    {
        cout << selected_paths[0][i] << ", ";
    }
    cout << endl << "Second (not by score): ";
    for (uint64_t i = 0; i < selected_paths[1].size(); i++)
    {
        cout << selected_paths[1][i] << ", ";
    }
    cout << endl;

    children = solver.TP_crossover(first, second);
    cout << endl << "TP crossover info:";

    cout << endl << "Cross between first and second: ";
    cout << endl << "First crossover: ";
    for (uint64_t i = 0; i < children.first.size(); i++)
    {
        cout << children.first[i] << ", ";
    }
    cout << endl << "Second crossover: ";
    for (uint64_t i = 0; i < children.second.size(); i++)
    {
        cout << children.second[i] << ", ";
    }
    cout << endl << endl;

    all_paths = {first, second, third, children.first, children.second};
    best_index = solver.get_best_path_index(all_paths);


    cout << "First path length: " << solver.path_length(first) << endl;
    cout << "Second path length: " << solver.path_length(second) << endl;
    cout << "Third path length: " << solver.path_length(third) << endl;
    cout << "First crossover length: " << solver.path_length(children.first) << endl;
    cout << "Second crossover length: " << solver.path_length(children.second) << endl;
    cout << "Best: " << solver.path_length(all_paths[best_index]) << endl;
    cout << endl;
#endif // TEST_PRINT

    Path result = solver.find_solution();

}
