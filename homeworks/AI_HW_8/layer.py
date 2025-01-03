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
        self.errors = None
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
        
    def calculate_neuron_values(self, previous_neuron_values: list[float]) -> None:
        assert self.weights is not None
        assert len(previous_neuron_values) == len(self.weights[0])

        input_values: np.NDArray = np.array(previous_neuron_values)
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

    """ """
    def _get_derivative_for_neuron(self, neuron_index: int) -> None:
        if self.activation_function == ActivationFunction.SIGMOID:
            return self.neurons[neuron_index].value * (1 - self.neurons[neuron_index].value)
        elif self.activation_function == ActivationFunction.TANH:
            return (1 - self.neurons[neuron_index].value**2)
        raise ValueError("Unsupported activation function.")

    def backpropagate_output_layer(self, output_errors: list[float], previous_layer: Self, learning_rate: float) -> None:
        assert len(output_errors) == len(self.neurons)
        for i, _ in enumerate(self.neurons):
            delta = output_errors[i]*self._get_derivative_for_neuron(i)
            for j, _ in enumerate(self.weights[i]):
                self.weights[i][j] -= learning_rate * delta * previous_layer.neurons[j].value
            self.biases[i] -= learning_rate * delta
        self.errors = output_errors

    def backpropagate_layer(self, previous_layer: Self, next_layer: Self, learning_rate: float) -> None:
        assert next_layer.errors is not None
        updated_errors = [0.0] * len(self.neurons)
        for i, _ in enumerate(self.neurons):
            delta = sum(next_layer.weights[j][i] * next_layer.errors[j] for j in range(len(next_layer.neurons)))
            updated_errors[i] = delta
            delta *= self._get_derivative_for_neuron(i)
            for j, _ in enumerate(self.weights[i]):
                self.weights[i][j] -= learning_rate * delta * previous_layer.neurons[j].value
            self.biases[i] -= learning_rate * delta
        
        self.errors = updated_errors