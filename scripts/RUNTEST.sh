#!/bin/bash

sbatch  run_currents_and_wind_and_diffusion.sh
sbatch  run_currents_and_wind.sh
sbatch  run_currents_only.sh
sbatch  run_currents_and_diffusion.sh
