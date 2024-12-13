import pytest
from pandas.core.frame import DataFrame
from src import Node, ID3
from math import log2, inf
from copy import deepcopy
test_dataset = DataFrame(  # From presentations for testing
    data={
        "Outlook": ["Rainy", "Rainy", "Overcast", "Sunny", "Sunny", "Sunny", "Overcast", "Rainy", "Rainy", "Sunny", "Rainy", "Overcast", "Overcast", "Sunny"],
        "Temp": ["Hot", "Hot", "Hot", "Mild", "Cool", "Cool", "Cool", "Mild", "Cool", "Mild", "Mild", "Mild", "Hot", "Mild"],
        "Humidity": ["High", "High", "High", "High", "Normal", "Normal", "Normal", "High", "Normal", "Normal", "Normal", "High", "Normal", "High"],
        "Windy": [False, True, False, False, False, True, True, False, False, False, True, True, False, True],
        "PlayGolf": ["No", "No", "Yes", "Yes", "Yes", "No", "Yes", "No", "Yes", "Yes", "Yes", "Yes", "Yes", "No"],
    }
)


def test_idle():
    assert True


def test_get_p_for_feature_value():
    assert ID3.get_p_for_feature_value(test_dataset, "PlayGolf", "No") == pytest.approx(5/14)
    assert ID3.get_p_for_feature_value(test_dataset, "PlayGolf", "Yes") == pytest.approx(9/14)

    assert ID3.get_p_for_feature_value(test_dataset, "Temp", "Hot") == pytest.approx(4/14)
    assert ID3.get_p_for_feature_value(test_dataset, "Temp", "Mild") == pytest.approx(6/14)
    assert ID3.get_p_for_feature_value(test_dataset, "Temp", "Cool") == pytest.approx(4/14)

def test_get_p_for_feature_value():
    assert ID3.get_p_for_feature_value(test_dataset[test_dataset["Outlook"] == "Overcast"], "PlayGolf", "Yes") == pytest.approx(1) # from presentation
    assert ID3.get_p_for_feature_value(test_dataset[test_dataset["Outlook"] == "Overcast"], "PlayGolf", "No") == pytest.approx(0) # from presentation


def test_get_entropy_for_feature():
    entropy_for_PlayGolf = ID3.get_entropy_for_feature(test_dataset, "PlayGolf")
    assert entropy_for_PlayGolf == pytest.approx(0.94, 0.01) # from presentation

    entropy_for_outlook =  ID3.get_entropy_for_feature(test_dataset, "Outlook")
    test_value_outlook = - 2 * 5/14 * log2(5/14) - 4/14 * log2(4/14)
    assert entropy_for_outlook == pytest.approx(test_value_outlook)

    entropy_for_temperature =  ID3.get_entropy_for_feature(test_dataset, "Temp")
    test_value_tempreature = - 6/14 * log2(6/14) - 2 * 4/14 * log2(4/14)
    assert entropy_for_temperature == pytest.approx(test_value_tempreature)


def test_get_entropy_for_feature_no_entropy():
    entropy_for_PlayGolf = ID3.get_entropy_for_feature(test_dataset[test_dataset["Outlook"] == "Overcast"], "PlayGolf")
    assert entropy_for_PlayGolf == pytest.approx(0) # should be no entropy

def test_get_entropy_for_two_features():
    entropy_for_PlayGolf_and_outlook = ID3.get_entropy_for_two_features(test_dataset, "PlayGolf", "Outlook")
    assert entropy_for_PlayGolf_and_outlook == pytest.approx(0.693, 0.001) # from presentations

def test_information_gain_for_feature():
    information_gain_for_outlook = ID3.get_information_gain_for_feature(test_dataset, "PlayGolf", "Outlook")
    information_gain_for_temp = ID3.get_information_gain_for_feature(test_dataset, "PlayGolf", "Temp")
    information_gain_for_humidity = ID3.get_information_gain_for_feature(test_dataset, "PlayGolf", "Humidity")
    information_gain_for_windy = ID3.get_information_gain_for_feature(test_dataset, "PlayGolf", "Windy")

    # all from presentations
    assert information_gain_for_outlook == pytest.approx(0.247, 0.01)
    assert information_gain_for_temp == pytest.approx(0.029, 0.01)
    assert information_gain_for_humidity == pytest.approx(0.152, 0.01)
    assert information_gain_for_windy == pytest.approx(0.048, 0.01)

def test_information_gain_for_feature_with_no_entropy():
    test_dataset_slice = test_dataset[test_dataset["Outlook"] == "Overcast"]
    information_gain_for_temp = ID3.get_information_gain_for_feature(test_dataset_slice, "PlayGolf", "Temp")
    information_gain_for_humidity = ID3.get_information_gain_for_feature(test_dataset_slice, "PlayGolf", "Humidity")
    information_gain_for_windy = ID3.get_information_gain_for_feature(test_dataset_slice, "PlayGolf", "Windy")

    # all from presentations
    assert information_gain_for_temp == -inf
    assert information_gain_for_humidity == -inf
    assert information_gain_for_windy == -inf


def assert_normal_tree_root(tree: Node): # for reuse later
    assert tree.feature_name == "Outlook"
    assert len(tree.feature_value_to_child) == 2
    assert len(tree.feature_value_to_return_value) == 1
    assert "Sunny" in tree.feature_value_to_child
    assert "Rainy" in tree.feature_value_to_child
    assert "Overcast" in tree.feature_value_to_return_value
    assert tree.feature_value_to_return_value["Overcast"] == "Yes"

def assert_normal_rainy_node(rainy_node: Node):
    assert rainy_node.feature_name == "Humidity"
    assert len(rainy_node.feature_value_to_child) == 0
    assert len(rainy_node.feature_value_to_return_value) == 2
    assert "High" in rainy_node.feature_value_to_return_value
    assert "Normal" in rainy_node.feature_value_to_return_value
    assert rainy_node.feature_value_to_return_value["High"] == "No"
    assert rainy_node.feature_value_to_return_value["Normal"] == "Yes"

def test_ID3_tree_generation():
    test_model = ID3()
    test_model.train_model(test_dataset, "PlayGolf")
    tree: Node = test_model.tree

    # everything from presentations
    assert_normal_tree_root(tree)

    child1 = tree.feature_value_to_child["Sunny"]
    assert child1.feature_name == "Windy"
    assert len(child1.feature_value_to_child) == 0
    assert len(child1.feature_value_to_return_value) == 2
    assert True in child1.feature_value_to_return_value
    assert False in child1.feature_value_to_return_value
    assert child1.feature_value_to_return_value[True] == "No"
    assert child1.feature_value_to_return_value[False] == "Yes"

    child2 = tree.feature_value_to_child["Rainy"]
    assert_normal_rainy_node(child2)


def test_ID3_predictions():
    test_model = ID3()
    test_model.train_model(test_dataset, "PlayGolf")

    # should not make random predictions
    for _, row in test_dataset.iterrows():
        assert test_model.make_prediciton(row) == (row["PlayGolf"], True)


def test_ID3_random_predictions():
    test_model = ID3()
    test_model.train_model(test_dataset, "PlayGolf")
    
    assert test_model.make_prediciton({"Outlook": "idk"}) [1] ==  False
    assert test_model.make_prediciton({"Outlook": "something else"}) [1] ==  False


def test_ID3_one_prepruning():
    # insert Rainy day so the ID3 only has to split Sunny attribute, because they
    # normally get 5 rows each, and both will split. Which we don't need for the first test
    modified_test_dataset = deepcopy(test_dataset)
    modified_test_dataset.loc[len(test_dataset)] = ['Rainy', "Mild", 'Normal', False, "Yes"] 
    test_model = ID3(min_samples_split = 6)
    test_model.train_model(modified_test_dataset, "PlayGolf")

    tree: Node = test_model.tree

    assert_normal_tree_root(tree)

    child1 = tree.feature_value_to_child["Sunny"] # sunny should not be split now
    assert child1.feature_name is None
    assert len(child1.feature_value_to_child) == 0
    assert len(child1.feature_value_to_return_value) == 0
    assert child1.majority_class == "Yes"

    child2 = tree.feature_value_to_child["Rainy"]
    assert_normal_rainy_node(child2) # Rainy should be split as normal


def test_ID3_one_prepruning_predictions():
    # Same as previous test
    modified_test_dataset = deepcopy(test_dataset)
    modified_test_dataset.loc[len(test_dataset)] = ['Rainy', "Mild", 'Normal', False, "Yes"] 
    test_model = ID3(min_samples_split = 6)
    test_model.train_model(modified_test_dataset, "PlayGolf")

    for _, row in test_dataset.iterrows():
        if row["Outlook"] == "Sunny":
            assert test_model.make_prediciton(row) == ("Yes", True) # should always be yes for sunny because of pruning
        else:
            assert test_model.make_prediciton(row) == (row["PlayGolf"], True)

def test_ID3_all_prepruning():
    # Now we let rainy be normal so it won't split and will be a leaf.
    test_model = ID3(min_samples_split = 6)
    test_model.train_model(test_dataset, "PlayGolf")

    tree: Node = test_model.tree

    assert_normal_tree_root(tree)

    child1 = tree.feature_value_to_child["Sunny"]
    assert child1.feature_name is None
    assert len(child1.feature_value_to_child) == 0
    assert len(child1.feature_value_to_return_value) == 0
    assert child1.majority_class == "Yes"

    child2 = tree.feature_value_to_child["Rainy"] # rainy should not be split now
    assert child2.feature_name is None
    assert len(child2.feature_value_to_child) == 0
    assert len(child2.feature_value_to_return_value) == 0
    assert child2.majority_class == "No"

def test_ID3_all_prepruning_predictions():
    test_model = ID3(min_samples_split = 6)
    test_model.train_model(test_dataset, "PlayGolf")

    for _, row in test_dataset.iterrows():
        if row["Outlook"] == "Sunny":
            assert test_model.make_prediciton(row) == ("Yes", True)
        elif row["Outlook"] == "Rainy":
            assert test_model.make_prediciton(row) == ("No", True)
        else:
            assert test_model.make_prediciton(row) == (row["PlayGolf"], True)