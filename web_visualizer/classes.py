from web_visualizer.store import *

# Data Definitions

# INTERPRETATION: A router with _ip_ located at [_latitude_, _longitude_]
class Router():
    ip = None
    def __init__(self, latitude, longitude, continent_code, ip=None):
        self.ip = ip
        self.latitude = latitude
        self.longitude = longitude
        self.continent_code = continent_code
    # Provide a json version of a router, so that it can be provided to the browser
    def jsonify(self):
        return {
            "ip": self.ip,
            "latitude": self.latitude,   
            "longitude": self.longitude,
            "continent_code": self.continent_code
        }
    # route : Router Router [List-of Router] -> [List-of Router]
    # Determine a route from _self_ to _destination_, choosing another router from ROUTERS or LANDING_POINTS if needed
    # ACCUMULATOR: The _path_ generated so far in the routing process
    # TERMINATION: Dealing with the circular case (adding the same router to the path twice) should ensure that all routers are searched through
    # HEURISTIC: Distance of router from destination
    def route(self, destination, path=[]):

        # Base case: The destination has been reached
        if self.latitude == destination.latitude and self.longitude == destination.longitude:
            return path
        # If we have run into a circular case, the path is invalid
        elif self in path:
            return False
        # If the current path is too long, the path is invalid
        elif len(path) > 30:
            return False
        else:
            # Update the path accumulator
            path.append(self)
            # Try each router within a given radius, starting with the closest to destination
            candidate_routers = candidates(self, destination, radius=1)

            for candidate in candidate_routers:
                candidate_path = candidate.route(destination, path=path)
                if candidate_path:
                    return candidate_path
            
            # If that radius of candidates came out with no successful path, try with a larger radius


# candidates : Router Router Number -> [List-of Routers]
# Provides a list of routers near _origin_, sorted in ascending order by distance to destination
def candidates(origin, destination, radius=1):
    return []


# INTERPREATION: A landing point for an oceanic cable, defining a path from _start_router_ to _end_router_ via _inner_nodes_
# By storing landing points like this, routing across the ocean will be an easy process
# N.B. The landing point might be stored twice, if that landing point connects to multiple cables
class LandingPoint(Router):
    def __init__(self, latitude, longitude, point_id):
        # Landing points don't have an ip address
        super().__init__(latitude, longitude, None)
        self.point_id = point_id
    # Provide a json version of a landing point, so that it can be provided to the browser
    def jsonify(self):
        return {
            "ip": self.ip,
            "latitude": self.latitude,   
            "longitude": self.longitude,
            "continent_code": self.continent_code,
            "point_id": self.point_id
        }
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

