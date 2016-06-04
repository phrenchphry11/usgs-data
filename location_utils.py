import re

import requests

MAPQUEST_API_KEY = "DpKvbEmBaeQ1oqc5Jea24RxCL6oh560e"

REGION_TYPE_TO_ADMIN_AREA = {
    "country": "adminArea1",
    "state": "adminArea3",
    "city": "adminArea5",
}


def get_region(latitude, longitude, region_type="country"):
    """
    Returns either a country, state, or city containing the latitude and longitude provided,
    via the MapQuest API.
    Returns None if there is no match.
    """
    if region_type not in REGION_TYPE_TO_ADMIN_AREA.keys():
        raise Exception("Not a valid region type:{}".format(region_type))

    admin_area = REGION_TYPE_TO_ADMIN_AREA.get(region_type)
    response = requests.get("http://www.mapquestapi.com/geocoding/v1/reverse?key={}&"
        "location={},{}".format(MAPQUEST_API_KEY, latitude, longitude))
    try:
        address = response.json().get("results")[0].get("locations")[0].get(admin_area)
        if address is not None:
            return address
    except Exception:
        print response.content
    return None


def get_place(place_string):
    """
    Given a `place` string formatted like so: 
        8km ENE of Eielson Air Force Base, Alaska
    Returns just the location from the end of the string: `City, State` or `City, Country` 
    or `Location` if there is no regular expression match.
    """
    m = re.search("(\d+km \w+ of )([a-zA-Z\,\s]+)", place_string)
    if m is not None:
        return m.group(2)
    else:
        return place_string


    