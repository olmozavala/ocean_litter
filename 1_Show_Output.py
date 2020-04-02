from parcels import plotTrajectoriesFile
from datetime import datetime

today_str = datetime.today().strftime("%Y-%m-%d_%H_%M")
file_name = F'/home/data/UN_Litter_data/output/2020-04-02_18_01_output.nc'
plotTrajectoriesFile(file_name) # Plotting trajectories
plotTrajectoriesFile(file_name, mode='2d') # Plotting trajectories
# plotTrajectoriesFile(file_name, mode='hist2d') # Plotting trajectories
