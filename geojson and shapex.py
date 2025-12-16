# #############################################
# Date   : 10/13/2025
# Module : 2.2
# Name   : Omar Ali
# 
# geojson_shapex_explorer.py
# 

import sys
sys.path.append(r"C:\Users\omarali\python\lib")
from geom.shapex import *

# 1) Ask for a polygon shapefile and validate
while True:
    fname = input("Enter a shapefile name: ").strip()
    #fname = r"C:\Users\omarali\python\lib\geom\uscnty48area.shp"

    try:
        shp = shapex(fname)
    except Exception as e:
        print("Error:", e)
        print("Make sure your enter a valid shapefile\n")
        continue

    shp_type = shp[0]["geometry"]["type"]
    if shp_type in ("Polygon", "MultiPolygon"):
        break
    print("Make sure it is a polygon or multipolygon shapefile\n")

# 2) Basic file info

nfeat = len(shp)
fields = [name for (name, _t) in shp.schema["properties"]]

print("\n=============================================")
print(f"There are {nfeat} features in the shapefile.")
print(f"There are {len(fields)} fieds.")
print("The fields are:")
for nm in fields:
    print(f"\t {nm}")
print("=============================================\n")


# Helpers: report() and draw()

def report(feat):
    """Print geometry type and total point counts."""
    g = feat["geometry"]
    coords = g["coordinates"]
    if g["type"] == "Polygon":
        rings = len(coords)
        pts = sum(len(r) for r in coords)
        print("This is a Polygon")
        print(f"Number of rings is {rings} and total number of points is {pts}")
    else:  # MultiPolygon
        parts = len(coords)
        pts = sum(len(r) for part in coords for r in part)
        print("This is a MultiPolygon")
        print(f"Number of parts is {parts} and total number of points is {pts}")

def draw(feat):
    """[Bonus] Quick plot of the polygon or multipolygon."""
    import matplotlib.pyplot as plt
    g = feat["geometry"]
    parts = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]

    plt.figure()
    for part in parts:
        for i, ring in enumerate(part):
            xs = [p[0] for p in ring]
            ys = [p[1] for p in ring]
            # exterior ring a bit thicker, interior rings dashed
            plt.plot(xs, ys,
                     linewidth=1.6 if i == 0 else 1.0,
                     linestyle="-" if i == 0 else "--")
    title = feat["properties"].get("NAME", "feature")
    plt.title(title)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.axis("equal")
    plt.show()

def show_help():
    print("# ------------------------------------------")
    print("Type an INTEGER index (e.g., 0 or 2788) to see that feature.")
    print("Other commands:")
    print("   fields  - list attribute names again")
    print("   count   - show number of features")
    print("   draw    - draw the last valid feature you viewed")
    print("   done    - finish the program (also empty line)")
    print("# ------------------------------------------")

# 3) Interactive loop

last_idx = None
show_help()
while True:
    s = input("Enter feature index (or command): ").strip()

    # end program
    if s == "" or s.lower() == "done":
        print("Thank you for using our program!")
        break

    # small utilities
    if s.lower() == "fields":
        print("\nFields:")
        for nm in fields:
            print(f"\t {nm}")
        print()
        continue

    if s.lower() == "count":
        print(f"\nFeature count: {nfeat}\n")
        continue

    if s.lower() == "draw":
        if last_idx is None:
            print("Invalid index: need an integer\n")
        else:
            draw(shp[last_idx])
        continue

    if s.lower() in ("help", "?"):
        show_help()
        continue

    # must be an index from here
    try:
        idx = int(s)
    except:
        print("Invalid index: need an integer\n")
        continue

    if not (0 <= idx < nfeat):
        print("Invalid index: out of range\n")
        continue

    # show properties + geometry summary
    f = shp[idx]
    print(f"\nProperties: {f['properties']}.")
    report(f)
    last_idx = idx
    print()


# Results Below-----

"""
Enter a shapefile name: C:\Users\omarali\python\lib\geom\uscnty48area.shp
There are 3109 features in the shapefile.
There are 8 fields.
The fields are:
    NAME
    STATE_NAME
    FIPS
    UrbanPop
    Area
    AreaKM2
    GEO_ID
    PopDensity

Enter feature index: 0
Properties: {'NAME': 'Gallatin', ... }
This is a Polygon
Number of rings is 1 and total number of points is 72

Enter feature index: 2788
Properties: {'NAME': 'Rockbridge', ... }
This is a Polygon
Number of rings is 3 and total number of points is 51

Enter feature index: DONE
Thank you for using our program!
"""




      
