
from typing import Optional
from pandas import DataFrame
from copy import deepcopy
import csv


FILE_PATH = "homeworks\AI_HW_5\house-votes-84.data"

def read_data_set(file_path: str) -> list[list[str]]:
    with open(file_path, newline='') as data:
        reader = csv.reader(data)
        return [row for row in reader]


def preprocess_data(data: list[list[str]]) -> list[tuple[str, list[Optional[bool]]]]:
    def map_vote(vote: str) -> Optional[bool]:
        return {"y": True, "n": False}.get(vote, None)
    
    dataset: list[tuple[str, list[Optional[bool]]]] = [(row[0], [map_vote(vote) for vote in row[1:]]) for row in data]

    return dataset

VotesStats = dict[str, int]

class BayesNC:
    def __init__(self):
        self.dataset_rows: int
        self.main_classes: list[str]
        self.attribute_counts: dict[str, dict[int, VotesStats]]
        self.class_counter: dict[int]
        self.dataset: list[tuple[str, list[Optional[bool]]]]

    def print_information_class_counter(self):
        #df: DataFrame = DataFrame(self.class_counter_matrix, index = self.main_classes)
        print(self.class_counter)

    def train_model(self, dataset: list[tuple[str, list[Optional[bool]]]]):
        self.dataset = deepcopy(dataset)
        self.dataset_rows = len(dataset)
        self.main_classes = list(set(row[0] for row in dataset))
        attribute_count: int = len(dataset[0][1])

        self.attribute_counts = {
            class_name: [{"yes": 0, "no": 0, "none": 0} for _ in range(attribute_count)]
            for class_name in self.main_classes
        }
        self.class_counter = {class_name: 0 for class_name in self.main_classes}

        for class_name, attributes in dataset:
            self.class_counter[class_name] += 1

            for i, vote in enumerate(attributes):
                if vote is None:
                    self.attribute_counts[class_name][i]["none"] += 1
                elif vote:
                    self.attribute_counts[class_name][i]["yes"] += 1
                else:
                    self.attribute_counts[class_name][i]["no"] += 1


        
    






        
        
        
        

print(preprocess_data(read_data_set(FILE_PATH)))