import pytest
from pandas.core.frame import DataFrame
from src import Node, ID3
from math import log2

test_dataset = DataFrame(  # From presentations for testing
    data={
        "Outlook": ["Rainy", "Rainy", "Overcast", "Sunny", "Sunny", "Sunny", "Overcast", "Rainy", "Rainy", "Sunny", "Rainy", "Overcast", "Overcast", "Sunny"],
        "Temp": ["Hot", "Hot", "Hot", "Mild", "Cool", "Cool", "Cool", "Mild", "Cool", "Mild", "Mild", "Mild", "Hot", "Mild"],
        "Humidity": ["High", "High", "High", "High", "Normal", "Normal", "Normal", "High", "Normal", "Normal", "Normal", "High", "Normal", "High"],
        "Windy": [False, True, False, False, False, True, True, False, False, False, True, True, False, True],
        "Class": ["No", "No", "Yes", "Yes", "Yes", "No", "Yes", "No", "Yes", "Yes", "Yes", "Yes", "Yes", "No"],
    }
)


def test_idle():
    assert True


def test_get_p_for_feature_value():
    assert ID3.get_p_for_feature_value(test_dataset, "Class", "No") == pytest.approx(5/14)
    assert ID3.get_p_for_feature_value(test_dataset, "Class", "Yes") == pytest.approx(9/14)

    assert ID3.get_p_for_feature_value(test_dataset, "Temp", "Hot") == pytest.approx(4/14)
    assert ID3.get_p_for_feature_value(test_dataset, "Temp", "Mild") == pytest.approx(6/14)
    assert ID3.get_p_for_feature_value(test_dataset, "Temp", "Cool") == pytest.approx(4/14)

def test_get_p_for_feature_value():
    assert ID3.get_p_for_feature_value(test_dataset[test_dataset["Outlook"] == "Overcast"], "Class", "Yes") == pytest.approx(1) # from presentation
    assert ID3.get_p_for_feature_value(test_dataset[test_dataset["Outlook"] == "Overcast"], "Class", "No") == pytest.approx(0) # from presentation


def test_get_entropy_for_feature():
    entropy_for_class = ID3.get_entropy_for_feature(test_dataset, "Class")
    assert entropy_for_class == pytest.approx(0.94, 0.01) # from presentation

    entropy_for_outlook =  ID3.get_entropy_for_feature(test_dataset, "Outlook")
    test_value_outlook = - 2 * 5/14 * log2(5/14) - 4/14 * log2(4/14)
    assert entropy_for_outlook == pytest.approx(test_value_outlook)

    entropy_for_temperature =  ID3.get_entropy_for_feature(test_dataset, "Temp")
    test_value_tempreature = - 6/14 * log2(6/14) - 2 * 4/14 * log2(4/14)
    assert entropy_for_temperature == pytest.approx(test_value_tempreature)


def test_get_entropy_for_feature_no_entropy():
    entropy_for_class = ID3.get_entropy_for_feature(test_dataset[test_dataset["Outlook"] == "Overcast"], "Class")
    assert entropy_for_class == pytest.approx(0) # should be no entropy

def test_get_entropy_for_two_features():
    entropy_for_class_and_outlook = ID3.get_entropy_for_two_features(test_dataset, "Class", "Outlook")
    assert entropy_for_class_and_outlook == pytest.approx(0.693, 0.001) # from presentations

    
def test_ID3_tree_generation():
    test_model = ID3()
    test_model.train_model(test_dataset)

    tree: Node = test_model.tree

    # everything from presentations
    assert tree.feature_name == "Outlook"
    assert len(tree.feature_value_to_child.keys()) == 2
    assert len(tree.feature_value_to_return_value.keys()) == 1
    assert "Sunny" in tree.feature_value_to_child.keys()
    assert "Rainy" in tree.feature_value_to_child.keys()
    assert "Overcast" in tree.feature_value_to_return_value.keys()
    assert tree.feature_value_to_return_value["Overcast"] == "Yes"

    child1 = tree.feature_value_to_child["Sunny"]
    assert child1.feature_name == "Windy"
    assert len(child1.feature_value_to_child.keys()) == 0
    assert len(child1.feature_value_to_return_value.keys()) == 2
    assert True in child1.feature_value_to_return_value.keys()
    assert False in child1.feature_value_to_return_value.keys()
    assert child1.feature_value_to_return_value[True] == "No"
    assert child1.feature_value_to_return_value[False] == "Yes"

    child2 = tree.feature_value_to_child["Rainy"]
    assert child2.feature_name == "Humidity"
    assert len(child2.feature_value_to_child.keys()) == 0
    assert len(child2.feature_value_to_return_value.keys()) == 2
    assert "High" in child2.feature_value_to_return_value.keys()
    assert "Normal" in child2.feature_value_to_return_value.keys()
    assert child2.feature_value_to_return_value["High"] == "No"
    assert child2.feature_value_to_return_value["Normal"] == "Yes"







