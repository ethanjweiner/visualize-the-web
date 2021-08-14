from math import cos, asin, sqrt
from math import isclose
import random
import pycountry_convert as pc
from functools import reduce
from numpy.random import choice
from flask import session
from web_visualizer.py_auxiliary.constants import *


# same_landmass: Point Point -> Boolean
# Are _p1_ and _p2_ on the same landmass?
def same_landmass(p1, p2):
    return p1.continent_code == p2.continent_code or (p1.continent_code == 'AS' and p2.continent_code == 'EU') or (p1.continent_code == 'EU' and p2.continent_code == 'AS')


# distance: Point Point -> Number
# Determines the geographically accurate distance between _p1_ and _p2_, in degrees
def distance(p1, p2):
    p = 0.017453292519943295
    a = 0.5 - cos((p2.latitude-p1.latitude)*p)/2 + cos(p1.latitude*p) * \
        cos(p2.latitude*p) * (1-cos((p2.longitude-p1.longitude)*p))/2
    return 116 * asin(sqrt(a))


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


# choose_point : [List-of Point] Point Number -> [Maybe Point]
# Randomly choose a point from _points_, weighting points higher that are closer to _destination_
def choose_point(points, destination, cmp_distance):
    probabilities = generate_probabilities(
        points, destination, cmp_distance)
    if not probabilities:
        return False
    return choice(points, p=probabilities)


# generate_probabilities: [List-of Point] Point Number -> [Maybe List-of Number]
# Generate the probabilities that each point should be chosen from _points_, based on how much closer it is to the destination than _reference_point_
def generate_probabilities(points, destination, cmp_distance):
    # The weight is inversely proportional to the distance to the destination
    weights = (
        list(map(lambda point: {"id": point.id, "weight": get_weight(point, destination, cmp_distance)}, points)))
    sum_weights = reduce(lambda acc, ele: ele["weight"] + acc, weights, 0)
    if sum_weights == 0:
        return False
    return list(map(lambda ele: ele["weight"]/sum_weights, weights))


# get_weight : Point Point Number -> Number
# Generate a weight for a _point_ to be selected based on how much closer it is to _destination_ than _cmp_distance_
def get_weight(point, destination, cmp_distance):
    diff = cmp_distance - distance(point, destination)

    # Must move the router substantially
    if diff <= 0.5 and point.type == "router":
        return 0

    if diff <= -1 and point.type == "landing_point":
        return 0

    return (diff + 1) * 2


# random_radius : Point Point -> Number
# Generate a random starting radius, based on the total _distance_ from the starting point to the destination
def random_radius(distance):
    rand = random.random() * distance / 3 + distance / 10  # At least 0.5

    rand = rand if rand < 15 else 15
    rand = rand if rand > 2 else 2
    return rand


# random_router_seed : Number -> Number
# Retrieve a random router id that serves as a seed id for selecting all _num_routers_
def random_router_seed(num_routers):
    min = TOTAL_NUM_LANDING_POINTS + 1
    max = min + TOTAL_NUM_ROUTERS - num_routers - 1
    return random.randint(min, max)
