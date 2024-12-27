import matplotlib.pyplot as plt
from pandas import DataFrame, concat, read_csv
from numpy import sqrt, random
from math import inf

def get_point_distance(point1: DataFrame, point2: DataFrame) -> float:
    distance = sqrt(((point1.to_numpy() - point2.to_numpy()) ** 2).sum())
    return distance

class KMeans:
    def __init__(self):
        self.k: int = -1
        self.is_k_means_pp: bool = False
        self.dataset: DataFrame = DataFrame()
        self.centroids: list[list[DataFrame]] = []
        self.assigned_cluster_points: list[list[DataFrame]] = []
        self.iteration: int = 0
        self.centroids_history = []
        self.assignments_history = []
        
        self.best_centroids: list[list[DataFrame]] = []
        self.best_assigned_cluster_points: list[list[DataFrame]] = []
        self.best_wcss: float = float('inf')

    def set_k_means_pp(self, value: bool):
        self.is_k_means_pp = value

    def set_data(self, dataset: DataFrame, k_clusters: int):
        assert(k_clusters > 0)
        self.dataset = dataset
        self.k = k_clusters
        self.iteration = 0

        self.pick_random_centroids()

    def pick_random_centroids(self):
        self.centroids = []
        if not self.is_k_means_pp:        
            for i in range(0, self.k):
                point: DataFrame = self.dataset.sample(n=1)
                self.centroids.append(point)
        else:
            first_centroid: DataFrame = self.dataset.sample(n=1)
            self.centroids.append(first_centroid)

            for _ in range(1, self.k):
                distances: list[float] = []
                for _, point in self.dataset.iterrows():
                    point: DataFrame = point.to_frame().T
                    min_distance: float = inf
                    for centroid in self.centroids:
                        distance: float = get_point_distance(centroid, point)
                        min_distance = min(min_distance, distance)
                    distances.append(min_distance**2)

                total_distance = sum(distances)
                probabilites = [distance / total_distance for distance in distances]

                next_centroid_index: int = random.choice(self.dataset.index, size=1, p=probabilites)[0]
                next_centroid = self.dataset.loc[next_centroid_index].to_frame().T
                self.centroids.append(next_centroid)



    def reset_assigned_cluster_points(self):
        self.assigned_cluster_points = [[] for _ in self.centroids]

    def assign_points_to_clusters(self):
        self.reset_assigned_cluster_points()
        

        assigned_cluster_points_temp: list[list[DataFrame]] = [[] for _ in range(self.k)]

        for _, point in self.dataset.iterrows():
            point = point.to_frame().T # points is series
            current_best_centroid_index: int = -1
            current_best_distance: float = inf
            for i, centroid in enumerate(self.centroids):
                distance: float = get_point_distance(point, centroid)
                if distance < current_best_distance:
                    current_best_centroid_index = i
                    current_best_distance = distance

            assigned_cluster_points_temp[current_best_centroid_index].append(point)

        for i in range(self.k):
            if assigned_cluster_points_temp[i]:
                self.assigned_cluster_points[i] = concat(assigned_cluster_points_temp[i], ignore_index=True)
            else:
                self.assigned_cluster_points[i] = DataFrame(columns=self.dataset.columns) 

    def update_centroids(self):
        for i, _ in enumerate(self.centroids):
            if not self.assigned_cluster_points[i].empty:
                self.centroids[i] = self.assigned_cluster_points[i].mean().to_frame().T
            else:
                # Handle empty clusters by reinitializing randomly
                self.centroids[i] = self.dataset.sample(n=1)

    def iterate(self, enable_history = True, max_iterations: int = 100, tolerance: float = 1e-4):
        for _ in range(max_iterations):
            old_centroids = [centroid.copy() for centroid in self.centroids]
            
            self.assign_points_to_clusters()
            self.update_centroids()

            if enable_history:
                self.centroids_history.append([centroid.copy() for centroid in self.centroids])
                self.assignments_history.append([cluster.copy() for cluster in self.assigned_cluster_points])

            converged = all(
                get_point_distance(old, new) < tolerance
                for old, new in zip(old_centroids, self.centroids)
            )
            if converged:
                break


    def evaluate_wcss(self) -> float: #within_cluster_square_distance
        total_wcss = 0
        for i, centroid in enumerate(self.centroids):
            cluster_points = DataFrame(self.assigned_cluster_points[i])
            if len(cluster_points) > 0:
                distances = ((cluster_points.values - centroid.values) ** 2).sum(axis=1)
                total_wcss += distances.sum()
        return total_wcss
    
    def random_restarts(self, restarts: int = 10):
        best_score = float('inf')

        for _ in range(restarts):
            self.pick_random_centroids()
            self.assign_points_to_clusters()
            self.iterate(enable_history=False)

            current_wcss = self.evaluate_wcss()

            if current_wcss < best_score:
                best_score = current_wcss
                self.best_centroids = self.centroids.copy()
                self.best_assigned_cluster_points = self.assigned_cluster_points.copy()
                self.best_wcss = current_wcss

        # Restore the best solution
        self.centroids = self.best_centroids
        self.assigned_cluster_points = self.best_assigned_cluster_points
    
def plot_kmeans_progress(kmeans_model: KMeans):
    num_iterations = len(kmeans_model.centroids_history)
    colors = ['r', 'g', 'b', 'y', 'c', 'm']  # Colors for clusters

    for i in range(num_iterations):
        plt.figure(figsize=(8, 6))
        
        for j in range(kmeans_model.k):
            cluster_points = kmeans_model.assignments_history[i][j]
            plt.scatter(cluster_points['dim1'], cluster_points['dim2'], color=colors[j % len(colors)], label=f'Cluster {j+1}')
        
        centroids = kmeans_model.centroids_history[i]
        for j, centroid in enumerate(centroids):
            plt.scatter(centroid['dim1'], centroid['dim2'], color='b', marker='X', s=100, label=f'Centroid')
        
        plt.title(f'K-Means Iteration {i + 1}')
        plt.xlabel('Dimension 1')
        plt.ylabel('Dimension 2')
        plt.legend()
        plt.show()

def plot_kmeans_result(kmeans_model: KMeans):
    plt.figure(figsize=(8, 6))
    colors = ['r', 'g', 'b', 'y', 'c', 'm', 'orange', 'purple', 'brown', 'pink', 'gray', 'lime', 'navy']  # Colors for clusters
    for j in range(kmeans_model.k):
        cluster_points = kmeans_model.assigned_cluster_points[j]
        plt.scatter(cluster_points['dim1'], cluster_points['dim2'], color=colors[j % len(colors)], label=f'Cluster {j+1}')
    
    for j, centroid in enumerate(kmeans_model.centroids):
        plt.scatter(centroid['dim1'], centroid['dim2'], color='k', marker='X', s=100, label=f'Centroid')
    
    plt.title(f'K-Means result')
    plt.xlabel('Dimension 1')
    plt.ylabel('Dimension 2')
    plt.legend()
    plt.show()


file_path = "unbalance.txt" #input()
dataset = read_csv(file_path, sep='\\s+', header=None)
dataset.columns = [f"dim{i+1}" for i in range(dataset.shape[1])]


model = KMeans()
model.set_k_means_pp(True)
model.set_data(dataset, 2)
model.random_restarts()

plot_kmeans_result(model)