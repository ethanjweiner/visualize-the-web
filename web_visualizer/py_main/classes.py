from web_visualizer import db
from web_visualizer.py_auxiliary.helpers import *
from web_visualizer.py_auxiliary.constants import *

import random
import json


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

    # route : Point Point [List-of Point] -> [List-of Point, Cable]
    # Determine a route of Points from _self_ to _destination_
    # ACCUMULATOR: The _path_ generated so far in the routing process
    # TERMINATION:
    # - [Circular case] Terminate the route
    # - [Non-circular case] Generally, the chosen neighbor is closer to the destination
    # HEURISTIC: Distance from neighbor to destination (lower is better)

    def route(self, destination, routers, radius_increment=0.5, path=None):

        # The radius can't expand too much
        if radius_increment > 2 * distance(self, destination):
            radius_increment = distance(self, destination)

        # Include the destination in the path to search for
        if destination not in routers:
            routers.append(destination)

        # Set the default path
        if path == None:
            path = []

        # BASE CASE: The destination has been reached -> Add destination & return
        if self.latitude == destination.latitude and self.longitude == destination.longitude:
            return path + [destination]

        # FAULTY CASE
        elif len(path) > MAX_PATH_LENGTH:
            return False

        # CIRCULAR CASE
        elif self in path:
            return False

        # MAIN LOGIC
        else:

            candidate_path = False
            radius = radius_increment

            # Try a path, starting with the closest routers
            while not candidate_path:
                # Avoid paths that search for neighbors far away
                if radius > 5 * distance(self, destination):
                    return False

                candidate_path = self.route_list(
                    destination, radius, routers, path=path+[self])

                radius += radius_increment

            return candidate_path

     # route_list : Point Point Number [List-of Point] -> [Maybe List-of Point, Cable]
    # Attempts to find a path from _origin_ to _destination_, testing all neighboring routers as specified by _radius_
    def route_list(self, destination, radius, routers, path=[]):
        # Search for nearby routers closer to destination
        candidate_routers = self.neighbors(destination, routers, radius)

        # Sort routers for efficiency (test closest routers first)
        # Switch to a weighted shuffle
        random.shuffle(candidate_routers)

        # If the destination is a neighbor, the path is complete
        if destination in candidate_routers:
            return path+[destination]

        for candidate in candidate_routers:
            # Append the candidate to a new path
            candidate_path = candidate.route(
                destination, routers, radius, path=path)

            if candidate_path:
                return candidate_path

        return False

    # neighbors : Point Point Number [List-of Point] -> [List-of Point]
    # Attempts to find routers within _radius_ of _self_
    # - Any Routers neighbors must be closer to _destination_ than _self_
    # - LandingPoint neighbors do not need to be much closer to _destination_
    def neighbors(self, destination, routers, radius):

        # is_candidate : Router -> Boolean
        # Is _point_ a neighbor of _self_ (as defined in the purpose statement)?
        def is_candidate(point):
            # If the candidate is a Router, it must be closer to the destination and not too close to the previous router
            if isinstance(point, Router):
                return (self is not point) and (self.continent_code == None or point.continent_code == self.continent_code) and (radius/5 <= distance(self, point) <= radius) and (distance(point, destination) < distance(self, destination))
            # If the candidate is a LandingPoint, give it some leeway
            else:
                max_distance = distance(self, destination) + 0.25
                return (self is not point) and (self.continent_code == None or point.continent_code == self.continent_code) and (distance(self, point) <= radius) and (distance(point, destination) < max_distance)

        # Try finding neighbors within _radius_
        candidates = list(filter(is_candidate, routers))

        return candidates


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

    # Override
    def route(self, destination, routers, radius_increment, path=None):

        # Set the default path
        if path == None:
            path = []

        # BASE CASE: The destination has been reached -> Add destination & return
        if self.latitude == destination.latitude and self.longitude == destination.longitude:
            return path + [destination]

        # FAULTY CASE: Retry routing from the start
        elif len(path) > MAX_PATH_LENGTH:
            return path[0].route(destination, routers)

        # CIRCULAR CASE
        elif self in path:
            return False

        # NORMAL ROUTING (same continent as destination)
        if self.continent_code == destination.continent_code:
            return Point.route(self, destination, routers, radius_increment, path=path)

        # TRANSCONTINENTAL ROUTING
        else:
            # Search for all paths
            path_candidates = Path.query.filter_by(
                start_point_id=self.point_id).all()

            # Add the endpoints to the paths
            for candidate in path_candidates:
                candidate.set_endpoint()

            # Filter paths that send to an unvisited continent
            path_candidates = list(filter(lambda candidate: candidate.endpoint != None and not contains_continent_code(
                candidate.endpoint, path+[self]), path_candidates))

            if not len(path_candidates):
                return False

            # Choose the endpoint closest to the destination
            path_candidates.sort(
                key=lambda candidate: distance(candidate.endpoint, destination))

            # Determine the cable to route with
            for candidate in path_candidates:

                cable = Cable([float(self.longitude), float(self.latitude)], [float(candidate.endpoint.longitude),
                                                                              float(candidate.endpoint.latitude)], candidate.slug)
                cable.find_nodes()

                candidate_path = candidate.endpoint.route(
                    destination, routers, radius_increment, path + [self, cable])

                if candidate_path:
                    return candidate_path

            # No candidates could be found
            return False


class Path(db.Model):
    __tablename__ = 'paths'

    id = db.Column(db.Integer, primary_key=True)
    start_point_id = db.Column(db.Text, nullable=False)
    end_point_id = db.Column(db.Text, nullable=False)
    slug = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Path from {self.start_point_id} to {self.end_point_id}"

    # Set the endpoint in the path corresponding to its _end_point_id_
    def set_endpoint(self):
        self.endpoint = LandingPoint.query.filter_by(
            point_id=self.end_point_id).first()


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


# polyline_dfs : [List-of [List-of Coordinate]] Coordinate Coordinate -> [List-of Coordinate]
# Using the lines in _whole_cable, finds some set of lines that connect _start_coordinate and end_coordinate_
def polyline_dfs(whole_cable, start_coordinate, end_coordinate):

    start = start_coordinate
    cable_parts = whole_cable + reverse_cable_parts(whole_cable)

    # ACCUMULATOR: _cable_accumulator_ represents the cable produced so far
    def polyline_dfs_accum(start_coordinate, cable_accumulator):
        # BASE CASE
        if same_location(start_coordinate, end_coordinate):
            return cable_accumulator + [start_coordinate]

        # CYCLICAL CASES
        elif find_coord(start_coordinate, cable_accumulator) != -1:
            return False

        else:

            if not len(cable_accumulator):
                cable_part_candidates = starting_cable_parts(
                    start_coordinate, cable_parts)
            else:
                cable_part_candidates = list(filter(lambda cable_part: same_location(
                    start_coordinate, cable_part[0]), cable_parts))

            cable_part_candidates = expand_cables(cable_part_candidates)

            candidate_path = False

            for cable_part in cable_part_candidates:
                # New starting coordinate: The end of the cable part
                # Update accumulator with the cable part
                if overlap(cable_part, cable_accumulator):
                    return False

                candidate_path = polyline_dfs_helper(
                    cable_part[len(cable_part)-1], cable_accumulator + cable_part[:-1])
                if candidate_path:
                    return candidate_path

            return False

    return polyline_dfs_accum(start_coordinate, [])


# starting_cable_parts : Coordinate [List-of [List-of Coordinate]] -> [List-of [List-of Coordinate]]
# Filters _cable_parts_ to those that have an endpoint on _start_coordinate_ (priority), OR
# creates cable parts from the parts in _cable_parts_ that contain _start_coordinate
def starting_cable_parts(start_coordinate, cable_parts):

    candidates = list(filter(lambda cable_part: same_location(
        start_coordinate, cable_part[0]), cable_parts))

    if len(candidates):
        return candidates

    candidates = []

    for cable_part in cable_parts:
        start = find_coord(start_coordinate, cable_part)

        if start != -1:
            # Starting coordinate to endpoint
            candidates.append(cable_part[start:len(cable_part)])
            # Staring point to starting coordinate
            candidates.append([ele for ele in reversed(cable_part[0:start+1])])

    return candidates
