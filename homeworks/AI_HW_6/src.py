from ucimlrepo import fetch_ucirepo 
from pandas.core.frame import DataFrame
from copy import deepcopy
from math import log2, inf
from random import choice
breast_cancer = fetch_ucirepo(id=14) 

features = breast_cancer.data.features
headers = breast_cancer.data.headers
targets = breast_cancer.data.targets

dataset = DataFrame(data=features, columns=headers)
dataset['Class'] = targets

class Node:
    def __init__(self, dataset: DataFrame, feature_name: str):
        self.feature_name: str = feature_name
        self.feature_values = dataset[feature_name].unique()
        self.feature_value_to_child: dict[str, Node] = {}
        self.feature_value_to_return_value: dict[str, str | None] = {}
    

# NOTE: this model won't work with inputs with number of features more than 36 since it works with recursion only, and python hard caps recursion to 36, unless modified
class ID3:
    classes: list[str]
    tree: Node

    def train_model(self, dataset: DataFrame):
        self.classes = list(dataset['Class'].unique())
        print(f"All classes to train model: {self.classes} to train on model")

        self.class_feature_name = "Class" #always

        self.tree: Node = self.create_tree(dataset)
        
    def create_tree(self, dataset: DataFrame):
        best_feature: str = None
        best_gain: float = -inf

        class_feature_name = "Class" #always

        for feature_name in dataset.columns:
            if feature_name == class_feature_name:
                continue

            result = self.get_information_gain_for_feature(dataset, class_feature_name, feature_name)

            if result > best_gain:
                best_gain = result
                best_feature = feature_name
        
        node = Node(dataset, best_feature)

        for value in node.feature_values:
            value_set: DataFrame = dataset[dataset[node.feature_name] == value]
            if len(value_set[class_feature_name].unique()) == 1:
                node.feature_value_to_return_value[value] = value_set[class_feature_name].unique()[0]
            else:
                dataset_slice = dataset[dataset[node.feature_name] == value]
                #dataset_slice = deepcopy(dataset_slice) # just in case
                dataset_slice = dataset_slice.drop(columns=[node.feature_name])
                node.feature_value_to_child[value] = self.create_tree(dataset_slice)
        
        return node
    

    def make_prediciton(self, data_row: DataFrame | dict) -> tuple[str, bool]:
        current_node = self.tree

        while True:
            if current_node.feature_name not in data_row:
                print("Missing feature :" + current_node.feature_name)
                break
            feature_value = data_row[current_node.feature_name]
            if feature_value in current_node.feature_value_to_child:
                current_node = current_node.feature_value_to_child[feature_value]
            elif feature_value in current_node.feature_value_to_return_value:
                return (current_node.feature_value_to_return_value[feature_value], True)
            else:
                break

        return (choice(self.classes), False)

    @staticmethod
    def get_p_for_feature_value(dataset: DataFrame, feature: str, value: str) -> float:
        size: int = len(dataset)
        assert(size != 0)
        occurrences: int = len(dataset[dataset[feature] == value])
        p: float = (occurrences / size)

        return p
    
    @staticmethod
    def get_entropy_for_feature(dataset: DataFrame, feature: str) -> float:
        feature_values = dataset[feature].unique()

        entropy: float = 0.0
        for feature_value in feature_values:
            p = ID3.get_p_for_feature_value(dataset, feature, feature_value)
            entropy -= p*log2(p)
        
        return entropy
    
    @staticmethod
    def get_entropy_for_two_features(dataset: DataFrame, class_feature_name: str, feature: str) -> float:
        classes = dataset[class_feature_name].unique()
        feature_values = dataset[feature].unique()
        result_entropy: float = 0.0

        for feature_value in feature_values:

            feature_entropy_in_class_name: float = 0.0
            p_feature: float = ID3.get_p_for_feature_value(dataset, feature, feature_value)
            for class_name in classes:
                p_class_feature: float = ID3.get_p_for_feature_value(dataset[dataset[feature] == feature_value], class_feature_name, class_name)
                if p_class_feature != 0:
                    feature_entropy_in_class_name -= p_class_feature*log2(p_class_feature)
            
            result_entropy += p_feature*feature_entropy_in_class_name
        
        return result_entropy

    @staticmethod
    def get_information_gain_for_feature(dataset: DataFrame, class_feature_name: str, feature: str) -> float:
        return ID3.get_entropy_for_feature(dataset, class_feature_name) - ID3.get_entropy_for_two_features(dataset, class_feature_name, feature)
    


model = ID3()
#model.train_model(dataset)

        
    