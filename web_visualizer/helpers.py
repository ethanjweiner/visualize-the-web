import math
import pycountry_convert as pc


# get_continent : String -> String
# Converts 2-character country code to continent code
def get_continent(country_code):
    return pc.country_alpha2_to_continent_code(country_code)


# distance: Router Router -> Number
# Determines the distance between _r1_ and _r2_
def distance(r1, r2):
    return math.sqrt((float(r1.latitude) - float(r2.latitude)) ** 2 + (float(r1.longitude) - float(r2.longitude)) ** 2)


def parse_continent(point_name):
    parts = point_name.split(", ")
    country_name = parts[len(parts) - 1]
    country_code = pc.country_name_to_country_alpha2(
        country_name, cn_name_format="lower")
    return get_continent(country_code)
