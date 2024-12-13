from ucimlrepo import fetch_ucirepo 
from pandas.core.frame import DataFrame
from math import log2, inf, isclose
from statistics import median, mean, stdev
from random import choice
from sklearn.model_selection import train_test_split, KFold

breast_cancer = fetch_ucirepo(id=14) 

features = breast_cancer.data.features
headers = breast_cancer.data.headers
targets = breast_cancer.data.targets

global_dataset = DataFrame(data=features, columns=headers)
global_dataset['Class'] = targets

#impute missing vals
modes = {col: global_dataset[col].mode().iloc[0] for col in global_dataset.columns if global_dataset[col].notna().any()}
global_dataset.fillna(modes, inplace=True)

class Node:
    def __init__(self, dataset: DataFrame, feature_name: str | None, class_feature_name: str):
        self.feature_name: str | None = feature_name

        self.feature_value_to_return_value: dict[str, str | None] = {}
        self.feature_value_to_child: dict[str, Node] = {} # to node

        self.is_leaf: bool = (feature_name is None)
        if feature_name == None:
            #MSS Prepruning
            self.majority_class = dataset[class_feature_name].value_counts().idxmax()
        else:
            #Normal
            self.majority_class = None
            self.feature_values = dataset[feature_name].unique()
    

# NOTE: this model won't work with inputs with number of features more than 36 since it works with recursion only, and python hard caps recursion to 36, unless modified
class ID3:
    classes: list[str]
    tree: Node
    def __init__(self, min_samples_split = -inf):
        self.min_samples_split = min_samples_split

    def train_model(self, dataset: DataFrame , class_feature_name: str):
        self.classes = list(dataset[class_feature_name].unique())
        #print(f"All classes to train model: {self.classes} to train on model")
        self.class_feature_name = class_feature_name
        self.tree: Node = self.create_tree(dataset)
        
    def create_tree(self, dataset: DataFrame):
        #MSS Prepruning
        if len(dataset) < self.min_samples_split:
            node = Node(dataset, feature_name = None, class_feature_name = self.class_feature_name)
            return node

        #Splitting
        best_feature: str = None
        best_gain: float = -inf

        for feature_name in dataset.columns:
            if feature_name == self.class_feature_name:
                continue

            result = ID3.get_information_gain_for_feature(dataset, self.class_feature_name, feature_name)

            if result > best_gain:
                best_gain = result
                best_feature = feature_name
        
        if best_gain == -inf: # Is just no entropy at all for all the values, and we haven't prepruned yet. (if there is no min_sample value given)
            node = Node(dataset, feature_name = None, class_feature_name = self.class_feature_name)
            return node
        
        node = Node(dataset, best_feature, self.class_feature_name)

        for value in node.feature_values:
            value_set: DataFrame = dataset[dataset[node.feature_name] == value]
            if len(value_set[self.class_feature_name].dropna().unique()) == 1:
                node.feature_value_to_return_value[value] = value_set[self.class_feature_name].dropna().unique()[0]
            else:
                dataset_slice: DataFrame = value_set.drop(columns=[node.feature_name])
                node.feature_value_to_child[value] = self.create_tree(dataset_slice)
        
        return node
    

    def make_prediciton(self, data_row: DataFrame | dict) -> tuple[str, bool]:
        current_node: Node = self.tree

        while current_node:
            if current_node.is_leaf:  # Leaf node due to MSS or other reasons
                return (current_node.majority_class, True)
            if current_node.feature_name not in data_row:
                print("Missing feature: " + current_node.feature_name)
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

        entropy: float = 0
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
        entropy_for_class = ID3.get_entropy_for_feature(dataset, class_feature_name)
        if isclose(entropy_for_class, 0.0):
            return -inf # obviously not best feature
        
        entropy_for_class_and_feature = ID3.get_entropy_for_two_features(dataset, class_feature_name, feature)
        return entropy_for_class - entropy_for_class_and_feature
    
    def get_right_predictions_for_set(self, dataset: DataFrame) -> int:
        count: int = 0
        for _, row in dataset.iterrows():
            prediction, _ = self.make_prediciton(row)
            count += 1 if prediction == row["Class"] else 0
        
        return count


        
X = global_dataset.drop(columns=['Class'])
y = global_dataset['Class']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y) # already coded one, no need for more

training_dataset = DataFrame(X_train)
training_dataset['Class'] = y_train

test_dataset = DataFrame(X_test)
test_dataset['Class'] = y_test

kf = KFold(n_splits=10, shuffle=True)

model_count = 0
accuracies: list = []

min_samples_split:int = 15 # getting best values with this. I guess

for train_index, validation_index in kf.split(training_dataset):
    train_fold, validation_fold = training_dataset.iloc[train_index], training_dataset.iloc[validation_index]
    model = ID3(min_samples_split = min_samples_split)
    model.train_model(train_fold, "Class")

    size: int = len(validation_fold)
    count: int = model.get_right_predictions_for_set(validation_fold)
    
    accuracy: float = (count*100)/size
    accuracies.append(accuracy)
    print(
        f"Model {model_count + 1} got accuracy: {accuracy:.2f}%"
    )
    model_count += 1

print(f"For 10 models:")
print(f"The median is {median(accuracies):.2f}%")
print(f"The mean is {mean(accuracies):.2f}%")
print(f"The standard deviation is {stdev(accuracies):.2f}%")


model = ID3(min_samples_split = min_samples_split)
model.train_model(training_dataset, "Class")
size: int = len(test_dataset)
count: int = model.get_right_predictions_for_set(test_dataset)
accuracy: float = (count*100)/size

print(
    f"\n\nModel after finished training got accuracy: {accuracy:.2f}%"
)