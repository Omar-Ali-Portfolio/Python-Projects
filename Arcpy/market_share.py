"""
market_share.py

figures out what percent of Franklin County's population lives closest to each public library.
uses thiessen polygons to divide the county into library zones, then estimates population
in each zone using proportional area of census tracts.

inputs:
    public_library_shp  - library locations
    trt00_shp           - census tracts
    population          - population table by tract (field P001001)

output:
    market_share - one polygon per library with total pop (SUM_NewPop) and percent (PctPop)
"""

import arcpy
# enviornment
src_ws = r'E:\GEOG 5223\Data\libraries_data_sources'
out_path = r'E:\temp'
out_name = 'myoutput.gdb'
out_ws = out_path + '\\' + out_name
if not arcpy.Exists(out_ws):
    arcpy.management.CreateFileGDB(out_path, out_name)
arcpy.env.workspace = out_ws
out_ws_scratch = arcpy.env.scratchGDB
arcpy.env.overwriteOutput = True
#input, output, permaters
in_features_point = src_ws + '\\' + 'public_library_shp'
in_features_polygon = src_ws +'\\' + 'trt00_shp'
in_population_table = src_ws +'\\' + 'population'
in_unique_filed = 'NAME'
in_join_field = 'STFID2'
in_area_field = 'Area'
in_table_join_field ='GEO_ID'
in_table_population_field = 'P001001'
out_features_class = 'market_share'
# step 1. Create thiessen polygons based on library locations
# splits county into zones based on which library is closest
desc = arcpy.da.Describe(in_features_polygon)
arcpy.env.extent = desc['extent']
out_features_thiessen_polygons = out_ws_scratch + '/thiessen_tmp' #intermediate
arcpy.analysis.CreateThiessenPolygons(in_features_point, out_features_thiessen_polygons, 'ALL')
print(arcpy.Exists(out_features_thiessen_polygons))
# step 2 Intersect the thiessen polygons with tracts
# cuts tracts by library zone so each piece knows what library it belongs to
out_features_intersect = out_ws_scratch + '/intersect_tmp'
arcpy.analysis.Intersect([out_features_thiessen_polygons, in_features_polygon], out_features_intersect)
print(arcpy.Exists(out_features_intersect))
# step 3 Join intersection output with population table
# brings in population counts for each tract piece
arcpy.management.JoinField(out_features_intersect,
                          in_join_field,
                          in_population_table,
                          in_table_join_field,
                          [in_table_population_field])
# step 4 get the proportions
# estimates pop in each piece based on how much of the tract it covers
new_population_field = 'NewPop'
formula = f'!{in_table_population_field}! * !Shape_Area! / !{in_area_field}!'
arcpy.management.CalculateField(out_features_intersect, new_population_field,
                               formula,
                               field_type='DOUBLE',
                               expression_type='PYTHON3')
# step 5 dissolve into one polygon per library, sums up NewPop
out_features_dissolve = out_ws + '\\' + out_features_class
arcpy.management.Dissolve(out_features_intersect, out_features_dissolve, in_unique_filed, [[new_population_field, 'SUM']])
print(arcpy.Exists(out_features_dissolve))

# step 6 add up total county pop from the pop table
cursor = arcpy.da.SearchCursor(in_population_table, [in_table_population_field])
total_pop = 0
for row in cursor:
    total_pop += float(row[0])

# step 7 each librarys pop / county total * 100 = market share
pct_field = 'PctPop'
formula_pct = f'!SUM_{new_population_field}! / {total_pop} * 100'
arcpy.management.CalculateField(out_features_dissolve, pct_field, formula_pct, 'PYTHON3', field_type='DOUBLE')
print(arcpy.Exists(out_features_dissolve))
