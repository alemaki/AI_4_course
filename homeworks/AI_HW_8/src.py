from neural_network import NN
from layer import Layer, ActivationFunction


# Results
# 1. No hidden layers:
    # 1.1. Sigmoid
    # And - works good
    # Or - works good
    # Xor - doesn't seem to figure it out (probably beacause only 1 layer is linear and the function is non-linear)
    # 1.2. Tanh
    # And - Half works. Seems to struggle.
    # Or - works good
    # Xor - same as sigmoid
# 2. One hidden layer with one neuron (Expecting like none):
    # 2.1. Sigmoid
    # Same results as No layers
    # 2.2. Tanh
    # Same results as No layers except And actually is better
# 3. One hidden layer with two neurons
    # 3.1. Sigmoid
    # And - works good
    # Or - works good
    # Xor - Sometimes fully figures it out, sometimes no (mostly no)
    # seems to be slowing down, tho
    # 3.2. Tanh
    # And - works good
    # Or - works good
    # Xor - suprisingly works good
# 4. One hidden layer with three neurons
    # 4.1. Sigmoid
    # And - works good
    # Or - works good
    # Xor - works good
    # 4.2. Tanh
    # And - works good
    # Or - works good
    # Xor - works good

and_or_or_or_xor = str(input()).lower()
function = bool(input())
hidden_layers = int(input())
neuron_count_for_hidden = int(input())

function = ActivationFunction.TANH if function else ActivationFunction.SIGMOID

def fit_model(layers, x_train, y_train, str):
    model = NN(layers)
    model.fit(x_train, y_train, epochs = 10000, learning_rate = 0.05, no_print = True)
    print(f"Result for {str}")
    for _, train in enumerate(x_train):
        print(train, "->", model.get_predictions(train))

def test_and():
    layers = [Layer(2)]
    layers.extend([Layer(neuron_count_for_hidden, function) for _ in range(hidden_layers)])
    layers.append(Layer(1, function))

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

    fit_model(layers, x_train, y_train, "And")

def test_or():
    layers = [Layer(2)]
    layers.extend([Layer(neuron_count_for_hidden, function) for _ in range(hidden_layers)])
    layers.append(Layer(1, function))

    x_train = [
        [1, 1],
        [0, 1],
        [1, 0],
        [0, 0]
    ]
    y_train = [
        1,
        1,
        1,
        0
    ]

    fit_model(layers, x_train, y_train, "Or")

def test_xor():
    layers = [Layer(2)]
    layers.extend([Layer(neuron_count_for_hidden, function) for _ in range(hidden_layers)])
    layers.append(Layer(1, function))

    x_train = [
        [1, 1],
        [0, 1],
        [1, 0],
        [0, 0]
    ]
    y_train = [
        0,
        1,
        1,
        0
    ]

    fit_model(layers, x_train, y_train, "XOR")

if and_or_or_or_xor == "and":
    test_and()
elif and_or_or_or_xor == "or":
    test_or()
elif and_or_or_or_xor == "xor":
    test_xor()
elif and_or_or_or_xor == "all":
    test_and()
    test_or()
    test_xor()