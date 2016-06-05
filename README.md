# Most Dangerous Earthquake Regions

This tool is a commandline program that returns a table of the regions on earth most prone to dangerous earthquakes, given data from the USGS [API](http://earthquake.usgs.gov/fdsnws/event/1/).

### Dependency installation

You'll need Python 2.7, and other dependencies should be installed via Pip.  Pip is already installed if you are 
running >= Python 2.7.9, but you can grab it [here](https://pip.pypa.io/en/stable/installing/).

Dependencies can be installed by running 
```
pip install -r requirements.txt
```

### Running the program

The program can be run through Python or just as a bash script:
```
python most_dangerous_regions/most_dangerous_regions.py 
```
or
```
./most-dangerous-regions
```

To learn about optional command line arguments, run:
```
python most_dangerous_regions/most_dangerous_regions.py -h
```
or
```
./most-dangerous-regions -h
```

Output that can be modified via command line arguments includes days, regional groupings, and number of regions to be displayed in the output.

Regional groupings include timezone (the command line arg is: `--region-type=tz`), network (`--region-type=net`), city (`--region-type=place`):  

1. Timezone is the offset from UTC in minutes at the event epicenter.

2. Network is the ID of a data contributor. Identifies the network considered to be the preferred source of information for this event.

3. Place is the City, State nearest to where the earthquake occurred.  Else, it is a general region, like `South of Tasmania`, for example.

Sample output looks something like:

```
$ ./most-dangerous-regions --region-type=place --num-regions=3 --days=2
REGION                        EARTHQUAKE COUNT              TOTAL MAGNITUDE               
Nikol                         3                             5.37918124605                 
South of Tasmania             1                             5.2                           
South of the Fiji Islands     1                             5.1   
```

and

```
$ ./most-dangerous-regions --region-type=net --num-regions=20
REGION                        EARTHQUAKE COUNT              TOTAL MAGNITUDE               
us                            801                           7.88966280209                 
ak                            2520                          5.84026391942                 
pr                            456                           5.41401148658                 
nc                            1565                          4.95204671502                 
nn                            1077                          4.75293920388                 
ci                            1255                          4.71465238654                 
at                            1                             4.6                           
hv                            217                           4.4228641695                  
uu                            164                           4.20861561329                 
uw                            437                           4.04561485108                 
mb                            154                           3.84026479175                 
nm                            32                            3.61392945576                 
se                            13                            3.23660841828                 
ismpkansas                    8                             2.9600003324                  
ld                            4                             1.85158129724
```

### Running unit tests

Unit tests should be run through [pytest](http://pytest.org/latest/).  To run:

```
cd tests

py.test
```

To run indivdual tests, separate the test class and the individual test within that class by two colons, like so:

```
py.test test_most_dangerous_regions.py::TestEarthquakeAnalyzer::test_load_existing_earthquakes_from_db
```  
