#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>
#include <random>
#include <math>

using namespace std;

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

inline double get_distance(double x1, double y1, double x2, double y2)
{
    return sqrt((x1 - x2)*(x1 - x2) + (y1 - y2)*(y1 - y2));
}


class TravelingSalesmanSolver
{
    vector<string> points;
    unordered_map<string, unordered_map<string, double>> distances;


public:
    TravelingSalesmanSolver()
    {}
    TravelingSalesmanSolver(vector<string> points, unordered_map<string, unordered_map<string, double>> distances) : points(points), distances(distances)
    {}
    TravelingSalesmanSolver(int64_t n)
    {
        if (!((n > 0) && (n <= 100)))
        {
            throw "Bad n error";
        }


        vector<pair<double, double>> real_points(n);
        this->points.reserve(n);

        for (int64_t i = 0; i < n; i++)
        {
            real_points[i] = {get_random_real0, 500),  get_random_real(0, 500)};
            string point = "(" + to_string(real_points[i].first) + ", " + to_string(real_points[i].second) + ")";
            this->points.push_back(move(point));
        }

        for (int64_t i = 0; i < n; i++)
        {
             for (int64_t j = i + 1; j < n; j++)
             {
                 double distance = get_distance(real_points[i].first,
                                                real_points[i].second,
                                                real_points[j].first,
                                                real_points[j].second);
                 this->distances[this->points[i]][this->points[j]] = distance;
                 this->distances[this->points[j]][this->points[i]] = distance;
             }
        }

        print_init_info();
    }

    void print_init_info()
    {
        cout << "points: " << endl;
        for (const string& point : this->points)
        {
            cout << point << " ";
        }
        cout << endl;

        for (const string& point1 : this->points)
        {
            if (!(distances.contains(point1)))
            {
                continue;
            }
            for (const string& point2 : this->points)
            {
                if (!(distances[point1].contains(point2)))
                {
                    continue;
                }
                cout << point1 << " to " << point2 << " :" << distances[point1][point2] << endl;
            }
        }
    }

};
