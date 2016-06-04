import pytest

from earthquake_tool.most_dangerous_regions.logarithmic_utils import sum_logscale_list


def test_sum_logscale_list():
    assert sum_logscale_list([0]) == 0
    assert sum_logscale_list([5]) == 5
    assert sum_logscale_list([5, 6]) == 6.041392685158225
