from math import cos, asin, sqrt, pi, isclose
import pycountry_convert as pc


# distance: Point Ppoint -> Number
# Determines the geographically accurate distance between _p1_ and _p2_
def distance(p1, p2):
    def deg2rad(deg): return deg * (math.pi/180)
    lat1 = float(p1.latitude)
    lat2 = float(p2.latitude)
    lon1 = float(p1.longitude)
    lon2 = float(p2.longitude)

    p = pi/180
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * \
        cos(lat2*p) * (1-cos((lon2-lon1)*p))/2
    return 116 * asin(sqrt(a))  # Rough approximation of change in lat/long

    return c


# parse_continent : String -> String
# Determines the continent that the location represented by _point_name_ is located on
def parse_continent(point_name):
    parts = point_name.split(", ")
    country_name = parts[len(parts) - 1]
    country_code = pc.country_name_to_country_alpha2(
        country_name, cn_name_format="lower")
    return get_continent(country_code)


# get_continent : String -> String
# Converts 2-character country code to continent code
def get_continent(country_code):
    return pc.country_alpha2_to_continent_code(country_code)


# contains_continent_code : String [List-of Point] -> Boolean
# Does _path_ contain a Point located on the continent specified by _continent_code_?
def contains_continent_code(continent_code, path):
    return continent_code in map(lambda point: point.continent_code, path)


# find_coord : Coordinate [List-of Coordinate] -> Number
# Is _coordinate_ in _cable_?
def find_coord(coordinate, cable):
    for i, coord in enumerate(cable):
        if same_location(coordinate, coord):
            return i
    return -1


# same_location : Coordinate Coordinate -> Boolean
# Are _c1_ and _c2_ approximately the same location (within 10^-2 of a degree)?
def same_location(c1, c2):
    return isclose(c1[0], c2[0], abs_tol=10**-2) and isclose(c1[1], c2[1], abs_tol=10**-2)


# reverse_cable_parts : [List-of [List-of Coordinates]] -> [List-of [List-of Coordinates]]
# Reverses the direction of every cable part in _whole_cable_
def reverse_cable_parts(whole_cable):
    return list(map(lambda cable_part: [ele for ele in reversed(cable_part)], whole_cable))


# expand_cables : [List-of [List-of Coordinates]] -> _
# Expands each part in _cable_ such that every sub-cable in that part is produced
def expand_cables(cables):
    # expand_cable : [List-of Coordinate] -> [List-of [List-of Coordinate]]
    # Expand a cable into all of its subcables, whose size is of at least 2 in length
    def expand_cable(cable):
        sub_cables = []
        for end in range(2, len(cable)+1):
            sub_cables.append(cable[0:end])
        return sub_cables

    temp = []
    for cable in cables:
        temp += expand_cable(cable)
    cables = temp
    return cables


# overlap : {X, Y} [List-of X] [List-of Y] -> Boolean
# Does _l2_ contain any elements that are in _l1_?
def overlap(l1, l2):
    for el in l2:
        if el in l1:
            return True
    return False
