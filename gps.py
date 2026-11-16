"""GPS helpers for the Campus Navigation Assistant (pure Python, no extra libraries).

What it does
  1. haversine()      distance in metres between two GPS points
  2. locate()         which campus building is nearest to a GPS fix, and are we on campus?
  3. guidance()       straight-line distance + compass direction to a destination
  4. to_map_xy()      converts GPS to a point on the campus layout map ("You" dot)
Terminal test:  python gps.py 12.2400 79.6500 "AI & DS Department Lab"
"""
import math
import sys
from navigator import (NODES, PLACES, GPS_ORIGIN, METRES_PER_MAP_UNIT, OFF_CAMPUS_M,
                       get_directions)

EARTH_RADIUS_M = 6371000
ARRIVED_M = 30            # closer than this to the destination building = arrived
WEAK_ACCURACY_M = 100     # GPS error bigger than this = weak signal warning


def haversine(lat1, lon1, lat2, lon2):
    """Great-circle distance in metres."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = (math.sin((p2 - p1) / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2)
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def bearing(lat1, lon1, lat2, lon2):
    """Compass bearing in degrees (0 = north) from point 1 to point 2."""
    p1, p2, dl = math.radians(lat1), math.radians(lat2), math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def compass(deg):
    return ["north", "north-east", "east", "south-east", "south", "south-west", "west", "north-west"][round(deg / 45) % 8]


def default_place(node):
    """The place name to use as a starting point when you are at this building."""
    inside = [p for p, d in PLACES.items() if d["node"] == node]
    ground = [p for p in inside if PLACES[p]["floor"] == 0]
    return (ground or inside)[0]


def locate(lat, lon, accuracy=None):
    """Match a GPS fix to the nearest campus building."""
    best = min(NODES, key=lambda k: haversine(lat, lon, NODES[k]["lat"], NODES[k]["lon"]))
    dist = haversine(lat, lon, NODES[best]["lat"], NODES[best]["lon"])
    return {
        "node": best,
        "name": NODES[best]["n"],
        "distance": round(dist),
        "on_campus": dist <= OFF_CAMPUS_M,
        "place": default_place(best) if dist <= OFF_CAMPUS_M else "Main Gate",
        "accuracy": accuracy,
        "weak": accuracy is not None and accuracy > WEAK_ACCURACY_M,
    }


def guidance(lat, lon, dest_place):
    """Straight-line help to the destination building, plus its map link."""
    n = NODES[PLACES[dest_place]["node"]]
    metres = haversine(lat, lon, n["lat"], n["lon"])
    deg = bearing(lat, lon, n["lat"], n["lon"])
    return {
        "metres": round(metres),
        "direction": compass(deg),
        "degrees": round(deg),
        "arrived": metres <= ARRIVED_M,
        "maps_url": f"https://www.google.com/maps/dir/?api=1&origin={lat},{lon}&destination={n['lat']},{n['lon']}&travelmode=walking",
    }


def to_map_xy(lat, lon):
    """GPS -> (x, y) on the 600x400 campus layout map, or None if far outside it."""
    o = NODES[GPS_ORIGIN["node"]]
    east = (lon - GPS_ORIGIN["lon"]) * 111320 * math.cos(math.radians(GPS_ORIGIN["lat"]))
    north = (lat - GPS_ORIGIN["lat"]) * 111320
    x, y = o["x"] + east / METRES_PER_MAP_UNIT, o["y"] - north / METRES_PER_MAP_UNIT
    return (x, y) if -30 <= x <= 630 and -30 <= y <= 430 else None


def parse_coordinates(text):
    """'12.2401, 79.6503' -> (12.2401, 79.6503) or None if it is not valid."""
    try:
        a, b = [float(v) for v in text.replace(";", ",").split(",")]
        return (a, b) if -90 <= a <= 90 and -180 <= b <= 180 else None
    except ValueError:
        return None


def live_route(lat, lon, dest_place):
    """Step-by-step directions from the building you are actually standing at."""
    here = locate(lat, lon)
    return here, get_directions(here["place"], dest_place)


if __name__ == "__main__":
    la, lo = float(sys.argv[1]), float(sys.argv[2])
    dest = sys.argv[3] if len(sys.argv) > 3 else "Library"
    here, d = live_route(la, lo, dest)
    g = guidance(la, lo, dest)
    print(f"GPS fix {la}, {lo}")
    print(f"Nearest: {here['name']} ({here['distance']} m)" + ("" if here["on_campus"] else "  -> OFF CAMPUS, start from the Main Gate"))
    print(f"{dest} is {g['metres']} m to the {g['direction']}" + ("  (you have arrived)" if g["arrived"] else ""))
    for i, s in enumerate(d["steps"], 1):
        print(f"  {i}. {s['text']}")
