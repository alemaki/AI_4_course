from neural_network import NN
from layer import Layer, ActivationFunction

and_or_or_or_xor = "and" #str(input()).lower()
function = 0 #bool(input())
hidden_layers = 0 #int(input())
neuron_count_for_hidden = 0 #int(input())

function = ActivationFunction.TANH if function else ActivationFunction.SIGMOID

def test_and():
    layers = [Layer(2)]
    layers.extend([Layer(neuron_count_for_hidden, function)] for _ in range(hidden_layers))
    layers.append(Layer(1, function))
    model = NN(layers)

    x_train = [
        [1, 1],
        [0, 1],
        [1, 0],
        [0, 0]
    ]
    y_train = [
        1,
        0,
        0,
        0
    ]

    model.fit(x_train, y_train, epochs = 5, learning_rate = 0.1)

    print("Result for AND")
    for _, train in enumerate(x_train):
        print(train, "->", NN.get_predictions(train))



if and_or_or_or_xor == "and":
    test_and()
