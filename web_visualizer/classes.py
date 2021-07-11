from web_visualizer import db
from web_visualizer.helpers import get_continent, distance, contains_continent_code
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
            "continent_code": self.continent_code
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
            new_path = path + [self]
            # 1. The landing point MUST route to another landing point
            cable_candidates = Path.query.filter_by(
                start_point_id=self.point_id).all()

            # The landing point must have a cable that sends to an unvisited continent
            def is_valid_cable(cable):
                endpoint = LandingPoint.query.filter_by(
                    point_id=cable.end_point_id).first()
                return endpoint != None and not contains_continent_code(endpoint.continent_code, new_path)

            cable_candidates = list(filter(is_valid_cable, cable_candidates))

            if not len(cable_candidates):
                return False

            landing_point_candidates = list(map(lambda cable: LandingPoint.query.filter_by(
                point_id=cable.end_point_id).first(), cable_candidates))

            # Choose the endpoint closest to the destination
            landing_point_candidates.sort(
                key=lambda landing_point: distance(landing_point, destination))

            candidate_path = False

            for landing_point in landing_point_candidates:
                candidate_path = landing_point.route(
                    destination, routers, radius_increment, path=new_path)
                if candidate_path:
                    break

            return candidate_path


class Path(db.Model):
    __tablename__ = 'paths'

    id = db.Column(db.Integer, primary_key=True)
    start_point_id = db.Column(db.Text, nullable=False)
    end_point_id = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Path from {self.start_point_id} to {self.end_point_id}"
