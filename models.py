class Router():
    def __init__(self, ip, latitude, longitude):
        self.ip = ip
        self.latitude = latitude
        self.longitude = longitude

    def route(routers):
        # Find router to connect to
        return


# Optional class
class OceanicRouter(Router):
    def __init__(self, ip, latitude, longitude, nodes):
        super().__init__(ip, latitude, longitude)
        selfnodes = nodes

    def route(routers):
        # [If crossing ocean] Route directly through the other nodes OR
        # [Else] Inherit the routing process from Router: super().route(routers)?
        return
