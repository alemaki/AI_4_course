
from typing import Optional
from random import shuffle
from copy import deepcopy
from math import log, inf
from statistics import median, mean, stdev
import csv


FILE_PATH = "./house-votes-84.data" # run in the same folder

DatasetType = list[tuple[str, list[Optional[bool]]]]

def read_data_set(file_path: str) -> list[list[str]]:
    with open(file_path, newline='') as data:
        reader = csv.reader(data)
        return [row for row in reader]

def preprocess_attributes(attributes: list[str]) -> list[Optional[bool]]:
    def map_vote(vote: str) -> Optional[bool]:
        return {"y": True, "n": False}.get(vote, None)
    
    return [map_vote(vote) for vote in attributes]

def preprocess_data(data: list[list[str]]) -> DatasetType:
    
    dataset: DatasetType = [(row[0], preprocess_attributes(row[1:])) for row in data]

    return dataset

def impute_missing_values(dataset: DatasetType) -> DatasetType:
    for col in range(0, len(dataset[0][1])):
        values = [row[1][col] for row in dataset if not (row[1][col] is None)]
        mode_value = max(set(values), key=values.count) if values else None
        # print(mode_value)
        for row in dataset:
            if row[1][col] is None:
                row[1][col] = mode_value
    return dataset


def stratified_split_shuffle(dataset: DatasetType, split_index: int = 5) -> DatasetType:
    classes: set[str] = set([entry[0] for entry in dataset])
    classes_entries: list[DatasetType] = []
    result: DatasetType = []

    for class_name in classes:
        class_name_entries = [entry for entry in dataset if entry[0] == class_name]
        shuffle(class_name_entries)
        classes_entries.append(class_name_entries)

        #print(f"class \"{class_name}\" has {len(class_name_entries)} entries")
    
    for i in range(0, split_index):
        for class_index in range(0, len(classes_entries)):
            class_size = len(classes_entries[class_index])
            start: int = i*(class_size // split_index)
            end: int = (i + 1)*(class_size // split_index) if i != (split_index - 1) else class_size

            result.extend(classes_entries[class_index][start:end])
    
    return result

VotesStats = dict[str, int]

class BayesNC:

    laplace_lambda = 1

    def __init__(self):
        self.class_names: set[str] = set() # fuck this in specific
        self.attribute_counts: dict[str, dict[int, VotesStats]] = {}
        self.class_counter: dict[int] = {}
        self.dataset: DatasetType = []

    def print_information_class_counter(self):
        #df: DataFrame = DataFrame(self.class_counter_matrix, index = self.class_names)
        print(self.class_counter)

    def train_model(self, dataset: DatasetType):
        self.dataset.append(dataset)
        new_classes = set([row[0] for row in dataset]) - self.class_names
        self.class_names.update(new_classes)
        attribute_count: int = len(dataset[0][1])

        self.attribute_counts.update({
            class_name: [{"yes": 0, "no": 0, "none": 0} for _ in range(attribute_count)]
            for class_name in new_classes
        })
        self.class_counter.update({class_name: 0 for class_name in new_classes})

        for class_name, attributes in dataset:
            self.class_counter[class_name] += 1

            for i, vote in enumerate(attributes):
                if vote is None:
                    self.attribute_counts[class_name][i]["none"] += 1
                elif vote:
                    self.attribute_counts[class_name][i]["yes"] += 1
                else:
                    self.attribute_counts[class_name][i]["no"] += 1

    """ Returns number of correct and incorrect predictions. """
    def get_predictions_for_entries(self, test_entries: DatasetType) -> tuple[int, int]:
        correct_predictions = 0
        incorrect_predictions = 0
        for entry in test_entries:
            prediction = self.get_model_prediction(entry[1])
            correct_predictions += (prediction == entry[0])
            incorrect_predictions += not (prediction == entry[0])
        
        return correct_predictions, incorrect_predictions


    def get_attribute_total_for_class(self, class_name: str, attribute_index: int) -> int:
        return self.attribute_counts[class_name][attribute_index]["none"] +\
                self.attribute_counts[class_name][attribute_index]["yes"] +\
                self.attribute_counts[class_name][attribute_index]["no"]

    def get_votes_for_attribute_for_class(self, class_name: str, attribute_index: int, attribute: Optional[bool]) -> int:
        if attribute == None:
            return self.attribute_counts[class_name][attribute_index]["none"]
        elif attribute == True:
            return self.attribute_counts[class_name][attribute_index]["yes"]
        
        return self.attribute_counts[class_name][attribute_index]["no"]
        
    def get_model_prediction(self, attributes: list[Optional[bool]]) -> str:
        #class_evals: dict[str, int] = {}
        best_class_name: str = "all 0"
        best_class_chance: float = -inf
        for class_name in self.class_names:
            chance: float = log(float(self.class_counter[class_name]) / len(self.dataset))

            for i, attribute in enumerate(attributes):
                #total_votes_for_atr_in_class: int = self.get_attribute_total_for_class(class_name, i) #not interested now
                votes_for_atr_in_class = self.get_votes_for_attribute_for_class(class_name, i, attribute) + 2.0 * self.laplace_lambda # Laplace smoothing 
                total_class_votes: float = float(self.class_counter[class_name]) + self.laplace_lambda
                chance += log(votes_for_atr_in_class / total_class_votes)
            if chance > best_class_chance:
                best_class_chance = chance
                best_class_name = class_name
        return best_class_name


train_split = 5 # 80:20
fold_splits = 10 # 90:10

user_input: bool = bool(input() != "0")

read_data = read_data_set(FILE_PATH)
dataset: DatasetType = preprocess_data(read_data)

if user_input:
    impute_missing_values(dataset)
    print("imputing all possible\"?\"")
shuffled_dataset: DatasetType = stratified_split_shuffle(dataset, train_split)

train_cut: int = (len(shuffled_dataset)*(train_split - 1))//train_split # 4/5
training_set: DatasetType = shuffled_dataset[0:train_cut] # get 80%
test_set: DatasetType = shuffled_dataset[train_cut:] # get other 20%

training_set: DatasetType = stratified_split_shuffle(training_set, fold_splits) #split again into 10 parts

accuracies: list[float] = []

for fold_index in range(0, fold_splits):
    training_set_size: int = len(training_set)
    
    train_start: int = 0 if fold_index != 0 else training_set_size // fold_splits
    train_end: int = fold_index * (training_set_size // fold_splits)
    train_start2: int = (fold_index + 1) * (training_set_size // fold_splits) if fold_index != fold_splits - 1 else training_set_size
    train_end2: int = training_set_size

    train_entries = training_set[train_start:train_end] + training_set[train_start2:train_end2]
    test_entries = training_set[train_end:train_start2]

    bayes_NC = BayesNC()
    bayes_NC.train_model(train_entries)

    correct_predictions, incorrect_predictions = bayes_NC.get_predictions_for_entries(test_entries)
    total_predictions = correct_predictions + incorrect_predictions
    accuracy_percentage = (correct_predictions / total_predictions) * 100

    print(
        #f"Model {fold_index + 1} got correct: {correct_predictions}; incorrect: {incorrect_predictions}; Accuracy: {accuracy_percentage:.2f}%"
        f"Model {fold_index + 1} got accuracy: {accuracy_percentage:.2f}%"
    )

    accuracies.append(accuracy_percentage)


print(f"For {fold_splits} models:")
print(f"The median is {median(accuracies):.2f}%")
print(f"The mean is {mean(accuracies):.2f}%")
print(f"The standard deviation is {stdev(accuracies):.2f}%")

bayes_NC = BayesNC()
bayes_NC.train_model(training_set)
correct_predictions, incorrect_predictions = bayes_NC.get_predictions_for_entries(test_set)
total_predictions = correct_predictions + incorrect_predictions
accuracy_percentage = (correct_predictions / total_predictions) * 100

print(
    f"\n\nModel after finished training got correct: {correct_predictions}, incorrect: {incorrect_predictions}. Accuracy: {accuracy_percentage:.2f}%"
)