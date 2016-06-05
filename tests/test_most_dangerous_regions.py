from mock import patch
import os
import unittest

import pytest
import simplejson

from earthquake_tool.most_dangerous_regions.most_dangerous_regions import (EarthquakeAnalyzer, 
                                                                            get_db_path)

PATH_TO_JSON_DUMP = os.path.join(os.path.dirname(__file__), "test_files", "usgs_dump.json")


@patch("earthquake_tool.most_dangerous_regions.most_dangerous_regions.EarthquakeAnalyzer._parse_arguments")
@patch("earthquake_tool.most_dangerous_regions.most_dangerous_regions.get_db_path")
class TestEarthquakeAnalyzer(unittest.TestCase):

    def test_earthquake_analyzer_init_without_database(self, path, parse_args):
        """
        If there are no database files of earthquakes, when the Earthquake Analyzer is initialized,
        the earthquake_history and seen_ids attributes should be empty.
        """
        path.return_value = None
        earthquake_analyzer = EarthquakeAnalyzer()
        self.assertEquals(earthquake_analyzer.seen_ids, [])
        self.assertEquals(earthquake_analyzer.earthquake_history, [])

    def test_load_existing_earthquakes_from_db(self, path, parse_args):
        """
        Given test database files, when the Earthquake Analyzer is initialized, the analyzer 
        object should be prepopulated with earthquake json objects.
        """
        path.return_value = os.path.join(os.path.dirname(__file__), "test_files")
        earthquake_analyzer = EarthquakeAnalyzer()
        self.assertEquals(["ci37369271"], earthquake_analyzer.seen_ids)
        self.assertEquals(1, len(earthquake_analyzer.earthquake_history))

    def test_region_for_individual_earthquake(self, path, parse_args):
        """
        Given a single earthquake json element, and the region_type attribute of the analyzer set
        as `place`, the region for the earthquake json element should be a City, State.
        """
        earthquake_analyzer = EarthquakeAnalyzer()
        earthquake_analyzer.region_type = "place"
        with open(PATH_TO_JSON_DUMP, "r") as data_file:
            earthquake_json = simplejson.load(data_file)[0]
        region = earthquake_analyzer._get_region_grouping(earthquake_json)
        self.assertEquals("Fontana, CA", region)

    def test_timezone_for_individual_earthquake(self, path, parse_args):
        """
        Given a single earthquake json element, and the region_type attribute of the analyzer set
        as `tz`, the region for the earthquake json element should be a timezone id.
        """
        earthquake_analyzer = EarthquakeAnalyzer()
        earthquake_analyzer.region_type = "tz"
        with open(PATH_TO_JSON_DUMP, "r") as data_file:
            earthquake_json = simplejson.load(data_file)[0]
        region = earthquake_analyzer._get_region_grouping(earthquake_json)
        self.assertEquals(-420, region)

    def test_network_for_individual_earthquake(self, path, parse_args):
        """
        Given a single earthquake json element, and the region_type attribute of the analyzer set
        as `net`, the region for the earthquake json element should be a network id.
        """
        earthquake_analyzer = EarthquakeAnalyzer()
        earthquake_analyzer.region_type = "net"
        with open(PATH_TO_JSON_DUMP, "r") as data_file:
            earthquake_json = simplejson.load(data_file)[0]
        region = earthquake_analyzer._get_region_grouping(earthquake_json)
        self.assertEquals("ci", region)

    def test_group_earthquakes_by_region(self, path, parse_args):
        """
        Given the region_type attribute of the analyzer set as `place`, the keys of the region 
        groupings dictionary should be places.
        """
        earthquake_analyzer = EarthquakeAnalyzer()
        earthquake_analyzer.days = 30
        earthquake_analyzer.region_type = "place"
        with open(PATH_TO_JSON_DUMP, "r") as data_file:
            earthquake_json = simplejson.load(data_file)
        grouping_dict = earthquake_analyzer._group_earthquakes_by_region(earthquake_json)
        self.assertEquals(["Fontana, CA"], grouping_dict.keys())

    def test_group_earthquakes_by_timezone(self, path, parse_args):
        """
        Given the region_type attribute of the analyzer set as `tz`, the keys of the region 
        groupings dictionary should be timezones.
        """
        earthquake_analyzer = EarthquakeAnalyzer()
        earthquake_analyzer.days = 30
        earthquake_analyzer.region_type = "tz"
        with open(PATH_TO_JSON_DUMP, "r") as data_file:
            earthquake_json = simplejson.load(data_file)
        grouping_dict = earthquake_analyzer._group_earthquakes_by_region(earthquake_json)
        self.assertEquals([-420], grouping_dict.keys())

    def test_group_earthquakes_by_region_no_days(self, path, parse_args):
        """
        When we try to group earthquakes by region, but the days attribute on the analyzer is 0,
        no earthquakes should be returned, and the dictionary should be empty.
        """
        earthquake_analyzer = EarthquakeAnalyzer()
        earthquake_analyzer.days = 0
        earthquake_analyzer.region_type = "place"
        with open(PATH_TO_JSON_DUMP, "r") as data_file:
            earthquake_json = simplejson.load(data_file)
        grouping_dict = earthquake_analyzer._group_earthquakes_by_region(earthquake_json)
        self.assertEquals([], grouping_dict.keys())
