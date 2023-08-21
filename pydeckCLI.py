import argparse
import pydeck as pdk
import json
import geopandas as gpd
import math
from shapely.geometry import Point, shape

def get_zoom_level(bounds, width, height):
    """
    Calculate an appropriate zoom level for a given bounding box and map size.

    :param bounds: Bounding box in the format (minx, miny, maxx, maxy)
    :param width: Width of the map in pixels
    :param height: Height of the map in pixels
    :return: Zoom level
    """
    minx, miny, maxx, maxy = bounds
    xdiff = maxx - minx
    ydiff = maxy - miny
    xzoom = -1 * (xdiff / width) / (2 * math.pi) * 360 / math.log(2)
    yzoom = -1 * (ydiff / height) / (2 * math.pi) * 360 / math.log(2)
    return min(xzoom, yzoom)

def create_map(input_file, layer_type, elevation_scale, fill_color, line_color, auto_highlight, pickable, extruded, stroked, filled, wireframe, coverage, pitch, bearing, output_file, elevation_property):
    
    """Create a 3D map using pydeck."""
    # Read data from the input file
    with open(input_file) as f:
        data = json.load(f)

    # Extract the features from the FeatureCollection
    features = data['features']

    # Calculate the bounding box and centroid of each feature
    bounds_list = []
    centroid_list = []
    for feature in features:
        geom = shape(feature['geometry'])
        bounds_list.append(geom.bounds)
        centroid_list.append(geom.centroid)

    # Calculate the total bounding box and centroid of the data
    minx = min(bounds[0] for bounds in bounds_list)
    miny = min(bounds[1] for bounds in bounds_list)
    maxx = max(bounds[2] for bounds in bounds_list)
    maxy = max(bounds[3] for bounds in bounds_list)
    bounds = (minx, miny, maxx, maxy)

    x = sum(centroid.x for centroid in centroid_list) / len(centroid_list)
    y = sum(centroid.y for centroid in centroid_list) / len(centroid_list)
    centroid = Point(x, y)
    longitude = centroid.x
    latitude = centroid.y

    # Calculate an appropriate zoom level based on the bounding box and map size
    zoom = get_zoom_level(bounds, 500, 500)

    # Define a layer to display on a map
    layer = pdk.Layer(
        type=layer_type,
        data=data,
        get_position=['lng', 'lat'],
        get_elevation=f'properties.{elevation_property}',
        get_fill_color=fill_color,
        get_line_color=line_color,
        auto_highlight=auto_highlight,
        elevation_scale=elevation_scale,
        pickable=pickable,
        elevation_range=[0, 3000],
        stroked=stroked,
        filled=filled,
        wireframe=wireframe,
        extruded=extruded,
        coverage=coverage)

    # Set the viewport location and zoom level
    view_state = pdk.ViewState(
        longitude=longitude,
        latitude=latitude,
        zoom=zoom,
        min_zoom=13,
        max_zoom=20,
        pitch=pitch,
        bearing=bearing)

    # Render and save the map
    r = pdk.Deck(layers=[layer], initial_view_state=view_state)
    r.to_html(output_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a 3D map using pydeck.')
    
    parser.add_argument('input_file', type=str, help='Input file path')
    
    parser.add_argument('--elevation-property', type=str, default='elevation', help='Name of the property in the GeoJSON file that contains the elevation values')
    
    parser.add_argument('--layer-type', type=str, choices=['GeoJsonLayer'], help='Type of layer to display on the map')
    
    parser.add_argument('--elevation-scale', default=1.00, type=float, help='Elevation scale of the layer')
    
    parser.add_argument('--fill-color', default=[255, 0, 0], nargs=3,type=int, help='Fill color of the layer (R G B)')
    
    parser.add_argument('--line-color', default=[0, 0, 255], nargs=3,type=int, help='Line color of the layer (R G B)')
    
    parser.add_argument('--auto-highlight', default=True,type=bool, help='Should the map elements highlight when hovered over? Boolean value (True/False).')
    
    parser.add_argument('--pickable', default=True,type=bool, help='Should the map elements be selectable when clicked? Boolean value (True/False).')
    
    parser.add_argument('--stroked', default=False,type=bool, help='HELPTEXT (True/False).')
    
    parser.add_argument('--filled', default=True,type=bool, help='HELPTEXT (True/False).')
    
    parser.add_argument('--wireframe', default=True,type=bool, help='HELPTEXT (True/False).')
    
    parser.add_argument('--extruded', default=True,type=bool, help='Should the map elements be three dimensional? Boolean value (True/False).')
    
    parser.add_argument('--coverage', default=1.0,type=float, help='Ratio (from 0.0 to 1.0) of all data to include in frame from the starting view.')
    
    parser.add_argument('--pitch', default=45.00,type=float, help='Azimuth / view direction of the map. Ranges from 0 to 90 degrees')
    
    parser.add_argument('--bearing', default=0.00,type=float, help='Degrees from true North that the layer will be oriented')
    
    parser.add_argument('output_file', type=str)
    
    args = parser.parse_args()
    
    create_map(args.input_file, args.layer_type, args.elevation_scale, args.fill_color, args.line_color, args.auto_highlight, args.pickable, args.stroked, args.filled, args.wireframe, args.extruded, args.coverage, args.pitch, args.bearing, args.output_file, args.elevation_property)

#CLI Argument should look something like this:
#python pydeckCLI.py input.geojson --layer-type GeoJsonLayer --elevation-property elevation --elevation-scale 1.00 --fill-color 85 85 85 --line-color 250 250 250 --auto-highlight True --pickable True --stroked False --filled True --wireframe False --extruded True --pitch 45.00 --bearing 0.00 output.html