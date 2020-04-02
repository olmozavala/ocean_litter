import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon, Point, MultiPoint
import shapely.speedups
import numpy as np
import functools
from os.path import join
import matplotlib.pyplot as plt

shapely.speedups.enable()

input_folder = '/home/olmozavala/Dropbox/TestData/GIS/Shapefiles/World/high_res/'
output_folder = '/home/data/UN_Litter_data'
output_file = 'Particles_by_Country.csv'
data_folder = 'data'
file_countries = 'ne_50m_admin_0_countries.shp'
release_loc_folder = join(data_folder,"release_locations")
buffer_size = .2  # in degrees

lat_files = ['coasts_all_y.cvs', 'rivers_all_y.cvs']
lon_files = ['coasts_all_x.cvs', 'rivers_all_x.cvs']

geo_countries = gpd.GeoDataFrame.from_file(input_folder+file_countries)
geo_oceans = gpd.GeoDataFrame.from_file('/home/olmozavala/Dropbox/TestData/GIS/Shapefiles/World/oceans_oz/oceans_oz.shp')

print("Reading initial positions.....")
lons = functools.reduce(lambda a,b: np.concatenate((a,b), axis=0),
                      [np.genfromtxt(join(release_loc_folder, x), delimiter='') for x in lat_files])
lats = functools.reduce(lambda a,b: np.concatenate((a,b), axis=0),
                      [np.genfromtxt(join(release_loc_folder, x), delimiter='') for x in lon_files])

# Test for Zimbabwe
# lats = [29.6, 29.6]
# lons = [-19, -19]
# print("Done!")

print("Creating geofiles!")
all_locs = [(lats[i], lons[i]) for i in range(len(lats))]
geo_locs = gpd.GeoDataFrame([Point(x[0], x[1]) for x in all_locs], columns=['geometry'])
print("Done!")

country_names = geo_countries['ADMIN'].values
ocean_names = geo_oceans['name'].values
loc_by_country = pd.DataFrame([], index=country_names, columns=['total', 'oceans', 'min', 'max', 'idx_country'])

print(country_names)
print(ocean_names)

# print("Plotting...")
# fig, ax = plt.subplots()
# geo_countries.plot(ax=ax, facecolor='gray')
# geo_locs.plot(ax=ax)
# plt.show()
# print("Done!")

# Select an ocean for each country?
# for c_ocean in ocean_names:
#     print(F"---------- {c_ocean}",  end=" ")
#     idx_ocean = geo_oceans['name'] == c_ocean
#     c_geo_ocean = geo_oceans[idx_ocean].geometry.buffer(buffer_size)
#     if len(c_geo_ocean) == 0:
#         c_geo_ocean = [c_geo_ocean]
#
#     oceans = []
#     for c_geo in c_geo_ocean:
#         inter = geo_countries.intersects(c_geo)
#         points = geo_countries[inter].geometry
#         if len(points) > 0:
#             oceans += list(geo_countries[inter]['ADMIN'])
#
#     print(F"{oceans} ---------- ")

# Iterate over every country
for c_country in country_names:
    idx_country = geo_countries['ADMIN'] == c_country

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
    for c_geo in c_geo_country:
        inter = geo_locs.intersects(c_geo)
        points = geo_locs[inter].geometry
        if len(points) > 0:
            temp_points += points.values
            indexes += list(geo_locs[inter].index.values)
            # Finding oceans for this country
            inter = geo_oceans.intersects(c_geo)
            int_oceans = geo_oceans[inter]['name'].values
            print(F' Oceans ({len(int_oceans)}): {int_oceans}',  end=" ")
            loc_by_country.at[c_country, 'oceans'] = ';'.join([F"x" for x in int_oceans])


    if len(temp_points) > 0:
        loc_by_country.at[c_country, 'min'] = np.amin(np.array(indexes))
        loc_by_country.at[c_country, 'max'] = np.amax(np.array(indexes))
        loc_by_country.at[c_country, 'idx_country'] = indexes
        # loc_by_country.at[c_country, 'lat'] = ','.join([str(obj.x) for obj in temp_points])
        # loc_by_country.at[c_country, 'lon'] = ','.join([str(obj.y) for obj in temp_points])
        loc_by_country.at[c_country, 'total'] = len(temp_points)
        print(F"{len(temp_points)} ---------- ")
    else:
        print("Deleting!!!!!!!! .....")
        loc_by_country.drop(c_country, inplace=True)

loc_by_country.to_csv(join(output_folder, output_file))
