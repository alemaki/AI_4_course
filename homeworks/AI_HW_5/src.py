
from typing import Optional
from pandas import DataFrame
from copy import deepcopy
from math import log, inf
import csv


FILE_PATH = "homeworks/AI_HW_5/house-votes-84.data"

def read_data_set(file_path: str) -> list[list[str]]:
    with open(file_path, newline='') as data:
        reader = csv.reader(data)
        return [row for row in reader]

def preprocess_attributes(attributes: list[str]) -> list[Optional[bool]]:
    def map_vote(vote: str) -> Optional[bool]:
        return {"y": True, "n": False}.get(vote, None)
    
    return [map_vote(vote) for vote in attributes]

def preprocess_data(data: list[list[str]]) -> list[tuple[str, list[Optional[bool]]]]:
    
    dataset: list[tuple[str, list[Optional[bool]]]] = [(row[0], preprocess_attributes(row[1:])) for row in data]

    return dataset

VotesStats = dict[str, int]

class BayesNC:
    def __init__(self):
        self.dataset_rows: int
        self.class_names: list[str]
        self.attribute_counts: dict[str, dict[int, VotesStats]]
        self.class_counter: dict[int]
        self.dataset: list[tuple[str, list[Optional[bool]]]]

    def print_information_class_counter(self):
        #df: DataFrame = DataFrame(self.class_counter_matrix, index = self.class_names)
        print(self.class_counter)

    def train_model(self, dataset: list[tuple[str, list[Optional[bool]]]]):
        self.dataset = deepcopy(dataset)
        self.dataset_rows = len(dataset)
        self.class_names = list(set(row[0] for row in dataset))
        attribute_count: int = len(dataset[0][1])

        self.attribute_counts = {
            class_name: [{"yes": 0, "no": 0, "none": 0} for _ in range(attribute_count)]
            for class_name in self.class_names
        }
        self.class_counter = {class_name: 0 for class_name in self.class_names}

        for class_name, attributes in dataset:
            self.class_counter[class_name] += 1

            for i, vote in enumerate(attributes):
                if vote is None:
                    self.attribute_counts[class_name][i]["none"] += 1
                elif vote:
                    self.attribute_counts[class_name][i]["yes"] += 1
                else:
                    self.attribute_counts[class_name][i]["no"] += 1

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
            chance: float = log(float(self.class_counter[class_name]) / self.dataset_rows)

            for i, attribute in enumerate(attributes):
                #total_votes_for_atr_in_class: int = self.get_attribute_total_for_class(class_name, i) #not interested now
                votes_for_atr_in_class = self.get_votes_for_attribute_for_class(class_name, i, attribute) + 2.0 # Laplace smoothing 
                total_class_votes: float = float(self.class_counter[class_name]) + 1.0
                chance += log(votes_for_atr_in_class / total_class_votes)
            if chance > best_class_chance:
                best_class_chance = chance
                best_class_name = class_name
        return best_class_name
                

read_data = read_data_set(FILE_PATH)
dataset: list[tuple[str, list[bool | None]]] = preprocess_data(read_data)



for fold_index in range(0, 10):
    dataset_size: int = len(dataset)
    first_train_start: int = 0 if fold_index != 0 else dataset_size // 10
    first_train_end: int = fold_index * (dataset_size // 10)
    second_train_start: int = (fold_index + 1) * (dataset_size // 10) if fold_index != 9 else dataset_size
    second_train_end: int = dataset_size

    test_start = first_train_end
    test_end = second_train_start

    if second_train_start == dataset_size:  # Last fold
        train_entries = dataset[first_train_start:first_train_end]
    else:
        train_entries = dataset[first_train_start:first_train_end] + dataset[second_train_start:second_train_end]

    test_entries = dataset[test_start:test_end]

    bayes_NC = BayesNC()
    bayes_NC.train_model(train_entries)

    correct_predictions = 0
    incorrect_predictions = 0
    for entry in test_entries:
        prediction = bayes_NC.get_model_prediction(entry[1])
        correct_predictions += (prediction == entry[0])
        incorrect_predictions += not (prediction == entry[0])

    total_predictions = correct_predictions + incorrect_predictions
    accuracy_percentage = (correct_predictions / total_predictions) * 100

    print(
        f"Model number {fold_index} got correct: {correct_predictions}, incorrect: {incorrect_predictions}\n",
        f"accuracy: {accuracy_percentage:.2f}%"
    )


    
