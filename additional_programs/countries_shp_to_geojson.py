import shapefile
from json import dumps
from os.path import join

input_folder = '/home/olmozavala/Dropbox/TestData/GIS/Shapefiles/World/high_res'
input_file = join(input_folder, 'ne_50m_admin_0_countries.shp')
output_folder = '/var/www/html/data'
output_file = join(output_folder, 'countries.json')

# read the shapefile
reader = shapefile.Reader(input_file)
fields = reader.fields[1:]
field_names = [field[0] for field in fields]
print(field_names)
buffer = []
for sr in reader.shapeRecords():
    # atr = dict(zip(field_names, sr.record))
    name = sr.record['ADMIN']
    continent = sr.record['CONTINENT']
    # id = sr.record['ADM0_A3']
    # atr = {'name': name, 'continent': continent, 'id': id}
    atr = {'name': name, 'continent': continent}
    geom = sr.shape.__geo_interface__
    buffer.append(dict(type="Feature", geometry=geom, properties=atr))

geojson = open(output_file, "w")
geojson.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")
geojson.close()