### Future improvements

The current biggest piece of techinical debt in this current implementation is the pseudo-database system I implemented.  Because the USGS API only provides up to 30 days of earthquake data, I went ahead and implemented a primitive storage system to persist data across program runs.  

Currently, when the user executes the program, a blob of JSON is returned from the USGS API.  There is a directory, `usgs_output` that contains two files, `usgs_dump.json` and `earthquake_ids.txt`.  All of this data gets loaded into the earthquake analyzer when it is instantiated.  Once the JSON is returned from the USGS, we look up the stored ids in `earthquake_ids.txt`, scan through the new JSON received, and see if there are any new, unseen ids that need to be added to our pseudo-database.  All new earthquakes and their ids get appended to the analyzer object and to the "database."  

This works well enough for the very low-volume usage of this program.  However, it still is not fast to read and write an entire JSON blob each time the program is executed, and additionally, earthquake data is only getting stored with each run of the program, so in the future, I hope to store the earthquake database in an actual database.  

This way, we can have a cron job periodically running to write new earthquakes to the database, and instead of loading all the earthquake data into the analyzer object with each run of the program, we can easily query on dates, regions, etc to filter and analyze only a subset of the total earthquakes.

Furthermore, storing these earthquakes in a true database rather than my simple "database" would allow for more robust testing.  Currently, the unit tests are a bit brittle and incomplete, partially because there isn't as much robust tooling to test my basic file read and write system!  I'd also like to add more unit tests around edge cases and error throwing.


### Region groupings

I chose my default region grouping to be by City.  It seemed most understandable and accessible to the layman, and since I have little knowledge about earthquakes, I am the layman who found the City groupings to be most interesting and easily understandible!  

This grouping isn't perfect, since many earthquakes do not occur near urbanized areas, so some earthquakes get grouped in a more general way, such as `South of the Fiji Islands`.  In addition, I used a regular expression to parse out the city from the USGS API, so if there is a typo coming from the API or the format of the strings suddenly changes, then groupings will be less accurate.

I also considered using Latitude and Longitude for more granular and precise regional data.  I did implement a Latitude/Longitude to City conversion using the MapQuest API.  However, there are no bulk coordinate lookups in the MapQuest API, so each time the program ran in my initial implementation, there were on average ~7 thousand MapQuest API calls.  Therefore, I scrapped the idea and went for the regular expression method as described above.  

If I were to implement this program in a more robust way using true databases, I would probably have a cron job querying the USGS API periodically, saving new earthquakes to a database, and then querying the MapQuest API with the Latitude and Longitude of the new earthquakes.  


### Implementing as a web service

If I were to expose this as a web service, some refactoring would be in order.  First of all, I would implement the use of a true database, rather than writing to a json file.  In this implementation, I tried to write my current code to be as modular as possible, with database read and writes in their own methods, so it would be easy enough to rip out the json file writing and replace with true database reads/writes.

Furthermore, I would not query the USGS API every time a user wants an earthquake analysis.  Since the USGS only updates earthquake info every ~15 minutes, I would have a cron job running in the background every 15 minutes that would update the database with any new earthquakes.  All earhquake analysis would be done on earthquakes already in the database belonging to our web service.

Before going out and implementing this as a web service, I'd like to find out more information about who the primary user of this is.  Currently, earthquakes are grouped by cities, but perhaps if a geologist is using this, it isn't meaningful to group earthquakes by what cities earthquakes are nearest to.  Perhaps it'd be better to group by what fault line the earthquake was closest to, or maybe latitude and longitude groupings are useful.  Maybe if an urban planner were using this tool, it'd be helpful to filter out any earthquakes that did not appear on land.  Or perhaps if a person didn't know much about earthquakes and was just looking to see how safe their city is, a city grouping is the most useful.  

Also, currenlty regions are sorted by total magnitude.  Depending on who is using this tool, perhaps it'd be useful to sort on number of earthquakes, frequency of earthquakes, or average magnitude of earthquakes.  These are things I'd like to talk to an average user about.
