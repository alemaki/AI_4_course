
from typing import Optional
from pandas import DataFrame
from copy import deepcopy
import csv


FILE_PATH = "homeworks\AI_HW_5\house-votes-84.data"

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
        
    def get_model_prediciton(self, attributes: list[Optional[bool]]) -> str:


        class_evals: dict[str, int] = {}
        best_class_name: str = ""
        for class_name in self.class_names:
            chance: float = 1
            for i, attribute in enumerate(attributes):
                #total_votes_for_atr_in_class: int = self.get_attribute_total_for_class(class_name, i) #not interested now
                votes_for_atr_in_class = self.get_votes_for_attribute_for_class(class_name, i, attribute)
                if votes_for_atr_in_class == 0:
                    votes_for_atr_in_class = 1.0 # Laplace smoothing 
                votes_for_atr_in_class = float(votes_for_atr_in_class) #force float just in case
                total_classes: float = float(self.class_counter[class_name])
                chance *= votes_for_atr_in_class/total_classes
                

                





        
        
        
        

print(preprocess_data(read_data_set(FILE_PATH)))