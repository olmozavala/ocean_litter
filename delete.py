from __future__ import division
import struct
__author__="Olmo S. Zavala Romero"
import numpy as np


def testReadingFile():

    #-------- Reading file ---------
    # -------- This part is just to test the reading of a specific binary file
    # header_file = "/var/www/html/data/4/YesWinds_YesDiffusion_NoUnbeaching_2010_01.txt"
    # data_file = "/var/www/html/data/4/YesWinds_YesDiffusion_NoUnbeaching_2010_01.bin"
    header_file = "/home/olmozavala/Desktop/DELETE/YesWinds_YesDiffusion_NoUnbeaching_2010_01_01.txt"
    data_file = "/home/olmozavala/Desktop/DELETE/YesWinds_YesDiffusion_NoUnbeaching_2010_01_01.bin"
    f_header = open(header_file,'r')
    header_lines = f_header.readlines()

    f_data = open(data_file,'rb')
    for country_line in header_lines:
        split = country_line.split(',')
        name = split[0]
        continent = split[1]
        num_particles = int(split[2])
        time_steps = int(split[3])

        lats_bin = f_data.read(num_particles*time_steps*2)
        lons_bin = f_data.read(num_particles*time_steps*2)
        lats_int = struct.unpack(F"{num_particles*time_steps}h", lats_bin)
        lons_int = struct.unpack(F"{num_particles*time_steps}h", lons_bin)
        lats = np.array([lats_int])[0]/100
        lons = np.array([lons_int])[0]/100
        print(lats[0:3])
        print(lons[0:3])

    f_data.close()
    f_header.close()

if __name__ == "__main__":
    testReadingFile()
