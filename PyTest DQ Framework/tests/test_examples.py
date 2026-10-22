"""Small, database-free examples of the reusable DQ assertion API."""

import pandas as pd
import pytest


@pytest.mark.example
def test_example_count_and_completeness(data_quality_library):
    expected = pd.DataFrame({"id": [1, 2], "label": ["a", "b"]})
    actual = pd.DataFrame({"label": ["b", "a"], "id": [2, 1]})

    data_quality_library.check_count(expected, actual)
    data_quality_library.check_data_completeness(expected, actual)


@pytest.mark.example
def test_example_not_null_and_unique(data_quality_library):
    frame = pd.DataFrame({"id": [1, 2], "label": ["a", "b"]})

    data_quality_library.check_duplicates(frame, ["id"])
    data_quality_library.check_not_null_values(frame, ["id", "label"])
