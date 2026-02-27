# Omar Ali
# 2/27/26
#
# Clip Buffer Population Percentage (Standalone Script)
# Buffers points, clips polygons, joins population table, calculates proportional population,
# and prints percent of total population within the buffer.

import arcpy


def clip_buffer_pct(
    in_features_point,
    in_buffer_distance,
    in_features_polygon,
    in_area_field,
    in_join_field,
    in_population_table,
    in_table_join_field,
    in_table_population_field,
    out_features_clip
):
    # Allow overwriting outputs if needed
    arcpy.env.overwriteOutput = True

    # Step 1: Buffer points (store intermediate in scratch)
    out_features_buffer = arcpy.env.scratchGDB + "/buffers"
    if arcpy.Exists(out_features_buffer):
        arcpy.management.Delete(out_features_buffer)

    arcpy.analysis.Buffer(in_features_point, out_features_buffer, f"{in_buffer_distance} Mile")

    # Step 2: Clip polygons by buffer
    arcpy.analysis.Clip(in_features_polygon, out_features_buffer, out_features_clip, "")

    # Step 3: Join population field onto clipped polygons
    arcpy.management.JoinField(
        out_features_clip,
        in_join_field,
        in_population_table,
        in_table_join_field,
        [in_table_population_field]
    )

    # Step 4: Add new field for proportional population
    new_field_name = "proportional_pop"
    existing_fields = [f.name for f in arcpy.ListFields(out_features_clip)]
    if new_field_name not in existing_fields:
        arcpy.management.AddField(out_features_clip, new_field_name, "FLOAT", field_precision=10, field_scale=2)

    # Step 5: Calculate proportional population
    in_new_area_field = "Shape_Area"
    formula = f"!{in_table_population_field}! * !{in_new_area_field}! / !{in_area_field}!"
    arcpy.management.CalculateField(out_features_clip, new_field_name, formula, "PYTHON3")

    # Step 6: Percent calculation
    total = 0
    with arcpy.da.SearchCursor(in_population_table, [in_table_population_field]) as cursor:
        for row in cursor:
            total += row[0]

    sub_total = 0
    with arcpy.da.SearchCursor(out_features_clip, [new_field_name]) as cursor:
        for row in cursor:
            sub_total += row[0]

    percent = 100 * sub_total / total if total else 0
    arcpy.AddMessage(f"The percent of population in {in_buffer_distance} mile(s) is {percent:.2f}%.")

    return percent


if __name__ == "__main__":
    # Example inputs (edit these to match your paths / gdb)
    # You can use shapefiles or feature classes in a geodatabase.

    in_features_point = r"E:\GEOG 5223\Data\libraries_data_sources\public_library_shp.shp"
    in_buffer_distance = 1
    in_features_polygon = r"E:\GEOG 5223\Data\libraries_data_sources\trt00_shp.shp"
    in_area_field = "Area"
    in_join_field = "STFID2"
    in_population_table = r"E:\GEOG 5223\Data\libraries_data_sources\population.dbf"
    in_table_join_field = "GEO_ID"
    in_table_population_field = "P001001"

    out_features_clip = r"E:\temp\myoutput.gdb\clip_1mile"

    clip_buffer_pct(
        in_features_point,
        in_buffer_distance,
        in_features_polygon,
        in_area_field,
        in_join_field,
        in_population_table,
        in_table_join_field,
        in_table_population_field,
        out_features_clip
    )
