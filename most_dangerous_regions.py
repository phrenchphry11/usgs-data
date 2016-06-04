from collections import defaultdict
import argparse
import datetime
import json

import requests

from location_utils import get_place
from logarithmic_utils import sum_logscale_list


EARTHQUAKE_JSON_URL = "http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
PATH = "usgs_output"


class EarthquakeAnalyzer(object):
    days = None
    region_type = None
    num_regions = None
    VIABLE_REGION_GROUPINGS = ("tz", "net", "place",)

    def __init__(self):
        self.parse_arguments()

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description="Prints the most dangerous regions as measured"
                                         " by total measured earthquake energy in descending "
                                         "order.")
        parser.add_argument("--days", type=int, dest="days", default=30,
                            help="Number of days back from the current time to consider. "
                            "Defaults to 30.")
        parser.add_argument("--region-type", dest="region_type", default="tz",
                            help="Optional. Group earthquakes by different region type. "
                            "Defaults to tz. Accepts `tz` (timezone), `net` "
                            "(reporting network) and `place` (City, Country).")
        parser.add_argument("--num-regions", type=int, dest="num_regions", default=10,
                            help="Number of regions to display. "
                            "Defaults to 10.")

        args = parser.parse_args()
        self.days = args.days
        self.region_type = args.region_type
        self.num_regions = args.num_regions

    def analyze_and_print(self):
        """
        Prints a table of the regions with the most dangerous earthquakes.
        """
        earthquakes = self._get_earthquakes()
        earthquake_dict = self._group_earthquakes_by_region(earthquakes)
        formatted_earthquake_list = self._sort_by_most_dangerous(
            earthquake_dict)[:self.num_regions]

        print "REGION\t\tEARTHQUAKE COUNT\tTOTAL MAGNITUDE"
        for region, count, magnitude in formatted_earthquake_list:
            print "{}\t\t{}\t\t\t{}".format(region, count, magnitude)

    def _get_earthquakes(self):
        """
        Returns a JSON list of all earthquakes that occured with the past number of days (as 
            specified by the `days` command line arg.)
        """
        seen_ids, earthquake_history = self._load_previously_seen_earthquakes_from_file()
        earthquakes = self._request_new_earthquakes()
        earthquake_history = self._update_earthquake_history(earthquakes, earthquake_history,
                                                             seen_ids)
        return earthquake_history

    def _load_previously_seen_earthquakes_from_file(self):
        """
        Because the USGS API only returns earthquakes from within the past 30 days, we look up
        older earthquakes from our very basic earthquake file database.  Earthquake unique ids 
        are in $PATH/earthquake_ids.txt and the full JSON info of these ids can be found in 
        $PATH/usgs_dump.json 
        """
        seen_ids = []
        earthquake_history = []
        try:
            with open('{}/usgs_dump.json'.format(PATH), 'r') as data_file:
                data = json.load(data_file)
                earthquake_history.extend(data)
            with open('{}/earthquake_ids.txt'.format(PATH), 'r') as data_file:
                seen_ids = data_file.read().splitlines()
        except IOError:
            # The data file does not exist yet.
            pass
        return seen_ids, earthquake_history

    def _request_new_earthquakes(self):
        """
        Returns a JSON list of earthquakes from the USGS API.
        """
        earthquake_response = requests.get(EARTHQUAKE_JSON_URL)
        if earthquake_response.status_code == 200:
            earthquakes = earthquake_response.json()["features"]
        else:
            raise Exception(
                "Error getting earthquake data from: {}".format(EARTHQUAKE_JSON_URL))
        return earthquakes

    def _update_earthquake_history(self, new_earthquakes, earthquake_history, seen_ids):
        """
        Updates our very basic earthquake file database with earthquakes that have not previously 
        been seen before.
        """
        data_changed = False
        for quake in new_earthquakes:
            if quake["id"] not in seen_ids:
                earthquake_history.append(quake)
                seen_ids.append(quake["id"])
                data_changed = True
        if data_changed:
            with open('{}/usgs_dump.json'.format(PATH), 'w') as data_file:
                json.dump(earthquake_history, data_file)
            with open('{}/earthquake_ids.txt'.format(PATH), 'w') as data_file:
                data_file.write("\n".join(seen_ids))
        return earthquake_history

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
            epoch_time = earthquake["properties"]["updated"]
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
