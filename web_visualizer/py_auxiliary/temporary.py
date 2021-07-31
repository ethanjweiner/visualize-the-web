from web_visualizer.py_auxiliary.constants import *
import os


# store_paths
# TEMPORARY FUNCTION: Used to initially store the paths into a table
def store_paths():

    for file in os.listdir(CABLES_PATH):
        with open(CABLES_PATH + '/' + file) as cable_file:
            try:
                data = json.load(cable_file)
                cable_paths = paths(data["landing_points"], data["id"])
                for path in cable_paths:
                    db.session.add(path)
            except KeyError:
                continue
            except UnicodeDecodeError:
                print(f"Improper JSON in {cable_file}")
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


# store_landing_points
# TEMPORARY FUNCTION: Used to initially store the landing points
def store_landing_points():
    # Iterate through all landing point JSON files
    for file in os.listdir(LANDING_POINTS_PATH):
        if file == "all.json":
            continue
        with open(LANDING_POINTS_PATH + '/' + file) as landing_point_file:
            data = json.load(landing_point_file)
            try:
                continent_code = parse_continent(data["name"])
                landing_point = LandingPoint(latitude=data["latitude"], longitude=data["longitude"],
                                             point_id=data["id"], continent_code=continent_code, type="landing_point")
                db.session.add(landing_point)
            # Disregard landing points with invalid countries
            except KeyError:
                continue

    db.session.commit()
