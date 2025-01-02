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

    def connect_layers(self):
        assert(self.input_layer != None)
        for i, layer in enumerate(self.layers[1:]):
            layer.connect_previous_layer(self.layers[i]) # i starts with 0
            