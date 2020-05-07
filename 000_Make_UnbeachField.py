"""
Created on December 1 2018
@author: Philippe Delandmeter
Function creating the unbeach velocity for the CMEMS data (A-grid)
"""
import xarray as xr
import numpy as np
from os.path import join


# data_dir = '/home/data/UN_Litter_data/HYCOM/2010c/'
data_dir = '/data/UN_Litter_data/HYCOM/2010c/'
datasetM = xr.open_dataset(data_dir + 'hycom_JRA55_GLBv0.08_20100101_t000.nc')

dataArrayLonF = datasetM['longitude']
dataArrayLatF = datasetM['latitude']

U = np.array(datasetM.surf_u)
V = np.array(datasetM.surf_v)

unBeachU = np.zeros(U.shape[1:])
unBeachV = np.zeros(V.shape[1:])

def island(U, V, j, i):
    if np.isnan(U[0, j, i]) and np.isnan(V[0, j, i]):
        return True
    else:
        return False

inc = 1
speed = 100000
for j in range(1, U.shape[1]-2):
    if j % 100 == 0:
        print(j)
    for i in range(1, U.shape[2]-2):
        if island(U, V, j, i):
            # ========== Fixing all related with U =============
            if not island(U, V, j, i-1):  # If the 'left' cell is ocean then U += -1
                unBeachU[j, i] += -inc
                # unBeachU[j, i+1] += -inc
            if not island(U, V, j, i+1):  # If the 'right' cell is ocean, then U += 1
                unBeachU[j, i] += inc
                # unBeachU[j, i-1] += inc
            # ========== Fixing all related with V =============
            if not island(U, V, j + 1, i):  # Up cell, then V += 1
                unBeachV[j, i] += inc
                # unBeachV[j-1, i] += inc
            if not island(U, V, j - 1, i):  # Down cell, then V += - 1
                unBeachV[j, i] += -inc
                # unBeachV[j+1, i] += -inc
            # ========== Fixing all related with U and V =============
            if not island(U, V, j+1, i+1):  # If the 'upper right' cell is ocean,
                unBeachU[j, i] += inc
                unBeachV[j, i] += inc
                # unBeachU[j, i-1] += inc
                # unBeachV[j, i-1] += inc
            if not island(U, V, j+1, i-1):  # If the 'upper left' cell is ocean,
                unBeachU[j, i] += -inc
                unBeachV[j, i] += inc
                # unBeachU[j-1, i+1] += -inc
                # unBeachV[j-1, i+1] += inc
            if not island(U, V, j - 1, i + 1):  # If the 'lower right' cell is ocean,
                unBeachU[j, i] += inc
                unBeachV[j, i] += -inc
                # unBeachU[j+1, i-1] += inc
                # unBeachV[j+1, i-1] += -inc
            if not island(U, V, j - 1, i - 1):  # If the 'lower left' cell is ocean,
                unBeachU[j, i] += -inc
                unBeachV[j, i] += -inc
                # unBeachU[j+1, i+1] += -inc
                # unBeachV[j+1, i+1] += -inc
            vres = 1
            unBeachV[j, i] = speed*vres*unBeachV[j, i]/max(np.abs(unBeachV[j, i]), 1)
            # unBeachV[j+1, i+1] = vres*unBeachV[j+1, i+1]/max(np.abs(unBeachV[j+1, i+1]), 1)
            # unBeachV[j-1, i-1] = vres*unBeachV[j-1, i-1]/max(np.abs(unBeachV[j-1, i-1]), 1)
            # unBeachV[j+1, i-1] = vres*unBeachV[j+1, i-1]/max(np.abs(unBeachV[j+1, i-1]), 1)
            # unBeachV[j-1, i+1] = vres*unBeachV[j-1, i+1]/max(np.abs(unBeachV[j-1, i+1]), 1)

            ures = 1
            unBeachU[j, i] = speed*ures*unBeachU[j, i]/max(np.abs(unBeachU[j, i]), 1)
            # unBeachU[j+1, i+1] = ures*unBeachU[j+1, i+1]/max(np.abs(unBeachU[j+1, i+1]), 1)
            # unBeachU[j-1, i-1] = ures*unBeachU[j-1, i-1]/max(np.abs(unBeachU[j-1, i-1]), 1)
            # unBeachU[j+1, i-1] = ures*unBeachU[j+1, i-1]/max(np.abs(unBeachU[j+1, i-1]), 1)
            # unBeachU[j-1, i+1] = ures*unBeachU[j-1, i+1]/max(np.abs(unBeachU[j-1, i+1]), 1)

coords = {'lon': dataArrayLonF,
          'lat': dataArrayLatF}

dataArrayUnBeachU = xr.DataArray(unBeachU, name='unBeachU', dims=('lat', 'lon'))
dataArrayUnBeachV = xr.DataArray(unBeachV, name='unBeachV', dims=('lat', 'lon'))

dataset = xr.Dataset()
dataset[dataArrayLonF.name] = dataArrayLonF
dataset[dataArrayLatF.name] = dataArrayLatF
dataset[dataArrayUnBeachU.name] = dataArrayUnBeachU
dataset[dataArrayUnBeachV.name] = dataArrayUnBeachV
dataset.to_netcdf(path=join(data_dir, '..',F'unbeaching{speed}ms.nc'), engine='scipy')


datasetM
# for j in range(1, U.shape[1]-2):
#     for i in range(1, U.shape[2]-2):
#         if island(U, V, j, i):
#             if not island(U, V, j, i-1):
#                 unBeachU[j, i] = -1
#                 unBeachU[j+1, i] = -1
#             if not island(U, V, j, i+1):
#                 unBeachU[j, i+1] = 1
#                 unBeachU[j+1, i+1] = 1
#             if not island(U, V, j-1, i):
#                 unBeachV[j, i] = -1
#                 unBeachV[j, i+1] = -1
#             if not island(U, V, j+1, i):
#                 unBeachV[j+1, i] = 1
#                 unBeachV[j+1, i+1] = 1
#             if not island(U, V, j, i-1) and not island(U, V, j+1, i) and island(U, V, j+1, i-1):
#                 print('Watch out: one cell width land [%d %d]: %g %g' %
#                       (j, i, dataArrayLonF[i], dataArrayLatF[j]))
#             if not island(U, V, j, i+1) and not island(U, V, j+1, i) and island(U, V, j+1, i+1):
#                 print('Watch out: one cell width land [%d %d]: %g %g' %
#                       (j, i, dataArrayLonF[i], dataArrayLatF[j]))
#             if not island(U, V, j, i-1) and not island(U, V, j-1, i) and island(U, V, j-1, i-1):
#                 print('Watch out: one cell width land [%d %d]: %g %g' %
#                       (j, i, dataArrayLonF[i], dataArrayLatF[j]))
#             if not island(U, V, j, i+1) and not island(U, V, j-1, i) and island(U, V, j-1, i+1):
#                 print('Watch out: one cell width land [%d %d]: %g %g' %
#                       (j, i, dataArrayLonF[i], dataArrayLatF[j]))
