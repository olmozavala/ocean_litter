# RUN AT HPC
## Normal run (new releases)
To run in parallel the `HPC_RUN.sh` modifies the `generalrun_hpc.sh` file and creates multiple
copies of it, one for each monthly release. 
**Warning**: be sure the *HPC running extra years* is commented out on the file.  
Each copy of `generalrun_hpc.sh` will be in charge of a single monthly release. It stops and
restarts the run every **30** days (or other).

To make a new run you have to:

1. Modify `HPC_RUN.sh` and define the years and months you want to generate releases
2. Modify `generalrun_hpc.sh` and specify:
   1. End date for all the releases `end_date_str`
   2. Define the output folder and the name of your run (each name will be appended with the year and month of the release)

### Commands to remember
`gpfs_quota scratch` to check the quota of the scratch folder
`rcctool my:partitions` to check the status of the partitions 
`rcctool my:account` to check the status of the account 
`sinfo --partition coaps_q` to check the status of the partition

`ijobs` info on all your jobs
`cjobs` cancels all your jobs


## Extra year (appending to an existing runs)
To run in parallel the `HPC_RUN.sh` modifies the `generalrun_hpc_extra_year.sh` file and creates multiple
copies of it, one for each monthly release. 
**Warning**: be sure the *HPC running starting new run* is commented out on the file.  

To make a new run you have to:

1. Modify `HPC_RUN.sh` and define the years and months you want to append new data. (ALL DATA)
2. Modify `7_Merge_Merged_Adding_New_Years.py` update the paths to the new data.
3. Modify `generalrun_hpc__extra_year.sh` and specify:
   1. Start date, is the date we want to start appening data. For example, if we are adding  
   2023, then the start date may be 2022-12-31
   2. End date for all the releases `end_date_str`
   2. Define the output folder and the name of your run (each name will be appended with the year and month of the release)

I'm 

# Folders

* HPC Data
    * Currents `/gpfs/home/osz09/scratch/world_litter_data/`


* Local Data `/data/UN_Litter_data`
    * Test vector fields `/data/UN_Litter_data/HYCOM`
    * Local output `/data/UN_Litter_data/output`
        * Histogram output `/data/UN_Litter_data/output/histo`
        
* Net Data (Remote) `/Net/work/ozavala/WorldLitterOutput`
    * Local output `/data/UN_Litter_data/output`
        * Histogram output `/data/UN_Litter_data/output/histo`

* Tables 
    * Original input files `ozavala@enterprise/home/xbxu/hycom/GLBv0.08/nations`
    * Local input files at `./data` inside the project. YOU MUST COPY THEM HERE
    * Local output file **ReachedTablesData.json** at `/var/www/html/data`
    * Output file **ReachedTablesData.json** at `ozavala@ozavala.coaps.fsu.edu/var/www/virtualhosts/ozavala.coaps.fsu.edu/data`
* Web
    * Main `ozavala@ozavala.coaps.fsu.edu/var/www/virtualhosts/marinelitter.coaps.fsu.edu`
    * Dev `ozavala@ozavala.coaps.fsu.edu/var/www/virtualhosts/ozavala.coaps.fsu.edu/marine_litter_dev`

## Preprocessing steps 
### Reduce countires shapefile size (reduce level of detail on polyons with QGIS)

## Files
### 0_1_Combine_Locations_with_Countries_and_Oceans  (Interpreter geoeoas)
Inputs: 
  * `oceans_oz.shp`  shapefile with the oceans
  * `ne_50m_adming_0_countries.shp` shapefile with the countries limits
Outputs: 
  * `ParticlesByCountry.csv` file.
   
It reads the start locations of the particles, then it makes a buffer of each country and matches
the particles with one of the countries. It performs the same idea with the oceans and assigns
one or more oceans into each country.

### 1_WorldLitter.py
Main code to run the Ocean Parcels lagrangian code. 
It can be executed from from a restart file or not.
It receives the following parameters:
* Start date --> 'YYYY-MM-DD'
* End date --> 'YYYY-MM-DD'
* Contains winds --> Boolean "It will search for folders ending with 'c' rather than just the year"
* Perfrom diffusion --> Boolean
* Perfrom unbeaching--> Boolean
* **Name** --> Name of the run
* (optiona for restart) **Restart file** --> Name of the run
* Dayst to run --> Number of days to run


### 2_MergeRuns.py
This file is in charge of merging Ocean Parcels outputs.
It takes into account the date that is 'repeated' in contiguous files.

### 3_Show_Output.py
This file generates outputs in multiple ways (needs refactoring):
* Images from netcdfs in an accumulated way.
* Images from netcdfs not accumulated and in parallel.
* Images JSON output files.
* Using functions directly from Ocean Parcels outputs (netcdfs)

### 4_OceanParcels_to_JSON_and_ZIP_V2.py
This file transform a single netcdf to a json file with the following
features:
* It can subsample the number of output particles.
* Creates binary (zip) and header (txt) files (no JSON any more)

### 5_MakeHistogramNcWMS.py
This file can be used to generate a histogram of particles
locations. It can also merge the generated histograms into a single
larger histogram. 

### 6_AnalizeHistogram.py
Makes images the generated histograms.

# Tables related
Xiabiao tables are at `/home/xbxu/hycom/GLBv0.08/nations`.

### Make_Tables_by_Country.py
This file reads all the original files and generates a `csv` and `json` files.

### MakesTables_PngsForPDF_Plotly.py
Reads the stats data from `ReachedTablesData.json` and generates 
`png` and `svg` files as output.



# OLD need to verify where are those files
### 00_Combine_Currents_And_Wind.py
This file can be used to merge winds and currents. It can 
add a deflection angle into the wind and a percentage of wind
to be added. 

### 01_once_countries_shp_to_geojson
It simply converts a shape file into a geojson. It
creates the `countries.json` file used for the vector of countries.


