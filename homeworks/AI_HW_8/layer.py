from neuron import Neuron
from enum import Enum
from typing import Self
from random import uniform
import numpy as np

class ActivationFunction(Enum):
    SIGMOID = 1
    TANH = 2

class Layer():
    def __init__(self,
                 neurons_count: int = 1,
                 activation_function: ActivationFunction = ActivationFunction.SIGMOID) -> None:
        assert neurons_count > 0
        self.neurons: list[Neuron] = [Neuron() for _ in range(neurons_count)]
        self.weights: list[list[float]] = None  # weights to calculate from previous layer
        self.activation_function: ActivationFunction = activation_function
        self.biases: list[float] = [uniform(0.0, 1.0) for _ in range(neurons_count)]
        #self.bias: Neuron = Neuron() #deprecated

    def set_activation_function(self, fn: ActivationFunction):
        self.activation_function = fn

    def connect_previous_layer(self, other_layer: Self) -> None:
        self.weights = [[uniform(0.0, 1.0) for _ in other_layer.neurons] for _ in self.neurons]
    
    def set_values(self, values: list[float]) -> None:
        assert len(values) == len(self.neurons)
        for i, value in enumerate(values):
            self.neurons[i].value = value

    def get_values(self) -> list[float]:
        return [neuron.value for neuron in self.neurons]
        
    def calculate_neuron_values(self, values: list[float]) -> None:
        assert self.weights is not None
        assert len(values) == len(self.weights[0])

        input_values: np.NDArray = np.array(values)
        weights: np.NDArray = np.array(self.weights)
        weighted_sum = np.dot(weights, input_values)

        weighted_sum += self.biases

        if self.activation_function == ActivationFunction.SIGMOID:
            activated_values = 1 / (1 + np.exp(-weighted_sum))
        elif self.activation_function == ActivationFunction.TANH:
            activated_values = np.tanh(weighted_sum)
        else:
            raise ValueError("Unsupported activation function.")

        for i, neuron in enumerate(self.neurons):
            neuron.value = activated_values[i]