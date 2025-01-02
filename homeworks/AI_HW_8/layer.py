from neuron import Neuron
from enum import Enum
from typing import Self
from random import uniform
class ActivationFunction(Enum):
    SIGMOID = 1
    TANH = 2

class Layer():
    def __init__(self,
                 neurons_count: int = 1,
                 activation_function: ActivationFunction = ActivationFunction.SIGMOID) -> None:
        self.bias: Neuron = Neuron()
        self.neurons: list[Neuron] = [Neuron() for _ in range(neurons_count)]
        self.weights: list[list[float]] = None  # weights to calculate from previous layer
        self.activation_function: ActivationFunction = activation_function

    def set_activation_function(self, fn: ActivationFunction):
        self.activation_function = fn

    def connect_previous_layer(self, other_layer: Self) -> None:
        self.weights = [[uniform(0.0, 1.0) for _ in other_layer.neurons] for _ in self.neurons]

        
