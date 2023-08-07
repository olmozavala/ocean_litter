import xarray as xr
import matplotlib.pyplot as plt
import shapefile
import sys
sys.path.append("eoas_pyutils/")

##
def compute(ds, output_file, var_name, title):
    lats = ds['LATITUDE'].values
    lons = ds['LONGITUDE'].values
    part_beached = ds[var_name]

    w = shapefile.Writer(target=output_file, shapeType=shapefile.POINT) # Create the file

    # Add headers, the first two must be Lat and Lon
    w.field(title,'N')

    for i, c_lat in enumerate(lats):
        if i % 100 == 0:
            print(f"{i}/{len(lats)}")
        c_lon = lons[i]
        w.point(c_lon, c_lat)
        w.record(int(part_beached[i].item()))

    w.close()
    print("Done!!!")

## ======== Make geotiff for figure 2 =========
# --- Beached --
file_name = "/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/UN_Ocean_Litter/WorldLitter/data/Extras/mpw_beached_2010_2019.nc"
output_file = "/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/UN_Ocean_Litter/WorldLitter/data/Extras/BeachedParticles.shp"
ds = xr.load_dataset(file_name)
compute(ds, output_file,  'MPW_beach', 'Beached Particles')

# --- Ocean --
file_name = "/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/UN_Ocean_Litter/WorldLitter/data/Extras/mpw_ocean_2010_2019.nc"
output_file = "/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/UN_Ocean_Litter/WorldLitter/data/Extras/OceanParticles.shp"
ds = xr.load_dataset(file_name)
compute(ds, output_file,  'MPW_ocean', 'Ocean Particles')
