#include <iostream>
#include <string>
#include <vector>
#include <random>
#include <cmath>
#include <algorithm>
#include <float.h>
#include <unordered_set>
#include <chrono>
#include <sstream>
#include <fstream>
#include <charconv>
#include <optional>

using namespace std;

typedef vector<uint64_t> Path;

/* Solution can be optimised a lot, since there is a lot of unneeded copying, but currently does the job pretty well for N <= 100, so I won't do it.*/

/* I should have f**king done this in python. */

#define TEST_PRINT 0

/* Will cross random parents if enabled, else will cross best parents.*/
#define ENABLE_RANDOM_CROSSOVER 0

/* Will use all given crossovers. Will generate more children in more crossovers are enabled.
   If none are, parents will just be copied. */
#define ENABLE_OP_CROSSOVER 1
#define ENABLE_TP_CROSSOVER 1
#define ENABLE_PMX_CROSSOVER 1
/* if 1 will use Tournament, if 0 - Rank-based*/
#define USE_TOURNAMENT_SELECTION 0

#define MUTATION_CHANCE ((double) 10/100)
/* swap mutation is always enabled */
#define ENABLE_INSERTION_MUTATION 1
#define ENABLE_REVERSE_MUTATION 1

#define GENERATIONS 10
#define ENABLE_TRUE_RANDOM 1

/* Do not edit these */
#define INITIAL_PATHS_SCALAR 600
#define SELECT_WINNERS_DELIM (ENABLE_OP_CROSSOVER + ENABLE_TP_CROSSOVER + ENABLE_PMX_CROSSOVER + 1)
#define NEW_RANDOM_GENERATIONS_SCALAR 0

#if ENABLE_TRUE_RANDOM
mt19937 rng(chrono::system_clock::now().time_since_epoch().count());
#else
random_device dev(12);
mt19937 rng(dev());
#endif // ENABLE_TRUE_RANDOM

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
    TravelingSalesmanSolver(){};
    TravelingSalesmanSolver(vector<string> point_names, vector<pair<double, double>> points);
    TravelingSalesmanSolver(uint64_t n);

    inline double get_distance(uint64_t point1_index, uint64_t point2_index) const
    {
        return get_euclidean_distance(this->points[point1_index], this->points[point2_index]);
    }

    void print_path_names(const Path& path) const;
    void print_init_info() const;
    uint64_t get_best_path_index(const vector<Path>& paths) const;
    uint64_t get_worst_path_index(const vector<Path>& paths) const;
    double path_length(const Path& path) const;
    Path generate_random_path() const;
    vector<Path> generate_random_paths(uint64_t size) const;
    vector<Path> rank_based_selection(const vector<Path>& paths, uint64_t select_size) const;
    vector<Path> tournament_selection(const vector<Path>& paths, uint64_t select_size) const;
    vector<Path> generate_children(const vector<Path>& parents) const;
    /* Partially mapped crossover */
    pair<Path, Path> PMX_crossover(const Path& parent1, const Path& parent2) const;
    /* Two point crossover */
    pair<Path, Path> TP_crossover(const Path& parent1, const Path& parent2) const;
    /* One point crossover */
    pair<Path, Path> OP_crossover(const Path& parent1, const Path& parent2) const;
    void mutate(Path& path) const;
    void mutate_paths(vector<Path>& paths) const;
    Path find_solution() const;

};

TravelingSalesmanSolver::TravelingSalesmanSolver(vector<string> point_names, vector<pair<double, double>> points) : point_names(point_names), points(points)
{}

TravelingSalesmanSolver::TravelingSalesmanSolver(uint64_t n)
{
    if (!(n > 1))
    {
        throw std::bad_alloc();
    }

    this->points.resize(n);
    this->point_names.resize(n);

    for (uint64_t i = 0; i < n; i++)
    {
        this->points[i] = {get_random_real(0, 5000),  get_random_real(0, 5000)};
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

uint64_t TravelingSalesmanSolver::get_worst_path_index(const vector<Path>& paths) const
{
    double max = this->path_length(paths[0]); // assume paths has something. xD
    uint64_t index = 0;
    for (uint64_t i = 1; i < paths.size(); i++)
    {
        double length = this->path_length(paths[i]);
        //cout << min << " > " << length << endl;
        if (length > max)
        {
            max = length;
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
        cout << this->point_names[path[i]] << " -> ";
    }
    cout << this->point_names[path[path.size() - 1]];
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


vector<Path> TravelingSalesmanSolver::tournament_selection(const vector<Path>& paths, uint64_t select_size) const
{
    vector<Path> selected_paths;
    vector<Path> copy_paths = paths;
    // assert(select_size > 0);
    uint64_t index_delim = paths.size()/select_size;

    const Path* current_path = &paths[0]; // kinda ugly, but will do
    uint64_t best_length = this->path_length(paths[0]);

    for (uint64_t i = 1; i < paths.size(); i++)
    {
        if (i % index_delim == 0)
        {
            selected_paths.push_back(*current_path);
            current_path = &paths[i];
            best_length = this->path_length(paths[i]);
        }
        else if (this->path_length(paths[i]) < best_length)
        {
            best_length = this->path_length(paths[i]);
            current_path = &paths[i];
        }
    }
    selected_paths.push_back(*current_path);
    return selected_paths;
}

vector<Path> TravelingSalesmanSolver::generate_children(const vector<Path>& parents) const
{
    vector<Path> result;
    vector<uint64_t> path_lengths(parents.size());
#if ENABLE_RANDOM_CROSSOVER
    iota(indices_for_crossover.begin(), indices_for_crossover.end(), 0);
    shuffle(indices_for_crossover.begin(), indices_for_crossover.end(), rng);
#else
    for (uint64_t i = 0; i < parents.size(); i++)
    {
        path_lengths[i] = this->path_length(parents[i]);
    }
    vector<uint64_t> indices_for_crossover = get_sorted_indices(path_lengths);
#endif // ENABLE_RANDOM_CROSSOVER

    for (uint64_t i = 0; i < indices_for_crossover.size() - 1; i += 2)
    {
        const Path& parent1 = parents[indices_for_crossover[i]];
        const Path& parent2 = parents[indices_for_crossover[i + 1]];

#if ENABLE_OP_CROSSOVER
        pair<Path, Path> op_offspring = this->OP_crossover(parent1, parent2);
        result.push_back(op_offspring.first);
        result.push_back(op_offspring.second);
#endif // ENABLE_OP_CROSSOVER

#if ENABLE_TP_CROSSOVER
        pair<Path, Path> tp_offspring = this->TP_crossover(parent1, parent2);
        result.push_back(tp_offspring.first);
        result.push_back(tp_offspring.second);
#endif // USE_TP_CROSSOVER

#if ENABLE_PMX_CROSSOVER
        pair<Path, Path> pmx_offspring = this->PMX_crossover(parent1, parent2);
        result.push_back(pmx_offspring.first);
        result.push_back(pmx_offspring.second);
#endif // USE_PMX_CROSSOVER

#if !(ENABLE_PMX_CROSSOVER || ENABLE_TP_CROSSOVER || ENABLE_OP_CROSSOVER)
        result.push_back(parent1);
        result.push_back(parent2);
#endif // not (USE_PMX_CROSSOVER || USE_TP_CROSSOVER || ENABLE_OP_CROSSOVER)
    }

    if (parents.size() % 2 == 1)  //keep copy of best parent
    {
        result.push_back(parents[indices_for_crossover[0]]);
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


pair<Path, Path> TravelingSalesmanSolver::OP_crossover(const Path& parent1, const Path& parent2) const
{
    vector<bool> placed_numbers1(parent1.size(), false);
    vector<bool> placed_numbers2(parent2.size(), false);

    pair<Path, Path> result;

    result.first.resize(parent1.size(), UINT64_MAX);
    result.second.resize(parent1.size(), UINT64_MAX);

    uint64_t end = get_random_int(0, parent1.size() - 2); /* nothing will change if equal to last. */

    for (uint64_t i = 0; i <= end; i++)
    {
        result.first[i] = parent1[i];
        result.second[i] = parent2[i];
        placed_numbers1[parent1[i]] = true;
        placed_numbers2[parent2[i]] = true;
    }

    uint64_t index = end + 1;
    for (uint64_t i = 0; i < parent1.size(); i++)
    {
        uint64_t gene = parent2[i];
        if (!placed_numbers1[gene])
        {
            result.first[index] = gene;
            placed_numbers1[gene] = true;
            index++;
        }
    }

    index = end + 1;
    for (uint64_t i = 0; i < parent2.size(); i++)
    {
        uint64_t gene = parent1[i];
        if (!placed_numbers2[gene])
        {
            result.second[index] = gene;
            placed_numbers2[gene] = true;
            index++;
        }
    }

    return result;
}

void TravelingSalesmanSolver::mutate(Path& path) const
{
    double mutation_chance = get_random_real(0, 100);
    if (mutation_chance > (MUTATION_CHANCE*100))
    {
        return;
    }

    uint64_t current_max_mutation = 1 + ENABLE_INSERTION_MUTATION + ENABLE_REVERSE_MUTATION;
    uint64_t mutation_type = get_random_int(1, current_max_mutation);
    switch (mutation_type)
    {
        case 1:
        {
            swap(path[get_random_int(0, path.size() - 1)], path[get_random_int(0, path.size() - 1)]);
            break;
        }
#if ENABLE_INSERTION_MUTATION
        case 2:
        {
            uint64_t erase_at = get_random_int(0, path.size() - 1);
            uint64_t insert_at = get_random_int(0, path.size() - 2);
            uint64_t res = path[erase_at];
            path.erase(path.begin() + erase_at);
            path.insert(path.begin() + insert_at, res);
            break;
        }
#endif // ENABLE_INSERTION_MUTATION
#if ENABLE_REVERSE_MUTATION
#if ENABLE_INSERTION_MUTATION
        case 3:
#else
        case 2:
#endif // ENABLE_INSERTION_MUTATION
        {
            uint64_t start = get_random_int(0, path.size() - 2);
            uint64_t end = get_random_int(start + 1, path.size() - 1);
            reverse(path.begin() + start, path.begin() + end + 1);
            break;
        }

#endif // ENABLE_REVERSE_MUTATION
    }
}

void TravelingSalesmanSolver::mutate_paths(vector<Path>& paths) const
{
    for (auto& path : paths)
    {
        this->mutate(path);
    }
}

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
#if USE_TOURNAMENT_SELECTION
        current_paths = this->tournament_selection(current_paths, select_winners_size);
#else
        current_paths = this->rank_based_selection(current_paths, select_winners_size);
#endif // ROULETTE_SELECTION
        vector<Path> children = this->generate_children(current_paths);
        vector<Path> new_generation = this->generate_random_paths(n*NEW_RANDOM_GENERATIONS_SCALAR);

        mutate_paths(children);

#if TEST_PRINT
        cout << "Number of winners: " << current_paths.size() << endl;
        cout << "Number of children: " << children.size() << endl;
        cout << "Number of new_generation: " << new_generation.size() << endl;
#endif // TEST_PRINT
        current_paths.insert(current_paths.end(), children.begin(), children.end());
        current_paths.insert(current_paths.end(), new_generation.begin(), new_generation.end());

        current_best_index = this->get_best_path_index(current_paths);
        cout << this->path_length(current_paths[current_best_index]) << endl;
    }

    cout << endl;
    this->print_path_names(current_paths[current_best_index]);
    cout << this->path_length(current_paths[current_best_index]) << endl;

    return current_paths[current_best_index];
}

optional<double> convert_to_number(const string& str) // python is easier :(
{
    try
    {
        size_t idx;
        double value = stod(str, &idx);

        if (idx == str.size())
        {
            return value;
        }
    } catch (const invalid_argument& e)
    {

    } catch (const out_of_range& e)
    {

    }
    return nullopt;

}

vector<string> read_CSV(const string& filename)
{
    vector<string> data;
    ifstream file(filename);

    string line;
    while (getline(file, line)) {
        vector<string> row;
        stringstream lineStream(line);
        string cell;

        while (getline(lineStream, cell, ','))
        {
            data.push_back(cell);
        }
    }

    return data;
}

vector<pair<double, double>> read_CSV_points(const string& filename)
{
    vector<pair<double, double>> points;
    ifstream file(filename);
    string line;

    while (getline(file, line))
    {
        stringstream lineStream(line);
        string cell;

        while (getline(lineStream, cell, ' '))
        {
            stringstream cellStream(cell);
            string xStr, yStr;
            if (getline(cellStream, xStr, ',') && getline(cellStream, yStr))
            {
                optional<double> xOpt = convert_to_number(xStr);
                optional<double> yOpt = convert_to_number(yStr);

                if (xOpt && yOpt)
                {
                    points.push_back({*xOpt, *yOpt});
                }
            }
        }
    }

    return points;
}

int main()
{
    string input;
    cin >> input;

    TravelingSalesmanSolver solver;

    optional<double> number = convert_to_number(input);
    if (number)
    {
        uint64_t N = *number;
        solver = TravelingSalesmanSolver(N);
    }
    else
    {
        for(char& c : input)
        {
           c = tolower(c);
        }
        vector<string> point_names = read_CSV(input + "_name.csv");
        vector<pair<double, double>> points = read_CSV_points(input + "_xy.csv");
        if (point_names.size() < 2 || points.size() < 2)
        {
            cout << "Insufficient files." << endl;
            return -1;
        }
        solver = TravelingSalesmanSolver(point_names, points);
    }


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

    selected_paths = solver.tournament_selection(all_paths, 2);

    cout << endl << "Selected paths from tournament: ";
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

    children = solver.OP_crossover(first, second);
    cout << endl << "OP crossover info:";

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

    cout << MUTATION_CHANCE << endl;
}
