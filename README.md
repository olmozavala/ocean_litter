### 00_Combine_Currents_And_Wind.py
This file can be used to merge winds and currents. It can 
add a deflection angle into the wind and a percentage of wind
to be added. 

### 01_once_countries_shp_to_geojson
It simply converts a shape file into a geojson. It
creates the `countries.json` file used for the vector of countries.

### 02_Countries_and_Oceans_from_locations
Produces the `ParticlesByCountry.py` file.
It reads the start locations of the particles,
then it makes a buffer of each country and matches
the particles with one of the countries. 

It performs the same idea with the oceans and assigns
one or more oceans into each country.
