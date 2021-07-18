from math import cos, asin, sqrt, pi
import pycountry_convert as pc


# get_continent : String -> String
# Converts 2-character country code to continent code
def get_continent(country_code):
    return pc.country_alpha2_to_continent_code(country_code)


# distance: Router Router -> Number
# Determines the geographically accurate distance between _r1 and _r2_

def distance(r1, r2):
    def deg2rad(deg): return deg * (math.pi/180)
    lat1 = float(r1.latitude)
    lat2 = float(r2.latitude)
    lon1 = float(r1.longitude)
    lon2 = float(r2.longitude)

    p = pi/180
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * \
        cos(lat2*p) * (1-cos((lon2-lon1)*p))/2
    return 116 * asin(sqrt(a))  # Rough approximation of change in lat/long

    return c


# distance_v1: Router Router -> Number
# Determines the geometrically accurate distance between _r1_ and _r2_
def distance_v1(r1, r2):
    return sqrt((float(r1.latitude) - float(r2.latitude)) ** 2 + (float(r1.longitude) - float(r2.longitude)) ** 2)


def parse_continent(point_name):
    parts = point_name.split(", ")
    country_name = parts[len(parts) - 1]
    country_code = pc.country_name_to_country_alpha2(
        country_name, cn_name_format="lower")
    return get_continent(country_code)


# contains_continent_code : String [List-of Point] -> Boolean
# Does _path_ contain a Point located on the continent specified by _continent_code_?

def contains_continent_code(continent_code, path):
    return continent_code in map(lambda point: point.continent_code, path)
