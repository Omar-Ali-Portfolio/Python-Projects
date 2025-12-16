# ================================
# Exercises Projection
# Name: Omar Ali
# Date: 11-3-25
# File: hammer_equal_area_projection.py
#
# Course tie-ins (from the projections lectures):
# - Used the same data pattern as class: the Natural Earth 110m coastlines
#   and the course graticule (GeoJSON). Data is read with the urlopen + json
#   pattern shown in lecture.
# - Used a line_id for each polyline (same structure as the draw routine in lecture),
#   then projected each (lon, lat) to (x, y) and drew polylines by line_id.
# - Converted degrees to radians before trig .
# - Included a central meridian (lambda0) parameter so the map can be recentered
#   like the sinusoidal example in lecture.
#
# Projection chosen (allowed list item): Hammer (equal-area).
#   Formulas (λ, φ in radians):
#     x = [ 2√2 * cosφ * sin(λ/2) ] / √(1 + cosφ * cos(λ/2))
#     y = [ √2 * sinφ ]           / √(1 + cosφ * cos(λ/2))
#
# Sources / References:
# - Natural Earth 110m Coastlines (GeoJSON used in lecture)
#   https://raw.githubusercontent.com/gisalgs/data/master/ne_110m_coastline.geojson
# - Course graticule (GeoJSON used in lecture)
#   https://raw.githubusercontent.com/gisalgs/data/refs/heads/master/graticule.geojson
# - Projection formulas: Snyder (1987) “Map Projections—A Working Manual”,
#   and Wikipedia “Hammer projection”.
# ================================

import json
import math
from urllib import request
import matplotlib.pyplot as plt

# --- Point class import
import sys, importlib, os
if "/content" not in sys.path:
    sys.path.insert(0, "/content")
from point import Point

def make_point(line_id, x, y):
    """Create a Point that also carries its polyline id for grouping when drawing."""
    p = Point(x, y)
    p.id = line_id
    return p

def get_id(p): return getattr(p, "id", 0)
def get_x(p):  return p.x
def get_y(p):  return p.y

# --- Data loader
def load_geojson(url: str):
    with request.urlopen(url) as r:
        return json.loads(r.read())

# --- Data: same sources used in lecture
GRATICULE_URL = "https://raw.githubusercontent.com/gisalgs/data/refs/heads/master/graticule.geojson"
COAST_URL     = "https://raw.githubusercontent.com/gisalgs/data/master/ne_110m_coastline.geojson"

graticule = load_geojson(GRATICULE_URL)
coastline = load_geojson(COAST_URL)

# --- Build raw points as Point(line_id, x=lon, y=lat); track line boundaries ---
raw_points = []
line_id = 0

# Graticule: MultiLineString -> list of lines -> list of [lon, lat]

for f in graticule["features"]:
    geom_type = f["geometry"]["type"]
    coords    = f["geometry"]["coordinates"]

    if geom_type == "MultiLineString":
        for segment in coords:            # segment = list of [lon, lat]
            for lon, lat in segment:
                raw_points.append(make_point(line_id, lon, lat))
            line_id += 1
    elif geom_type == "LineString":
        for lon, lat in coords:           # coords = list of [lon, lat]
            raw_points.append(make_point(line_id, lon, lat))
        line_id += 1
    else:
        # Unexpected geometry; skip gracefully
        continue

num_graticule = line_id

print("Built raw_points:", len(raw_points), "| graticule lines:", num_graticule, "| total lines:", line_id)
s = raw_points[0]
print("sample -> id, lon, lat =", get_id(s), get_x(s), get_y(s))

# --- Hammer projection
def hammer_xy(lon_deg, lat_deg, lambda0_deg=0.0):
    lam = math.radians(lon_deg - lambda0_deg)   # λ - λ0  -> radians
    phi = math.radians(lat_deg)                 # φ -> radians
    denom = math.sqrt(1.0 + math.cos(phi) * math.cos(lam / 2.0))
    if denom == 0:
        return float("nan"), float("nan")
    x = (2.0 * math.sqrt(2.0) * math.cos(phi) * math.sin(lam / 2.0)) / denom
    y = (math.sqrt(2.0) * math.sin(phi)) / denom
    return x, y

# --- Project all raw points to (x, y) ---
lambda0 = 0.0   # central meridian; change (e.g., -20, 0, 20) to re-center
proj_points = []
for p in raw_points:
    x, y = hammer_xy(get_x(p), get_y(p), lambda0_deg=lambda0)
    proj_points.append(make_point(get_id(p), x, y))

fig, ax = plt.subplots(figsize=(10, 6))

# plot one polyline per line_id, graticule first (ids < num_graticule)
for lid in range(line_id):
    xs = [get_x(p) for p in proj_points if get_id(p) == lid]
    ys = [get_y(p) for p in proj_points if get_id(p) == lid]
    if not xs:     # skip empty (safety)
        continue
    if lid < num_graticule:
        ax.plot(xs, ys, lw=0.6, color="#cccccc")   # graticule
    else:
        ax.plot(xs, ys, lw=0.8, color="#333333")   # coastlines

ax.set_aspect("equal", adjustable="box")
ax.axis("off")
ax.set_title("Hammer (Equal-Area) Projection", pad=12)
plt.show()
