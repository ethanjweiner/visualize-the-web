from web_visualizer import db
from web_visualizer.helpers import get_continent, distance, contains_continent_code
import random
from math import isclose
import json

MAX_PATH_LENGTH = 50
CABLES_GEOJSON_PATH = 'web_visualizer/data/cables.json'


class Point(db.Model):
    __tablename__ = 'points'  # Store all in a singular table

    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.String(20), nullable=False)
    longitude = db.Column(db.String(20), nullable=False)
    continent_code = db.Column(db.String(10), nullable=True)
    type = db.Column(db.Text, nullable=False)

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'point'
    }

    def __repr__(self):
        return f"Point{self.type, self.latitude, self.longitude, self.continent_code}"

    # route : Router Router [List-of Router] -> [List-of Router]
    # Determine a route from _self_ to _destination_, choosing another router from ROUTERS or LANDING_POINTS (if needed)
    # ACCUMULATOR: The _path_ generated so far in the routing process
    # TERMINATION:
    # - Dealing with the circular case (adding the same router to the path twice) should ensure that all routers are searched through
    # - The chosen neighbor for the path must be closer to the destination than the previous router
    # HEURISTIC: Distance of router from destination

    def route(self, destination, routers, radius_increment, path=None):

        if radius_increment > 2 * distance(self, destination):
            radius_increment = distance(self, destination)
        elif radius_increment < 0.5:
            radius_increment = 0.5
        # Include the destination in the path to search for
        if destination not in routers:
            routers.append(destination)

        # Set the default path
        if path == None:
            path = []

        # Base case: The destination has been reached -> Add destination & return
        if self.latitude == destination.latitude and self.longitude == destination.longitude:
            return path + [destination]

        # Invalid cases
        elif len(path) > MAX_PATH_LENGTH:
            return False

        # If we have run into a circular case, the path is invalid
        elif self in path:
            return False

        # Search for a path until it is found, increasing the radius of search as needed
        else:

            candidate_path = False
            radius = radius_increment

            # Try a path, starting with the closest routers
            while not candidate_path:
                # Avoid paths that search for neighbors far away
                if radius > 5 * distance(self, destination):
                    return False

                candidate_path = self.route_neighbors(
                    destination, radius, routers, path=path+[self])

                radius += radius_increment

            return candidate_path

     # route_neighbors : Router Router Number [List-of Router] -> [Maybe List-of Router]
    # Attempts to find a path (of at most 30 routers) from _origin_ to _destination_, testing all routers within _radius_ of _origin_
    def route_neighbors(self, destination, radius, routers, path=[]):
        # Search for nearby routers closer to destination
        candidate_routers = self.neighbors(destination, routers, radius)

        # Sort routers for efficiency (test closest routers first)
        random.shuffle(candidate_routers)

        # If the destination is a neighbor, the path is complete
        if destination in candidate_routers:
            return path+[destination]

        for candidate in candidate_routers:
            # Append the candidate to a new path
            # N.B.: Candidate could be a Router or LandingPoint
            candidate_path = candidate.route(
                destination, routers, radius, path=path)

            if candidate_path:
                return candidate_path

        return False

    # neighbors : Router Router Number [List-of Routers] -> [Maybe List-of Routers]
    # Attempts to find routers within _radius_ of _self_
    # - Any Routers neighbors must be closer to _destination_ than _self_
    # - LandingPoint neighbors do not need to be closer to _destination_
    def neighbors(self, destination, routers, radius):
        # is_candidate : Router -> Boolean
        # Is _router_ a neighbor of _self_ (as defined in the purpose statement)?
        def is_candidate(router):
            # If the candidate is a Router, it must be closer to the destination and not too close to the previous router
            if isinstance(router, Router):
                return (self is not router) and (self.continent_code == None or router.continent_code == self.continent_code) and (radius/5 <= distance(self, router) <= radius) and (distance(router, destination) < distance(self, destination))
            # If the candidate is a LandingPoint, give it some leeway
            else:
                max_distance = distance(self, destination) + 0.25
                return (self is not router) and (self.continent_code == None or router.continent_code == self.continent_code) and (distance(self, router) <= radius) and (distance(router, destination) < max_distance)

        # Try finding neighbors within _radius_
        candidates = list(filter(is_candidate, routers))

        return candidates


# Inherit Point class w/ Routers & Landing Points
class Router(Point):

    __tablename__ = None  # For STI, use the same table name as parent

    __mapper_args__ = {
        'polymorphic_identity': 'router'
    }

    ip = db.Column(db.String(40), nullable=True)

    def __repr__(self):
        return f"Router{self.ip, self.latitude, self.longitude, self.continent_code}"

    def toJson(self):
        return {
            "type": self.type,
            "ip": self.ip,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "continent_code": self.continent_code
        }


class LandingPoint(Point):

    __tablename__ = None  # For STI, use the same table name as parent

    __mapper_args__ = {
        'polymorphic_identity': 'landing_point'
    }

    point_id = db.Column(db.Text, nullable=True, unique=True)

    def __repr__(self):
        return f"LandingPoint({self.point_id, self.latitude, self.longitude, self.continent_code})"

    def toJson(self):
        return {
            "type": self.type,
            "point_id": self.point_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "continent_code": self.continent_code,
        }

    # route : Router Router [List-of Router] Number -> [List-of Router]
    # Determine a route from _self_ to _destination_, choosing another router from ROUTERS or LANDING_POINTS (if needed)
    # ACCUMULATOR: The _path_ generated so far in the routing process
    # TERMINATION:
    # - Dealing with the circular case (adding the same router to the path twice) should ensure that all routers are searched through
    # - The chosen neighbor for the path must be closer to the destination than the previous router
    # HEURISTIC: Distance of router from destination

    def route(self, destination, routers, radius_increment, path=None):

        # Set the default path
        if path == None:
            path = []

        if self in path:
            return False

        if len(path) > MAX_PATH_LENGTH:
            return False

        # If the LandingPoint and destination are on the same landmass, route in the normal manner (not overseas)
        if self.continent_code == destination.continent_code:
            return Point.route(self, destination, routers, radius_increment, path=path)
        # If they are not on the same landmass, route overseas
        else:
            # 1. The landing point MUST route to another landing point
            cable_candidates = Path.query.filter_by(
                start_point_id=self.point_id).all()

            # The landing point must have a cable that sends to an unvisited continent
            def is_valid_cable(cable):
                endpoint = LandingPoint.query.filter_by(
                    point_id=cable.end_point_id).first()
                return endpoint != None and not contains_continent_code(endpoint.continent_code, path+[self])

            cable_candidates = list(filter(is_valid_cable, cable_candidates))

            if not len(cable_candidates):
                return False

            def path_to_landing_point(path):
                return {
                    "point": LandingPoint.query.filter_by(point_id=path.end_point_id).first(),
                    "cable_slug": path.slug
                }

            landing_point_candidates = list(
                map(path_to_landing_point, cable_candidates))

            # Choose the endpoint closest to the destination
            landing_point_candidates.sort(
                key=lambda landing_point: distance(landing_point["point"], destination))

            candidate_path = False

            for landing_point in landing_point_candidates:

                cable = Cable([float(self.longitude), float(self.latitude)], [float(landing_point["point"].longitude),
                                                                              float(landing_point["point"].latitude)], landing_point["cable_slug"])
                cable.find_nodes()

                new_path = path + [self, cable]

                candidate_path = landing_point["point"].route(
                    destination, routers, radius_increment, new_path)

                if candidate_path:
                    break

            return candidate_path


class Path(db.Model):
    __tablename__ = 'paths'

    id = db.Column(db.Integer, primary_key=True)
    start_point_id = db.Column(db.Text, nullable=False)
    end_point_id = db.Column(db.Text, nullable=False)
    slug = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Path from {self.start_point_id} to {self.end_point_id}"


class Cable():
    type = "cable"
    nodes = []
    continent_code = None

    def __init__(self, start_coordinate, end_coordinate, slug):
        self.slug = slug
        self.start_coordinate = start_coordinate
        self.end_coordinate = end_coordinate

    def toJson(self):
        return {
            "type": self.type,
            "slug": self.slug,
            "nodes": self.nodes
        }

    # Update the nodes with the cable
    def find_nodes(self):
        with open(CABLES_GEOJSON_PATH) as cables_geojson:
            whole_cables = json.load(cables_geojson)["features"]

            # Find the cable with the proper slug
            whole_cable = None
            for cable in whole_cables:
                if cable["properties"]["slug"] == self.slug:
                    whole_cable = cable["geometry"]["coordinates"]
                    break

            # If no cable could be found, this route is false
            if whole_cable == None:
                self.nodes = []

            self.nodes = polyline_dfs(
                whole_cable, self.start_coordinate, self.end_coordinate)
            return self.nodes


# polyline_dfs : [List-of [List-of Coordinates]] Coordinate Coordinate -> [List-of Coordinates]
# Using the lines in _whole_cable, finds some set of lines that connect start_coordinate and end_coordinates
def polyline_dfs(whole_cable, start_coordinate, end_coordinate):
    # Create a DFS styled algorithm here
    cable_parts = whole_cable + reverse_cable_parts(whole_cable)

    # ACCUMULATOR: The cable produced so far
    def polyline_dfs_helper(start_coordinate, cable_accumulator):
        # The destination has been reached
        if same_location(start_coordinate, end_coordinate):
            return cable_accumulator + [start_coordinate]

        # Cyclical case
        elif find_coord(start_coordinate, cable_accumulator):
            return False

        else:
            # Determine all cable parts that start with the correct coordinate
            cable_part_candidates = list(filter(lambda cable_part: same_location(
                start_coordinate, cable_part[0]), cable_parts))

            # Expand all the cable parts
            cable_part_candidates = expand_cables(cable_part_candidates)

            candidate_path = False

            for cable_part in cable_part_candidates:
                # New starting coordinate: The end of the cable part
                # Update accumulator with the cable part (not including the end of the cable)
                candidate_path = polyline_dfs_helper(
                    cable_part[len(cable_part)-1], cable_accumulator + cable_part[:-1])
                if candidate_path:
                    return candidate_path

            # No candidates could be found from the starting point
            return []

    return polyline_dfs_helper(start_coordinate, [])

# find_coord : Coordinate [List-of Coordinate] -> Boolean
# Is _coordinate_ in _cable_?


def find_coord(coordinate, cable):
    for coord in cable:
        if same_location(coordinate, coord):
            return True
    return False

# same_location : Coordinate Coordinate -> Boolean
# Are _c1_ and _c2_ approximately the same location (within 10^-2 of a degree)?


def same_location(c1, c2):
    # Latitudes and longitudes are approximately equal
    return isclose(c1[0], c2[0], abs_tol=10**-2) and isclose(c1[1], c2[1], abs_tol=10**-2)


# reverse_cable_parts : [List-of [List-of Coordinates]] -> [List-of [List-of Coordinates]]
# Reverses the direction of every cable part in _whole_cable_
def reverse_cable_parts(whole_cable):
    return list(map(lambda cable_part: [ele for ele in reversed(cable_part)], whole_cable))


# expand_cables : [List-of [List-of Coordinates]] -> _
# Expands each part in _cable_ such that every sub-cable in that part is produced
def expand_cables(cables):
    # Assumes that a cable has at least 2 nodes
    def expand_cable(cable):
        sub_cables = []
        for end in range(2, len(cable)+1):
            sub_cables.append(cable[0:end])
        return sub_cables

    temp = []
    for cable in cables:
        temp = temp + expand_cable(cable)
    cables = temp
    return cables
