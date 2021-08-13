from web_visualizer.py_auxiliary.constants import *
import os


# store_routers : Number -> [List-of Router]
# Uses the ip_addresses database to generate a list of Routers, of size _num_routers_
def store_routers(num_routers):

    ip_addresses_db = Database(IP_ADDRESSES_PATH)
    routers = []

    # Change to insert num_routers as argument instead (to avoid database manipulation)
    for loc in ip_addresses_db.query_db('SELECT * FROM ip_addresses ORDER BY RANDOM() LIMIT ?',
                                        [num_routers]):
        router = Router(ip=loc["ip"], latitude=float(loc["latitude"]), longitude=float(loc["longitude"]),
                        continent_code=loc["continent_id"])
        db.session.add(router)

    db.session.commit()


# store_landing_points
# TEMPORARY FUNCTION: Used to initially store the landing points
def store_landing_points():
    LandingPoint.query.delete()
    db.session.commit()
    # Iterate through all landing point JSON files
    for file in os.listdir(LANDING_POINTS_PATH):
        if file == "all.json":
            continue
        with open(LANDING_POINTS_PATH + '/' + file) as landing_point_file:
            data = json.load(landing_point_file)
            try:
                try:
                    continent_code = parse_continent(data["name"])
                except Exception:
                    continent_code = None
                landing_point = LandingPoint(latitude=float(data["latitude"]), longitude=float(data["longitude"]),
                                             point_id=data["id"], continent_code=continent_code, type="landing_point")
                db.session.add(landing_point)
            # Disregard landing points with invalid countries
            except KeyError:
                continue

    db.session.commit()


# store_paths
# TEMPORARY FUNCTION: Used to initially store the paths into a table
def store_paths():
    Path.query.delete()
    db.session.commit()

    for file in os.listdir(CABLES_PATH):
        with open(CABLES_PATH + '/' + file) as cable_file:
            try:
                data = json.load(cable_file)
                cable_paths = paths(data["landing_points"], data["id"])
                for path in cable_paths:
                    db.session.add(path)
            except Exception:
                continue
    db.session.commit()


# paths
# Given the _landing_points_ and _slug_ associated with a cable, generate all the 2-way cable paths (as point id's) that a packet could take
def paths(landing_points, slug):
    point_ids = map(lambda landing_point: landing_point["id"], landing_points)
    # Generate all 2-sized subsets of the landing points
    point_combinations = combinations(point_ids, 2)
    paths = []
    for combination in point_combinations:
        # Add the path and reverse of that path
        paths.append(
            Path(start_point_id=combination[0], end_point_id=combination[1], slug=slug))
        paths.append(
            Path(start_point_id=combination[1], end_point_id=combination[0], slug=slug))

    return paths
