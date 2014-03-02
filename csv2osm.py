#!/usr/bin/python3

from pyproj import Proj, transform
from xml.sax.saxutils import quoteattr
import csv, argparse, sys, locale, re

parser = argparse.ArgumentParser(description="Convert csv spreadsheets to osm format.")
parser.add_argument('infile', help="Input csv file", nargs='?', type=argparse.FileType('r'), default=sys.stdin)
parser.add_argument('outfile', help="Output osm file", nargs='?', type=argparse.FileType('w'), default=sys.stdout)
parser.add_argument("-x", "--lon", help="Name of the longitude/easting field", metavar="FIELD_NAME")
parser.add_argument("-y", "--lat", help="Name of the latitude/northing field", metavar="FIELD_NAME")
parser.add_argument("-l", "--locale", help="Locale used to convert coordinate fields to float")
parser.add_argument("--proj4", help="Input coordinate system, given as a proj4 string", metavar="PROJ4_STRING")
parser.add_argument("--sirgas2000", metavar="ZONE", help="Set input coordinate system to SIRGAS2000 in the given UTM zone")
parser.add_argument("--sad69", metavar="ZONE", help="Set input coordinate system to SAD69 in the given UTM zone. Use the special value 'll' for longitude/latitude coordinates.")
parser.add_argument('--way', action='store_true', help="Create a way joining all nodes")
args = parser.parse_args()

proj_out = Proj('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs +towgs84=0,0,0')

if args.locale:
    locale.setlocale(locale.LC_NUMERIC, args.locale)

# Projection conversions according to http://wiki.osgeo.org/wiki/Brazilian_Coordinate_Reference_Systems
if args.proj4:
    proj_in = Proj(args.proj4)
elif args.sirgas2000:
    proj_in = Proj('+proj=utm +zone={} +south +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs'.format(args.sirgas2000))
elif args.sad69 == 'll':
    proj_in = Proj('+proj=longlat +ellps=aust_SA +towgs84=-67.35,3.88,-38.22,0,0,0,0 +no_defs')
elif args.sad69:
    proj_in = Proj('+proj=utm +zone={} +south +ellps=aust_SA +towgs84=-67.35,3.88,-38.22,0,0,0,0 +units=m +no_defs'.format(args.sad69))
else:
    proj_in = proj_out

parse_dms = re.compile(r'''(?P<pre>[NSWE+-]?)\s?(?P<deg>\d+)(?:°|º|\s?deg)\s?(?P<min>\d+)(?:'|’| )\s?(?P<sec>[\d,.]+)(?:"|”)?\s?(?P<post>[NSWE]?)''')

def parse_coord(c):
    try:
        return locale.atof(c)
    except:
        m = parse_dms.match(c)
        if m.group('post') and m.group('pre'):
            h = None
        elif m.group('post') in ['S', 'W'] or m.group('pre') in ['-', 'S', 'W']:
            h = -1
        elif m.group('post') in ['N', 'E'] or m.group('pre') in ['+', 'N', 'E']\
             or not (m.group('post') and m.group('pre')):
            h = 1
        return h * (locale.atof(m.group('deg')) + locale.atof(m.group('min'))/60 + locale.atof(m.group('sec'))/3600)

if args.infile.seekable():
    dialect = csv.Sniffer().sniff(args.infile.read(1024))
    args.infile.seek(0)
else:
    dialect = csv.excel

reader = csv.DictReader(args.infile, dialect=dialect)

try:
    xkey = args.lon or [i for i in ["LONGITUDE", "longitude", "lon", "x", "e"] if i in reader.fieldnames][0]
    ykey = args.lat or [i for i in ["LATITUDE", "latitude", "lat", "y", "n"] if i in reader.fieldnames][0]
except:
    sys.exit('Error: Coordinate fields not found in the csv file header.')

print('<?xml version="1.0" encoding="UTF-8"?><osm version="0.6" generator="csv2osm">', file=args.outfile)

i=0

for row in reader:
    i = i-1
    try:
        (lon, lat) = transform(proj_in, proj_out, parse_coord(row.pop(xkey)), parse_coord(row.pop(ykey)))
    except:
        print("Skipping node {}: couldn't parse coordinates".format(i), file=sys.stderr)
        continue
    print('<node id="{}" lat="{}" lon="{}">'.format(i,lat, lon), file=args.outfile)
    for key in row:
        if row[key]:
            print('<tag k="{}" v={}/>'.format(key, quoteattr(row[key])), file=args.outfile)
    print('</node>', file=args.outfile)

if args.way:
    print('<way id="{}" changeset="false">'.format(i-1), file=args.outfile)
    for j in range(-1,i-1,-1):
        print('<nd ref="{}"/>'.format(j), file=args.outfile)
    print('</way>', file=args.outfile)

print('</osm>', file=args.outfile)
