import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon, Point, MultiPoint
import shapely.speedups
import numpy as np
import functools
from os.path import join
from config.MainConfig import get_preproc_config
from config.params import GlobalModel, Preproc
import matplotlib.pyplot as plt

# REVISAR ESTOS SON IGUALES O HACEN LO MISMO
# https://github.com/olmozavala/ocean_litter/blob/5da13b00a1852b2aaf7079a128fad23b7ad13763/02_once_Countries_and_Oceans_from_locations.py

shapely.speedups.enable()

config = get_preproc_config()

input_folder = config[Preproc.shapes_folder]
output_file = config[GlobalModel.countries_file]
file_countries = 'ne_50m_admin_0_countries.shp'  # File with the countries polygons
release_loc_folder = config[GlobalModel.loc_folder]
lat_files = config[GlobalModel.lat_files]
lon_files = config[GlobalModel.lon_files]

buffer_size = .3  # in degrees

# File witht the ocean of the world polygons
geo_countries = gpd.GeoDataFrame.from_file(input_folder+file_countries)
geo_oceans = gpd.GeoDataFrame.from_file('/home/olmozavala/Dropbox/TestData/GIS/Shapefiles/World/oceans_oz/oceans_oz.shp')

print(F"Reading initial positions from {release_loc_folder}.....")
lons = functools.reduce(lambda a,b: np.concatenate((a,b), axis=0),
                      [np.genfromtxt(join(release_loc_folder, x), delimiter='') for x in lat_files])
lats = functools.reduce(lambda a,b: np.concatenate((a,b), axis=0),
                      [np.genfromtxt(join(release_loc_folder, x), delimiter='') for x in lon_files])

# Test for Zimbabwe
# lats = [29.6, 29.6]
# lons = [-19, -19]
# print("Done!")

print("Creating geofiles!")  # Builds a geofile with all the points in lats and lons
all_locs = [(lats[i], lons[i]) for i in range(len(lats))]
geo_locs = gpd.GeoDataFrame([Point(x[0], x[1]) for x in all_locs], columns=['geometry'])
print("Done!")

country_names = geo_countries['ADMIN']
continents = geo_countries['CONTINENT']
ocean_names = geo_oceans['name'].values
# Creates the dataframe taht will contain all the outputs
loc_by_country = pd.DataFrame([], index=country_names, columns=['total', 'oceans', 'continent', 'min', 'max', 'idx_country'])
tot_assigned = 0

print(country_names)
print(ocean_names)
print(continents.unique())

# print("Plotting...")
# fig, ax = plt.subplots()
# geo_countries.plot(ax=ax, facecolor='gray')
# geo_locs.plot(ax=ax)
# plt.show()
# print("Done!")

# Iterate over every country
for i, c_country in enumerate(country_names):
    idx_country = geo_countries['ADMIN'] == c_country
    c_continent = continents[i]

    # Creates a buffer of each country polygon
    c_geo_country = geo_countries[idx_country].geometry.buffer(buffer_size)

    # # Plot the buffered country
    # fig, ax = plt.subplots()
    # geo_countries.plot(ax=ax, facecolor='gray')
    # c_geo_country.plot(ax=ax, facecolor='red')
    # plt.show()

    print(F"---------- {c_country}",  end=" ")
    if len(c_geo_country) == 0:
        c_geo_country = [c_geo_country]

    temp_points = []
    indexes = []
    for c_geo in c_geo_country: # Iterate over all the polygons of the country (it can have multiple)
        # MAGIC here. Intersects the coordinates with the country
        inter = geo_locs.intersects(c_geo)
        points = geo_locs[inter].geometry # Obtains the locations that interesct
        if len(points) > 0:  # If intersects with some of the locations then we add it
            temp_points += points.values
            indexes += list(geo_locs[inter].index.values)
            # ========= Finding oceans for this country ================
            inter = geo_oceans.intersects(c_geo)
            int_oceans = geo_oceans[inter]['name'].values
            print(F' Oceans ({len(int_oceans)}): {int_oceans}',  end=" ")
            loc_by_country.at[c_country, 'oceans'] = ';'.join([x for x in int_oceans])

    if len(temp_points) > 0:
        loc_by_country.at[c_country, 'min'] = np.amin(np.array(indexes))
        loc_by_country.at[c_country, 'max'] = np.amax(np.array(indexes))
        loc_by_country.at[c_country, 'idx_country'] = indexes
        loc_by_country.at[c_country, 'continent'] = c_continent
        # loc_by_country.at[c_country, 'lat'] = ','.join([str(obj.x) for obj in temp_points])
        # loc_by_country.at[c_country, 'lon'] = ','.join([str(obj.y) for obj in temp_points])
        loc_by_country.at[c_country, 'total'] = len(temp_points)
        tot_assigned += len(temp_points)
        print(F"{len(temp_points)} ---------- ")
    else:
        print(F"Deleting {c_country} it doesn't intersect with any start location!!!!!!!! .....")
        loc_by_country.drop(c_country, inplace=True)

print(F"Saving data, total amount assigned: {tot_assigned}...")
loc_by_country.to_csv(output_file)
