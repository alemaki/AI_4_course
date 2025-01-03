from neuron import Neuron
from layer import Layer
from copy import deepcopy
import numpy as np

class NN():
    def __init__(self, layers: list[Layer] = []) -> None:
        self.input_layer: Layer = None
        self.output_layer: Layer = None
        self.layers: list[Layer] = deepcopy(layers)
        if len(self.layers) > 0: 
            self.input_layer = self.layers[0]
            self.output_layer = self.layers[-1]
            self.model_type = "single" if len(self.output_layer.neurons) == 1 else "multiple"

        self.connect_layers()
    def connect_layers(self) -> None:
        assert self.input_layer is not None
        for i, layer in enumerate(self.layers[1:]):
            layer.connect_previous_layer(self.layers[i]) # i starts with 0
    
    def get_predictions(self, value_list: list[float]) -> list[float]:
        self.input_layer.set_values(value_list)
        for i, layer in enumerate(self.layers[1:]):
            prev_values: list[float] = self.layers[i].get_values()
            layer.calculate_neuron_values(prev_values)
        

        output_values = self.output_layer.get_values()
        return output_values
    
    def get_output_values_error(self, predictions: list[float], class_index: float) -> list[float]:
        predictions = deepcopy(predictions)
        if self.model_type == "single": # TODO: a bit unclean way to check.
            predictions[0] -= class_index
        else:
            predictions[class_index] -= 1
        return predictions
    
    def get_single_value_loss(prediction: float, should_be_value: float) -> float:
        return (prediction - should_be_value)**2

    def get_multiple_values_loss(predictions: list[float], class_index: float) -> float:
        predictions = deepcopy(predictions)
        predictions[class_index] -= 1
        return sum(map(lambda i: i * i, predictions))

    def calculate_loss(self, predictions: list[float], class_index: float) -> float:
        if self.model_type == "single": # TODO: a bit unclean way to check.
            loss = NN.get_single_value_loss(predictions[0], class_index)
        else:
            loss = NN.get_multiple_values_loss(predictions, class_index)
        return loss/2
    
    def fit(self, x_train: np.ndarray, 
            y_train: np.ndarray, 
            epochs: int = 1, 
            learning_rate: float = 0.01, 
            no_print = False)  -> None:
        if isinstance(x_train, np.ndarray):
            x_train = x_train.tolist()
        if isinstance(y_train, np.ndarray):
            y_train = y_train.tolist()


        for epoch in range(epochs):
            total_loss = 0
            for i, values in enumerate(x_train):
                class_index = y_train[i]
                predictions = self.get_predictions(values)
                loss = self.calculate_loss(predictions, class_index)
                total_loss += loss
                self.backpropagate(predictions, class_index, learning_rate)
            if not no_print:
                print(f"Epoch {epoch + 1}/{epochs}, Loss: {total_loss / len(x_train)}")

    def backpropagate(self, predictions: list[float], class_index: int, learning_rate: float) -> None:
        output_errors = self.get_output_values_error(predictions, class_index)

        self.output_layer.backpropagate_output_layer(output_errors, self.layers[-2], learning_rate)

        for l in range(len(self.layers) - 2, 0, -1):
            layer = self.layers[l]
            next_layer = self.layers[l + 1]
            previous_layer = self.layers[l - 1]
            
            output_errors = layer.backpropagate_layer(previous_layer, next_layer, learning_rate)
