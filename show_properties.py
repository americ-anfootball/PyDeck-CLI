import argparse
import json

def show_properties(input_file):
    """Show the available GeoJSON properties of a file."""
    with open(input_file) as f:
        data = json.load(f)
    properties = set()
    for feature in data['features']:
        properties.update(feature['properties'].keys())
    print('Available properties:')
    for property in sorted(properties):
        print(f'  - {property}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Show the available GeoJSON properties of an input file.')
    parser.add_argument('input_file', type=str, help='Input file path')
    parser.add_argument('--properties', action='store_true', help='Show the available GeoJSON properties')
    args = parser.parse_args()
    
    if args.properties:
        show_properties(args.input_file)
