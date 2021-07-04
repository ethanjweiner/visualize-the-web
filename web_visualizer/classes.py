from web_visualizer import db
from web_visualizer.helpers import get_continent, distance
import random

MAX_PATH_LENGTH = 50


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

    # Abstract
    def route():
        return 'Route'


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

    # route : Router Router [List-of Router] -> [List-of Router]
    # Determine a route from _self_ to _destination_, choosing another router from ROUTERS or LANDING_POINTS (if needed)
    # ACCUMULATOR: The _path_ generated so far in the routing process
    # TERMINATION:
    # - Dealing with the circular case (adding the same router to the path twice) should ensure that all routers are searched through
    # - The chosen neighbor for the path must be closer to the destination than the previous router
    # HEURISTIC: Distance of router from destination

    def route(self, destination, routers, radius_increment, path=None):

        # Include the destination in the path to search for
        if destination not in routers:
            routers.append(destination)

        # Set the default path
        if path == None:
            path = []

        # If the current path is too long, the path is invalid
        if len(path) > MAX_PATH_LENGTH:
            return False

        # If we have run into a circular case, the path is invalid
        elif self in path:
            return False

        # Base case: The destination has been reached -> Add destination & return
        elif self.latitude == destination.latitude and self.longitude == destination.longitude:
            path.append(destination)
            return path

        # Search for a path until it is found, increasing the radius of search as needed
        else:
            # Update the path accumulator
            path.append(self)

            candidate_path = False
            radius = radius_increment

            # Try a path, starting with the closest routers
            while not candidate_path:
                candidate_path = self.route_neighbors(
                    destination, radius, routers, path=path)
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
            path.append(destination)
            return path

        for candidate in candidate_routers:
            # Append the candidate to a new path

            candidate_path = candidate.route(
                destination, routers, radius, path=path)

            if candidate_path:
                return candidate_path

        return False

    # neighbors : Router Router Number [List-of Routers] -> [Maybe List-of Routers]
    # Attempts to find routers within _radius_ of _self_ that are closer to _destination_ than _self_
    def neighbors(self, destination, routers, radius):
        # is_candidate : Router -> Boolean
        # Is _router_ a neighbor of _self_ (as defined in the purpose statement)?
        def is_candidate(router):
            return (self is not router) and (self.continent_code == None or router.continent_code == self.continent_code) and (distance(self, router) <= radius) and (distance(router, destination) < distance(self, destination))
        # Try finding neighbors within _radius_
        candidates = list(filter(is_candidate, routers))

        return candidates


class LandingPoint(Point):

    __tablename__ = None  # For STI, use the same table name as parent

    __mapper_args__ = {
        'polymorphic_identity': 'landing_point'
    }

    # Use a foreign key to relate to landing points
    point_id = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"LandingPoint({self.point_id, self.latitude, self.longitude, self.continent_code})"

    def toJson(self):
        return {
            "type": self.type,
            "point_id": self.point_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "continent_code": self.continent_code
        }
