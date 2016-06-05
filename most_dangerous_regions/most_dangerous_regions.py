from collections import defaultdict
import argparse
import datetime
import json
import os

import requests

from location_utils import get_place
from logarithmic_utils import sum_logscale_list


EARTHQUAKE_JSON_URL = "http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "usgs_output")


def get_db_path():
    return PATH


class EarthquakeAnalyzer(object):
    days = None
    region_type = None
    num_regions = None
    seen_ids = []
    earthquake_history = []
    VIABLE_REGION_GROUPINGS = ("tz", "net", "place",)

    def __init__(self):
        self._parse_arguments()
        self._load_earthquakes_from_db()

    def _parse_arguments(self):
        parser = argparse.ArgumentParser(description="Prints the most dangerous regions as measured"
                                         " by total measured earthquake energy in descending "
                                         "order.")
        parser.add_argument("--days", type=int, dest="days", default=30,
                            help="Optional. Number of days back from the current time to consider. "
                            "Defaults to 30.")
        parser.add_argument("--region-type", dest="region_type", default="place",
                            help="Optional. Group earthquakes by different region type. "
                            "Defaults to place. Accepts `tz` (timezone), `net` "
                            "(reporting network) and `place` (City, Country).")
        parser.add_argument("--num-regions", type=int, dest="num_regions", default=10,
                            help="Optional. Number of regions to display. "
                            "Defaults to 10.")

        args = parser.parse_args()
        self.days = args.days
        self.region_type = args.region_type
        self.num_regions = args.num_regions

    def analyze_and_print(self):
        """
        Fetches new earthquakes from the USGS API and saves them to the db.
        Prints a table of the regions with the most dangerous earthquakes.
        """
        earthquakes = self._request_new_earthquakes()
        self._update_earthquake_history(earthquakes)
        earthquake_dict = self._group_earthquakes_by_region(self.earthquake_history)
        formatted_earthquake_list = self._sort_by_most_dangerous(
            earthquake_dict)[:self.num_regions]

        header_list = ["REGION", "EARTHQUAKE COUNT", "TOTAL MAGNITUDE"]
        row_format = "{:<30}" * (len(header_list))
        print row_format.format(*header_list)
        for row in formatted_earthquake_list:
            print row_format.format(*row)

    def _load_earthquakes_from_db(self):
        """
        Loads previously seen earthquakes into the class, within the limit of the `day` param.
        Because the USGS API only returns earthquakes from within the past 30 days, we look up
        older earthquakes from our very basic earthquake file database.  Earthquake unique ids 
        are in $PATH/earthquake_ids.txt and the full JSON info of these ids can be found in 
        $PATH/usgs_dump.json 
        """
        try:
            with open('{}/usgs_dump.json'.format(get_db_path()), 'r') as data_file:
                data = json.load(data_file)
                self.earthquake_history.extend(data)
            with open('{}/earthquake_ids.txt'.format(get_db_path()), 'r') as data_file:
                self.seen_ids = data_file.read().splitlines()
        except IOError:
            # The data file does not exist yet.
            pass

    def _request_new_earthquakes(self):
        """
        Returns a GeoJson list of earthquakes from the USGS API.
        """
        earthquake_response = requests.get(EARTHQUAKE_JSON_URL)
        if earthquake_response.status_code == 200:
            earthquakes = earthquake_response.json()["features"]
        else:
            raise Exception(
                "Error getting earthquake data from: {}".format(EARTHQUAKE_JSON_URL))
        return earthquakes

    def _update_earthquake_history(self, new_earthquakes):
        """
        Updates our very basic earthquake file database with earthquakes that have not previously 
        been seen before.
        """
        data_changed = False
        for quake in new_earthquakes:
            if quake["id"] not in self.seen_ids:
                self.earthquake_history.append(quake)
                self.seen_ids.append(quake["id"])
                data_changed = True
        if data_changed:
            with open('{}/usgs_dump.json'.format(get_db_path()), 'w') as data_file:
                json.dump(self.earthquake_history, data_file)
            with open('{}/earthquake_ids.txt'.format(get_db_path()), 'w') as data_file:
                data_file.write("\n".join(self.seen_ids))

    def _group_earthquakes_by_region(self, earthquake_json):
        """
        Takes in an input of earthquakes in GeoJson format.
        Returns a dictionary where keys are regions, and the values are lists of magnitudes,
        all within the date specified by the command line args.
        """
        if self.region_type not in self.VIABLE_REGION_GROUPINGS:
            raise Exception(
                "Region `{}` not a valid region type.".format(self.region_type))

        cutoff_date = datetime.datetime.now(
        ) - datetime.timedelta(days=self.days)
        earthquake_dict = defaultdict(list)
        for earthquake in earthquake_json:
            region = self._get_region_grouping(earthquake)
            if region is None:
                continue
            magnitude = earthquake["properties"]["mag"]
            epoch_time = earthquake["properties"]["time"]
            # divide by 1000 to convert from milliseconds to seconds
            date = datetime.datetime.fromtimestamp(epoch_time / 1000)
            if date > cutoff_date:
                earthquake_dict[region].append(magnitude)
        return earthquake_dict

    def _get_region_grouping(self, earthquake):
        """
        Returns the name of the region by which the current earthquake will be grouped.
        """
        if self.region_type in ("tz", "net",):
            region = earthquake["properties"][self.region_type]
        else:
            place = earthquake["properties"]["place"]
            region = get_place(place)
        return region

    def _sort_by_most_dangerous(self, earthquake_dict):
        """
        Takes in an input dictionary of earthquake regions as keys, and the
        values a list of magnitudes.
        Returns a sorted list of lists, where each inner list includes:
         [region, number of earthquakes per region, total magnitude]
        The list of lists is sorted by total magnitude in decreasing order.
        """
        earthquake_list = []
        for region in earthquake_dict.keys():
            count = len(earthquake_dict[region])
            total_magnitude = sum_logscale_list(earthquake_dict[region])
            earthquake_list.append([region, count, total_magnitude])
        return sorted(earthquake_list, key=lambda earthquake: earthquake[2], reverse=True)


def main():
    earthquake_analyzer = EarthquakeAnalyzer()
    earthquake_analyzer.analyze_and_print()


if __name__ == "__main__":
    main()
