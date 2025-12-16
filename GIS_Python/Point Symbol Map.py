# #############################################
# Date   : 12/15/2024
# Module : Final Project
# Name   : Omar Ali
#
# proportional_point_symbol_map.py
#
# Description:
# Draws a proportional point symbol map from any
# polygon or multipolygon shapefile. Polygons are
# drawn as a base map, and proportional point
# symbols are placed at polygon centroids.
# #############################################


import sys
sys.path.append(r"C:\Users\omarali\python\lib")
from geom.shapex import *

import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch


# Helper functions

def make_path(polygon):
    """Create a matplotlib Path from a polygon."""
    verts = []
    codes = []
    for ring in polygon:
        for i in range(len(ring)):
            pt = ring[i]
            verts.append(pt)
            if i == 0:
                codes.append(Path.MOVETO)
            else:
                codes.append(Path.LINETO)
    return Path(verts, codes)


def polygon_centroid(poly):
    """Calculate center point by averaging coordinates."""
    exterior = poly[0]
    xs = [p[0] for p in exterior]
    ys = [p[1] for p in exterior]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def force_multipolygon(geom):
    """Make sure geometry is in multipolygon format."""
    if geom["type"] == "Polygon":
        return [geom["coordinates"]]
    return geom["coordinates"]


# 1) Ask for shapefile and validate geometry

while True:
    fname = input("Enter a polygon shapefile path: ").strip()
    
    try:
        shp = shapex(fname)
    except Exception as e:
        print("Error:", e)
        print("Make sure you entered a valid shapefile\n")
        continue
    
    gtype = shp[0]["geometry"]["type"]
    if gtype in ("Polygon", "MultiPolygon"):
        break
    
    print("Shapefile must be Polygon or MultiPolygon\n")


# 2) List fields and ask for numeric attribute

fields = [name for (name, _t) in shp.schema["properties"]]

print("\n=============================================")
print("There are " + str(len(shp)) + " features.")
print("Available fields:")
for f in fields:
    print("\t" + f)
print("=============================================\n")

while True:
    attr = input("Enter attribute name for proportional symbols: ").strip()
    if attr in fields:
        break
    print("Invalid field name. Try again.\n")


# 3) Collect centroids and attribute values

xs = []
ys = []
vals = []

for f in shp:
    geom = f["geometry"]
    props = f["properties"]
    
    if attr not in props:
        continue
    
    v = props[attr]
    if type(v) != int and type(v) != float:
        continue
    
    parts = force_multipolygon(geom)
    
    cx_list = []
    cy_list = []
    for poly in parts:
        cx, cy = polygon_centroid(poly)
        cx_list.append(cx)
        cy_list.append(cy)
    
    xs.append(sum(cx_list) / len(cx_list))
    ys.append(sum(cy_list) / len(cy_list))
    vals.append(float(v))


# 4) Scale symbol sizes (proportional)

if len(vals) == 0:
    print("\nError: No valid numeric values found")
    print("Cannot create map. Exiting.")
    shp.close()
else:
    vmax = max(vals)
    sizes = [50 + 450 * (v / vmax) for v in vals]
    
    
    # 5) Draw map
    
    fig, ax = plt.subplots()
    
    # Draw polygon base map
    for f in shp:
        geom = f["geometry"]
        parts = force_multipolygon(geom)
        
        for poly in parts:
            path = make_path(poly)
            patch = PathPatch(path,
                            facecolor="#DDDDDD",
                            edgecolor="blue",
                            linewidth=0.5)
            ax.add_patch(patch)
    
    # Draw proportional point symbols
    ax.scatter(xs, ys, s=sizes, alpha=0.75)
    
    ax.autoscale()
    ax.set_aspect(1)
    ax.set_title("Proportional Point Symbol Map")
    ax.grid()
    
    plt.show()
    
    shp.close()









