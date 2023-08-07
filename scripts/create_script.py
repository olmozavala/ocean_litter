if __name__ == "__main__":
    for c_year in range(2010, 2020):
        for c_month in range(1, 13):
            print(F"scp -r /data/UN_Litter_data/output/TEN_YEARS/YesWinds_YesDiffusion_NoUnbeaching/TenYears_YesWinds_YesDiffusion_NoUnbeaching_{c_year}_{c_month:02d}.nc osz09@coaps.rcc.fsu.edu:~/scratch/TEN_YEARS/")


