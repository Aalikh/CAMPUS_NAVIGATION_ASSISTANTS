"""Campus Navigation Assistant - core logic (pure Python, no extra libraries).

Run `python navigator.py` for a terminal version, or `streamlit run app.py` for the web app.
Edit NODES, EDGES and PLACES below to use your real campus.
"""
from collections import deque
from html import escape

# ---------------------------------------------------------------- CAMPUS DATA
# Buildings: key -> name, building label, colour group, map x, map y, landmarks
NODES = {
    "mg":    {"n": "Main Gate",     "b": "Main Gate",              "c": "entry",    "x": 300, "y": 350, "lm": ["Security cabin", "Visitor parking"]},
    "plaza": {"n": "Central Plaza", "b": "Central Plaza",          "c": "plaza",    "x": 300, "y": 235, "lm": ["Fountain", "Campus map board"]},
    "admin": {"n": "Admin Block",   "b": "Admin Block",            "c": "admin",    "x": 105, "y": 235, "lm": ["Red-brick building", "Bank ATM"]},
    "lib":   {"n": "Library",       "b": "Library Building",       "c": "student",  "x": 495, "y": 235, "lm": ["Glass front", "Bookstore"]},
    "aud":   {"n": "Auditorium",    "b": "Auditorium",             "c": "student",  "x": 520, "y": 110, "lm": ["Dome roof", "Open-air stage"]},
    "aids":  {"n": "AI & DS Block", "b": "Block A (AI & DS)",      "c": "academic", "x": 300, "y": 110, "lm": ["Blue AI & DS signboard", "Bike stand"]},
    "caf":   {"n": "Cafeteria",     "b": "Cafeteria Court",        "c": "student",  "x": 165, "y": 110, "lm": ["Food court", "Water cooler"]},
    "stu":   {"n": "Student Centre","b": "Student Centre",         "c": "student",  "x": 55,  "y": 110, "lm": ["Notice boards", "Clubs room"]},
    "sci":   {"n": "Science Block", "b": "Block S (Science & Labs)","c": "labs",    "x": 410, "y": 38,  "lm": ["Garden", "Lab safety signboard"]},
}

# ---------------------------------------------------------------- GPS SETTINGS
# Real-world anchor: the GPS position of the Main Gate (replace with your real campus
# coordinates from Google Maps: right-click the gate > copy the two numbers).
# Every building without its own "lat"/"lon" is placed from the map layout below.
# For best accuracy, add "lat" and "lon" to each building in NODES.
GPS_ORIGIN = {"node": "mg", "lat": 12.240000, "lon": 79.650000}
METRES_PER_MAP_UNIT = 1.3          # how many metres one map unit (pixel) stands for
OFF_CAMPUS_M = 250                 # farther than this from every building = off campus

# Walkways: (from, to, directions from->to, directions to->from, metres)
EDGES = [
    ("mg", "plaza", "Walk straight along Main Avenue until you reach the fountain at Central Plaza.", "Walk back down Main Avenue towards the Main Gate.", 150),
    ("plaza", "admin", "From the fountain, turn left. The red-brick Admin Block is at the end of the path.", "From Admin Block, walk right along the path to the fountain.", 120),
    ("plaza", "lib", "From the fountain, turn right. The glass-front Library is straight ahead.", "From the Library, walk left to the fountain.", 120),
    ("plaza", "aids", "Go straight past the fountain. The blue signboard marks Block A.", "From Block A, walk straight back to the fountain.", 110),
    ("lib", "aud", "Take the path on the right side of the Library. The dome-roofed Auditorium is ahead.", "From the Auditorium, take the path back to the Library.", 110),
    ("aids", "caf", "Leave Block A and turn left. Follow the covered walkway to the Cafeteria.", "From the Cafeteria, follow the covered walkway to Block A.", 90),
    ("caf", "stu", "Walk past the food court to the Student Centre.", "Walk past the food court to the Cafeteria.", 70),
    ("aids", "sci", "Go out the back door of Block A and cross the garden to Block S.", "Cross the garden back to Block A.", 90),
]


import math as _m
_o = NODES[GPS_ORIGIN["node"]]
for _k, _N in NODES.items():
    if "lat" not in _N:
        _N["lat"] = GPS_ORIGIN["lat"] + (_o["y"] - _N["y"]) * METRES_PER_MAP_UNIT / 111320
        _N["lon"] = GPS_ORIGIN["lon"] + (_N["x"] - _o["x"]) * METRES_PER_MAP_UNIT / (111320 * _m.cos(_m.radians(GPS_ORIGIN["lat"])))

# Places: name -> building key, category, floor, room, what to look for
PLACES = {
    "Main Gate":                 {"node": "mg",    "cat": "Entry",              "floor": 0, "room": "Gate cabin",           "cue": "Security cabin on your left"},
    "Central Plaza":             {"node": "plaza", "cat": "Entry",              "floor": 0, "room": "Open plaza",          "cue": "Fountain in the middle, campus map board beside it"},
    "Administrative Office":     {"node": "admin", "cat": "Admin",              "floor": 0, "room": "Room AD-01",           "cue": "Reception desk just inside the entrance"},
    "Dean's Office":             {"node": "admin", "cat": "Admin",              "floor": 2, "room": "Room AD-205",          "cue": "Take the lift to Floor 2 and turn right"},
    "Examination Cell":          {"node": "admin", "cat": "Admin",              "floor": 1, "room": "Room AD-110",          "cue": "Next to the staircase on Floor 1"},
    "Library":                   {"node": "lib",   "cat": "Student Facilities", "floor": 0, "room": "Main Hall",            "cue": "Enter through the glass doors, counter on the left"},
    "Auditorium":                {"node": "aud",   "cat": "Student Facilities", "floor": 0, "room": "Main Hall",            "cue": "Big double doors under the dome"},
    "Cafeteria":                 {"node": "caf",   "cat": "Student Facilities", "floor": 0, "room": "Food Court",           "cue": "Seating area right at the walkway"},
    "Student Activity Centre":   {"node": "stu",   "cat": "Student Facilities", "floor": 1, "room": "Room SC-101",          "cue": "Stairs beside the notice boards"},
    "AI & DS Department Office": {"node": "aids",  "cat": "Academic Blocks",    "floor": 2, "room": "Room A-201",           "cue": "First door on the left after the Floor 2 stairs"},
    "AI & DS Faculty Cabins":    {"node": "aids",  "cat": "Academic Blocks",    "floor": 2, "room": "Rooms A-210 to A-225", "cue": "Corridor at the far end of Floor 2"},
    "Lecture Halls A101-A110":   {"node": "aids",  "cat": "Academic Blocks",    "floor": 1, "room": "Block A",              "cue": "Numbered doors along the Floor 1 corridor"},
    "AI & DS Department Lab":    {"node": "aids",  "cat": "Labs",               "floor": 3, "room": "Room A-301",           "cue": "Top floor, door with the lab sign"},
    "Physics Lab":               {"node": "sci",   "cat": "Labs",               "floor": 1, "room": "Room S-102",           "cue": "Right wing, behind the safety signboard"},
    "Chemistry Lab":             {"node": "sci",   "cat": "Labs",               "floor": 1, "room": "Room S-110",           "cue": "Left wing, lab coat needed inside"},
    "Computer Centre":           {"node": "sci",   "cat": "Labs",               "floor": 2, "room": "Room S-201",           "cue": "Take the lift to Floor 2"},
}

CATEGORIES = ["All", "Academic Blocks", "Labs", "Student Facilities", "Admin"]
COLORS = {"entry": "#ffd9a0", "plaza": "#a8a2c8", "admin": "#ffb4c8",
          "academic": "#8ab4ff", "labs": "#d6a2ff", "student": "#7ef0d0"}
ROUTE_COLOR = "#ffc58a"
WALK_SPEED_M_PER_MIN = 70

# ---------------------------------------------------------------- LOGIC
_graph = {}
for a, b, ab, ba, m in EDGES:
    _graph.setdefault(a, []).append((b, ab, m))
    _graph.setdefault(b, []).append((a, ba, m))


def places_in(category="All"):
    """Place names for a category button (All shows everything)."""
    return [p for p, d in PLACES.items() if category == "All" or d["cat"] == category]


def floor_text(n):
    return f"Floor {n}" if n else "Ground floor"


def find_route(start, goal):
    """Shortest path (fewest walkways) between two buildings using BFS.
    Returns a list of (next_building, directions, metres)."""
    queue, seen = deque([(start, [])]), {start}
    while queue:
        node, path = queue.popleft()
        if node == goal:
            return path
        for nxt, text, metres in _graph.get(node, []):
            if nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, path + [(nxt, text, metres)]))
    return None


def get_directions(from_place, to_place):
    """Everything the UI needs for one start/destination pair."""
    f, t = PLACES[from_place], PLACES[to_place]
    legs = [] if f["node"] == t["node"] else (find_route(f["node"], t["node"]) or [])
    steps = []
    if from_place == to_place:
        steps.append({"text": "You are already here.", "note": ""})
    else:
        if legs and f["floor"] > 0:
            steps.append({"text": f"Take the stairs or lift down to the ground floor of {NODES[f['node']]['b']} and step outside.", "note": ""})
        for nxt, text, metres in legs:
            steps.append({"text": text, "note": f"Landmarks: {', '.join(NODES[nxt]['lm'])} ({metres} m)"})
        if not legs:
            verb = "Go up" if t["floor"] > f["floor"] else "Go down" if t["floor"] < f["floor"] else "Stay on this floor"
            steps.append({"text": f"You are in the same building. {verb} to {floor_text(t['floor']).lower()} using the stairs or lift.", "note": ""})
        elif t["floor"] > 0:
            steps.append({"text": f"Go inside {NODES[t['node']]['b']} and take the stairs or lift to {floor_text(t['floor']).lower()}.", "note": ""})
    metres = sum(m for _, _, m in legs)
    return {
        "steps": steps,
        "metres": metres,
        "minutes": max(1, round(metres / WALK_SPEED_M_PER_MIN)) if metres else 0,
        "building": NODES[t["node"]]["b"],
        "floor": floor_text(t["floor"]),
        "room": t["room"],
        "cue": t["cue"],
        "nodes": [f["node"]] + [n for n, _, _ in legs],
    }


def map_svg(route_nodes, you=None):
    """Labelled campus layout (dark glass style) as an SVG string with a glowing route."""
    start, goal = route_nodes[0], route_nodes[-1]
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="100%">',
         '<style>.flow{animation:flow 1.4s linear infinite}@keyframes flow{to{stroke-dashoffset:-24}}@keyframes pulse{from{r:7;opacity:.9}to{r:22;opacity:0}}.pulse{animation:pulse 1.6s ease-out infinite}'
         '@media (prefers-reduced-motion:reduce){.flow,.pulse{animation:none}}</style>',
         '<defs><filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="4" result="b"/>'
         '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>',
         '<rect x="1" y="1" width="598" height="398" rx="22" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.14)"/>']
    for a, b, *_ in EDGES:
        A, B = NODES[a], NODES[b]
        s.append(f'<line x1="{A["x"]}" y1="{A["y"]}" x2="{B["x"]}" y2="{B["y"]}" stroke="rgba(255,255,255,0.12)" stroke-width="12" stroke-linecap="round"/>')
    for k, N in NODES.items():
        col = COLORS[N["c"]]
        on = k in (start, goal) and len(route_nodes) > 1
        ring = f' stroke="{ROUTE_COLOR}" stroke-width="3" filter="url(#glow)"' if on else f' stroke="{col}" stroke-width="1.5"'
        s.append(f'<rect x="{N["x"]-46}" y="{N["y"]-19}" width="92" height="38" rx="12" fill="{col}" fill-opacity="0.16"{ring}/>')
        s.append(f'<text x="{N["x"]}" y="{N["y"]+4}" text-anchor="middle" font-family="Outfit,Segoe UI,sans-serif" font-size="11" font-weight="500" fill="#f1ecff">{escape(N["n"])}</text>')
    if len(route_nodes) > 1:
        pts = " ".join(f'{NODES[k]["x"]},{NODES[k]["y"]}' for k in route_nodes)
        s.append(f'<polyline points="{pts}" fill="none" stroke="{ROUTE_COLOR}" stroke-opacity="0.45" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)"/>')
        s.append(f'<polyline class="flow" points="{pts}" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="6 18"/>')
        for k, label, col in ((start, "A", "#7ef0d0"), (goal, "B", ROUTE_COLOR)):
            N = NODES[k]
            s.append(f'<circle cx="{N["x"]+46}" cy="{N["y"]-19}" r="11" fill="{col}"/>')
            s.append(f'<text x="{N["x"]+46}" y="{N["y"]-15}" text-anchor="middle" font-family="Outfit,sans-serif" font-size="11" font-weight="700" fill="#1a1033">{label}</text>')
    if you:
        s.append(f'<circle class="pulse" cx="{you[0]:.0f}" cy="{you[1]:.0f}" r="7" fill="none" stroke="#6ee7ff" stroke-width="2"/>')
        s.append(f'<circle cx="{you[0]:.0f}" cy="{you[1]:.0f}" r="7" fill="#6ee7ff" stroke="#fff" stroke-width="2.5"/>')
        s.append(f'<text x="{you[0]:.0f}" y="{you[1]-14:.0f}" text-anchor="middle" font-family="Outfit,sans-serif" font-size="10" font-weight="600" fill="#6ee7ff">You</text>')
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- TERMINAL VERSION
def _pick(prompt):
    names = list(PLACES)
    for i, n in enumerate(names, 1):
        print(f"  {i:>2}. {n}")
    while True:
        v = input(prompt).strip()
        if v.isdigit() and 1 <= int(v) <= len(names):
            return names[int(v) - 1]
        match = [n for n in names if v.lower() and v.lower() in n.lower()]
        if len(match) == 1:
            return match[0]
        print("  Type a number or part of a name (e.g. 'lab').")


def main():
    print("\n=== Campus Navigation Assistant | Takshashila University ===\n")
    while True:
        print("Where are you now?"); a = _pick("Start (number or name): ")
        print("\nWhere do you want to go?"); b = _pick("Destination (number or name): ")
        d = get_directions(a, b)
        print(f"\n{a}  ->  {b}")
        print(f"{d['minutes']} min walk, {d['metres']} m | {d['building']}, {d['floor']}, {d['room']}\n" if d["metres"] else f"Same building | {d['floor']}, {d['room']}\n")
        for i, st in enumerate(d["steps"], 1):
            print(f"  {i}. {st['text']}")
            if st["note"]:
                print(f"     {st['note']}")
        print(f"  Arrived: {b} ({d['building']}, {d['floor']}, {d['room']}). Look for: {d['cue']}\n")
        if input("Another route? (y/n): ").strip().lower() != "y":
            break


if __name__ == "__main__":
    main()
