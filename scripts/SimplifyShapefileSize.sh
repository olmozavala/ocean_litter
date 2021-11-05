#!/bin/bash
#ogr2ogr output.shp Data/world_countries_final.shp -dialect sqlite -sql \
# "SELECT ST_Union(geometry), LAND_RANK FROM world_countries_final GROUP BY LAND_RANK"

export SHAPE_ENCODING="UTF-8"

# Sep 27 2021. First run this
ogr2ogr /home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/UN_Ocean_Litter/WorldLitter/data/world_boundaries/Simplified_World_Countries.shp /home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/UN_Ocean_Litter/WorldLitter/data/world_boundaries/ne_50m_admin_0_countries.shp -simplify .05
# Then run countries_shp_to_geojson
#ogr2ogr /home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/UN_Ocean_Litter/WorldLitter/data/world_boundaries/Simplified_World_Countries.shp /home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/UN_Ocean_Litter/WorldLitter/data/world_boundaries/World_Countries__Generalized_.shp -simplify .05
#ogr2ogr -f GeoJSON -t_srs crs:84 /var/www/html/data/countries.geojson /home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/UN_Ocean_Litter/WorldLitter/data/world_boundaries/Simplified_World_Countries.shp
