# Data Definitions

# INTERPRETATION: A router with _ip_ located at [_latitude_, _longitude_]
class Router():
    ip = None
    def __init__(self, latitude, longitude, ip=None):
        self.ip = ip
        self.latitude = latitude
        self.longitude = longitude
    # Provide a json version of a router, so that it can be provided to the browser
    def jsonify(self):
        return {
            "ip": self.ip,
            "latitude": self.latitude,   
            "longitude": self.longitude
        }
    # Determine a route from _self_ to _destination_, such that the next router is closer to the destination
    # ACCUMULATOR: The _path_ generated so far in the routing process
    # TERMINATION: Dealing with the circular case (adding the same router to the path twice) should ensure that all routers are searched through
    def route(self, destination, path=[]):
        # Base case: The destination has been reached
        if self.latitude == destination.latidue and self.longitude == self.latitude:
            return path
        # Circular case: We backtracked by accident
        elif self in path:
            return None
        else:
            # Route the next router/landing point: route(...)
            return None


# INTERPREATION: A landing point for an oceanic cable, defining a path from _start_router_ to _end_router_ via _inner_nodes_
# By storing landing points like this, routing across the ocean will be an easy process
# N.B. The landing point might be stored twice, if that landing point connects to multiple cables
class LandingPoint(Router):
    def __init__(self, latitude, longitude, point_id):
        # Landing points don't have an ip address
        super().__init__(latitude, longitude)
        self.point_id = point_id
    # Provide a json version of a landing point, so that it can be provided to the browser
    def jsonify(self):
        return {
            "ip": self.ip,
            "latitude": self.latitude,   
            "longitude": self.longitude,
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

