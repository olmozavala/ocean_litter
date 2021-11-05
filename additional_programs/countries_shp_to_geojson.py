import shapefile
from json import dumps
from os.path import join

input_folder = '/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/UN_Ocean_Litter/WorldLitter/data/world_boundaries/'
# input_file = join(input_folder, 'ne_50m_admin_0_countries.shp')
input_file = join(input_folder, 'Simplified_World_Countries.shp')
# input_file = join(input_folder, 'World_Countries__Generalized_.shp')
output_folder = '/var/www/html/data'
output_file = join(output_folder, 'countries.geojson')

# read the shapefile
reader = shapefile.Reader(input_file)
fields = reader.fields[1:]
field_names = [field[0] for field in fields]
print(field_names)
buffer = []
for sr in reader.shapeRecords():
    # For the ne file version, it contains the continent
    atr = dict(zip(field_names, sr.record))
    name = sr.record['ADMIN']
    continent = sr.record['CONTINENT']
    id = sr.record['ADM0_A3']
    atr = {'name': name, 'continent': continent, 'id': id}
    # atr = {'name': name, 'continent': continent}

    # ----- For the World file version, it contains the continent
    # name = sr.record['COUNTRY']
    # atr = {'name': name, 'id': id}

    geom = sr.shape.__geo_interface__
    buffer.append(dict(type="Feature", geometry=geom, properties=atr))

geojson = open(output_file, "w")
geojson.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")
geojson.close()