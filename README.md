# Most Dangerous Earthquake Regions

This tool is a commandline program that returns a table of the regions on earth most prone to dangerous earthquakes, given data from the USGS [API](http://earthquake.usgs.gov/fdsnws/event/1/).

### Dependency installation.

You'll need Python 2.7, and other dependencies should be installed via Pip.  Pip is already installed if you are 
running >= Python 2.7.9, but you can grab it [here](https://pip.pypa.io/en/stable/installing/).

Dependencies can be installed by running 
```
pip install -r requirements.txt
```

### Running the program.

The program can be run through Python or just as a bash script:
```
python most_dangerous_regions.py 
```
or
```
./most-dangerous-regions
```

To learn about optional command line arguments, run:
```
python most_dangerous_regions.py -h
```
or
```
./most-dangerous-regions -h
```

Output that can be modified via command line arguments includes days, regional groupings, and number of regions to be displayed in the output.

Regional groupings include timezone (tz) and network (net):  

1. Timezone is the offset from UTC in minutes at the event epicenter.

2. Network is the ID of a data contributor. Identifies the network considered to be the preferred source of information for this event.


Sample output looks something like:

```
$ ./most-dangerous-regions --region-type=net --num-regions=2
REGION    EARTHQUAKE COUNT  TOTAL MAGNITUDE
us    795     7.88891457232
ak    2485      5.83884362451
```

and

```
$ ./most-dangerous-regions --region-type=tz --num-regions=10
REGION    EARTHQUAKE COUNT  TOTAL MAGNITUDE
-120    15      7.22449270832
-300    218     7.14706659389
-720    135     6.98733617984
480   95      6.86882925426
420   17      6.68377930931
540   72      6.65808574549
-420    4362      6.53736881821
600   67      6.5362137677
-240    493     6.28999100609
720   36      6.28645960271
```