
import math
from web_visualizer.helpers import *

# Constants
MAX_PATH_LENGTH = 30

# Data Definitions

# A Point somewhere on the map


class Point():
    def __init__(self, latitude, longitude, continent_code):
        self.latitude = latitude
        self.longitude = longitude
        self.continent_code = continent_code

# INTERPRETATION: A router with _ip_ located at [_latitude_, _longitude_]


class Router(Point):
    def __init__(self, ip, latitude, longitude, continent_code=None):
        if continent_code == None:
            continent_code == get_continent(latitude, longitude)
        super().__init__(latitude, longitude, continent_code)
        self.ip = ip

    # route : Router Router [List-of Router] -> [List-of Router]
    # Determine a route from _self_ to _destination_, choosing another router from ROUTERS or LANDING_POINTS (if needed)
    # ACCUMULATOR: The _path_ generated so far in the routing process
    # TERMINATION:
    # - Dealing with the circular case (adding the same router to the path twice) should ensure that all routers are searched through
    # - The chosen neighbor for the path must be closer to the destination than the previous router
    # HEURISTIC: Distance of router from destination

    def route(self, destination, routers, path=None):

        # Set the default path
        if path == None:
            path = []

        # Base case: The destination has been reached -> Add destination & return
        if self.latitude == destination.latitude and self.longitude == destination.longitude:
            path.append(destination)
            return path
        # If we have run into a circular case, the path is invalid
        elif self in path:
            return False
        # If the current path is too long, the path is invalid
        elif len(path) > MAX_PATH_LENGTH:
            return False
        # Search for a path until it is found, increasing the radius of search as needed
        else:
            # Update the path accumulator
            path.append(self)

            candidate_path = False
            radius = 1

            # Try a path, starting with the closest routers
            while not candidate_path:
                candidate_path = self.route_neighbors(
                    destination, radius, routers, path=path)
                radius += 1

            return candidate_path

    # route_neighbors : Router Router Number [List-of Router] -> [Maybe List-of Router]
    # Attempts to find a path (of at most 30 routers) from _origin_ to _destination_, testing all routers within _radius_ of _origin_
    def route_neighbors(self, destination, radius, routers, path=[]):

        candidate_routers = self.neighbors(destination, routers, radius)

        # Sort routers for efficiency (test closest routers first)
        candidate_routers.sort(
            key=lambda router: distance(router, destination))

        # If the destination is a neighbor, the path is complete
        if destination in candidate_routers:
            path.append(destination)
            return path

        for candidate in candidate_routers:
            # Append the candidate to a new path

            candidate_path = candidate.route(destination, routers, path=path)

            if candidate_path:
                return candidate_path

        return False

    # neighbors : Router Router Number [List-of Routers] -> [Maybe List-of Routers]
    # Attempts to find routers within _radius_ of _self_ that are closer to _destination_ than _self_
    def neighbors(self, destination, routers, radius):
        # is_candidate : Router -> Boolean
        # Is _router_ a neighbor of _self_ (as defined in the purpose statement)?
        def is_candidate(router):
            return (self is not router) and (router.continent_code == self.continent_code) and (distance(self, router) <= radius) and (distance(router, destination) < distance(self, destination))
        # Try finding neighbors within _radius_
        candidates = list(filter(is_candidate, routers))

        return candidates


# INTERPREATION: A landing point for an oceanic cable, defining a path from _start_router_ to _end_router_ via _inner_nodes_
# By storing landing points like this, routing across the ocean will be an easy process
# N.B. The landing point might be stored twice, if that landing point connects to multiple cables


class LandingPoint(Point):
    def __init__(self, latitude, longitude, point_id):
        # Landing points don't have an ip address
        super().__init__(latitude, longitude, get_continent(latitude, longitude))
        self.point_id = point_id

    # Determine a route from _self_ to _destination_, such that the next router is closer to the destination
    # ACCUMULATOR: The _path_ generated so far in the routing process
    # TERMINATION: On each recursion, the current router in the path must be closer to _destination_ than the previous

    def route(self, destination, path=[]):
        # Base case: The destination has been reached
        if self.latitude == destination.latidue and self.longitude == self.latitude:
            return path
        # Circular case: We backtracked by accident
        elif self in path:
            return None
        else:
            # Choose a cable starting from _self_ whose endpoint (lat/lng) is closest to _destination_
            # Route the next router / landing point: route(...)
            return None


# HELPERS

# distance: Router Router -> Number
# Determines the distance between _r1_ and _r2_
def distance(r1, r2):
    return math.sqrt((r1.latitude - r2.latitude) ** 2 + (r1.longitude - r2.longitude) ** 2)
