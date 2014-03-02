csv2osm
=======

Convert a csv table with geographical information to osm format.  This script supports coordinate system transformations and it can create a way joining all nodes in the csv file.  This is useful to import polygons described in the law into OSM.

Dependencies:

  - Python 3
  - pyproj (`sudo apt-get install python3-pyproj` on Debian/Ubuntu)

Usage
-----

If your csv file is reasonably well formatted and requires no coordinate system transformation, then `./csv2osm.py CSV_FILE.csv OSM_FILE.osm`  should do the trick.  If you need more info, type `./csv2osm.py -h`.

    usage: csv2osm.py [-h] [-x FIELD_NAME] [-y FIELD_NAME] [-l LOCALE]
		      [--proj4 PROJ4_STRING] [--sirgas2000 ZONE] [--sad69 ZONE]
		      [--way]
		      [infile] [outfile]

    Convert csv spreadsheets to osm format.

    positional arguments:
      infile                Input csv file
      outfile               Output osm file

    optional arguments:
      -h, --help            show this help message and exit
      -x FIELD_NAME, --lon FIELD_NAME
			    Name of the longitude/easting field
      -y FIELD_NAME, --lat FIELD_NAME
			    Name of the latitude/northing field
      -l LOCALE, --locale LOCALE
			    Locale used to convert coordinate fields to float
      --proj4 PROJ4_STRING  Input coordinate system, given as a proj4 string
      --sirgas2000 ZONE     Set input coordinate system to SIRGAS2000 in the given
			    UTM zone
      --sad69 ZONE          Set input coordinate system to SAD69 in the given UTM
			    zone. Use the special value 'll' for
			    longitude/latitude coordinates.
      --way                 Create a way joining all nodes


