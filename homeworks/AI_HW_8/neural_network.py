from neuron import Neuron
from layer import Layer
from copy import deepcopy

class NN():
    def __init__(self, layers: list[Layer] = []) -> None:
        self.input_layer: Layer = None
        self.output_layer: Layer = None
        self.layers: list[Layer] = deepcopy(layers)
        if len(self.layers) > 0: 
            self.input_layer = self.layers[1]
            self.out_layer = self.layers[-1]

        self.connect_layers()

    def connect_layers(self) -> None:
        assert self.input_layer is not None
        for i, layer in enumerate(self.layers[1:]):
            layer.connect_previous_layer(self.layers[i]) # i starts with 0
    
    """Returns index of neuron and value of prediction"""
    def predict(self, value_list: list[float]) -> tuple[int, float]:
        self.input_layer.set_values(value_list)
        for i, layer in enumerate(self.layers[1:]):
            prev_values: list[float] = self.layers[i].get_values()
            layer.calculate_neuron_values(prev_values)
        

        output_values = self.output_layer.get_values()
    
        if len(output_values) == 1:
            return (0, output_values[0])

        value = max(output_values)
        return (output_values.index(value), value)