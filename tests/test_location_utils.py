import pytest

from earthquake_tool.most_dangerous_regions.location_utils import get_region, get_place


def test_get_region():
    assert get_region(40.053116, -76.313603) == "US"
    assert get_region(40.053116, -76.313603, "country") == "US"
    assert get_region(40.053116, -76.313603, "state") == "PA"
    assert get_region(40.053116, -76.313603, "city") == "Lancaster"


def test_get_place():
    assert get_place("8km ENE of Eielson Air Force Base, Alaska") == "Eielson Air Force Base, Alaska"
    assert get_place("Next Door") == "Next Door"
    assert get_place("") == ""
