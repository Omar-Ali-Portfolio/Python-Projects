"""
this program finds the total and percent of population living within 1 to 10 miles
of Franklin County public libraries. it uses proportional area to estimate population
within each buffer.

results:
1 mile:  277516, 25.96%
2 miles: 653674, 61.15%
3 miles: 860307, 80.48%
4 miles: 976032, 91.31%
5 miles: 1024574, 95.85%
6 miles: 1046181, 97.87%
7 miles: 1056989, 98.88%
8 miles: 1063023, 99.44%
9 miles: 1065710, 99.69%
10 miles: 1067301, 99.84%

only about 26% of residents are within 1 mile which makes sense since not everyone
lives right next to a library. but by 4 miles its already over 90% which tells us
the libraries are pretty well spread out across the county. after 5 miles the numbers
barely change meaning most of the remaining population is in more rural areas on
the edges of the county.
"""

import arcpy

### Environment
src_ws = r'E:\GEOG 5223\Data\libraries_data_sources'
out_path = r'E:\temp'
out_name = 'myoutput.gdb'
out_ws = out_path + '\\' + out_name
if not arcpy.Exists(out_ws):
    arcpy.management.CreateFileGDB(out_path, out_name)
arcpy.env.workspace = out_ws
out_ws_scratch = arcpy.env.scratchGDB
arcpy.env.overwriteOutput = True

#### input, output, parameters
in_features_point = src_ws + '\\' + 'public_library_shp'
in_features_polygon = src_ws + '\\' + 'trt00_shp'
in_population_table = src_ws + '\\' + 'population'
in_join_field = 'STFID2'
in_area_field = 'Area'
in_table_join_field = 'GEO_ID'
in_table_population_field = 'P001001'
out_features_clip = 'trt_clip'

def get_field_sum(table, field):
    cursor = arcpy.da.SearchCursor(table, [field])
    total = 0
    for row in cursor:
        total += float(row[0])
    return total

for mile in range(1, 11):

    ### Step 1. Create buffers
    out_features_buffer = out_ws_scratch + '\\buffers'  # intermediate
    arcpy.analysis.Buffer(in_features_point, out_features_buffer, f'{mile} Mile')

    #Step 2. Clip features
    arcpy.analysis.Clip(in_features_polygon, out_features_buffer, out_features_clip)

    #step 3. Join
    arcpy.management.JoinField(out_features_clip, in_join_field, in_population_table, in_table_join_field, [in_table_population_field])

    # Step 4. Calculate new field
    new_field_name = "proportional_pop"
    in_new_area_field = 'Shape_Area'
    formuala = f'!{in_table_population_field}! * !{in_new_area_field}! / !{in_area_field}!'
    arcpy.management.CalculateField(out_features_clip, new_field_name, '!P001001! * !Shape_Area! / !Area!', "PYTHON3")

    #step 5 Get total and percent
    pct = 100 * get_field_sum(out_features_clip, new_field_name)/get_field_sum(in_population_table, 'P001001')
    total_pop = get_field_sum(out_features_clip, new_field_name)

    print(f'{mile}, {total_pop:.0f}, {pct:.2f}%')




