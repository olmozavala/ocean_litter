import numpy as np
import pandas as pd
import json
import cmocean.cm as cmo
import matplotlib.pyplot as plt
import matplotlib as mpl

countries_file = "./data/initial-locations-global.csv"
df = pd.read_csv(countries_file, header=0)

## Making the json
part_by_country = []
list_countries = list(df['country'].unique())
list_countries.sort()
tot_countries = len(list_countries)
max_tons_per_country = df.groupby('country').sum().iloc[:,2].max()
min_tons_per_country = df.groupby('country').sum().iloc[:,2].min()
norm = mpl.colors.LogNorm(min_tons_per_country, max_tons_per_country/5)
colors = plt.cm.get_cmap('jet', tot_countries)  # By country
# colors = plt.cm.get_cmap(cmo.thermal, tot_countries)  # By country

##
for c_id, c_country in enumerate(list_countries):
    c_country_data = df[df['country'] == c_country]
    print(f"Sum is: {tot_countries*norm(c_country_data.iloc[:,2].sum())}")
    print(f"Color is: {colors(int(tot_countries*norm(c_country_data.iloc[:,2].sum())))}")
    part_by_country.append({'name':c_country,
                            # "color": F"rgb{tuple(255 * np.array(colors(c_id - 1)))}",
                            "color": F"rgb{tuple(255 * np.array(colors(int(tot_countries*norm(c_country_data.iloc[:,2].sum()) ))))}",
                            "index": ','.join(list(c_country_data.index.astype(str)))
                            })

color_scheme = {'Countries':part_by_country}

with open("/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/Particle_viz/data/color_schemes/ColorSchemeWorldLitterMPW.json", 'w') as f:
# with open("/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/Particle_viz/data/color_schemes/ColorSchemeWorldLitterCountries.json", 'w') as f:
    json.dump(color_scheme, f, indent=4)
