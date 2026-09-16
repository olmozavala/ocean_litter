"""Command-line entry point for fresh or restartable surface-transport runs.

Usage: python 1_WorldLitter.py START END WINDS DIFFUSION UNBEACHING NAME
       [RESTART_FILE EXECUTION_DAYS]
Dates must use YYYY-MM-DD:HH. Supply both optional arguments for segmented runs.
A missing restart path starts a fresh release. See Docs/CODE_GUIDE.md for setup
and the existing WorldLitter/GlobalModel configuration mismatch.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Mapping


from parcels.scripts import *
from datetime import timedelta, datetime
from os.path import join
from config.params import WorldLitter
from config.MainConfig import get_op_config
import sys
import os
from utils.several_utils import get_file_name, str2bool
from models.models import sequential

try:
    from mpi4py import MPI
except:
    MPI = None

time_format = "%Y-%m-%d:%H"
time_format_red = "%Y_%m_%d"

def runWithRestart(
    execution_days: int,
    config: Mapping[Enum, Any],
    start_date: datetime,
    end_date: datetime,
    winds: bool,
    diffusion: bool,
    unbeaching: bool,
    name: str,
    restart_file: str = '',
) -> None:
    """Execute successive segments, restarting from each preceding output.

    Callers must provide positive ``execution_days`` and end_date > start_date;
    these preconditions are not checked here. The final segment is shortened
    to end_date. An existing restart_file seeds the first segment; an empty or
    missing path starts a fresh release. Later restart filenames combine
    output_folder, get_file_name(), and config's output_file suffix.

    Adjacent segments share a boundary timestamp. This function writes separate
    outputs and synchronizes MPI ranks; use 2_MergeRuns.py to merge them.
    """
    part_n = 0

    # =================== Computing all the models in 'batches' =====================

    # --------- First run without restart file ----------
    cur_end_date = min(start_date + timedelta(days=execution_days), end_date)
    cur_name = get_file_name(name, start_date, cur_end_date, part_n)
    print(F"{start_date.strftime(time_format)} {cur_end_date.strftime(time_format)} winds={winds} diff={diffusion} " \
          F"unbeaching={unbeaching} name={cur_name}")

    # In this case we run our first set of dates from a restart file
    if (restart_file != '') and (os.path.exists(restart_file)):
        sequential(start_date, cur_end_date, config, cur_name, winds=winds, unbeaching=unbeaching, diffusion=diffusion,
                   restart_file=restart_file)
    else:
        sequential(start_date, cur_end_date, config, cur_name, winds=winds, unbeaching=unbeaching, diffusion=diffusion)

    if MPI:
        print(F"----- Waiting for all proc to finish.....", flush=True)
        MPI.COMM_WORLD.Barrier()

    # # --------- Iterate over all the rest of the models, specify the resart file in each case
    while(cur_end_date < end_date):
        prev_start_date = start_date
        prev_end_date = cur_end_date
        start_date = cur_end_date  # Share the boundary observation; the merger removes its duplicate.
        cur_end_date = min(start_date + timedelta(days=execution_days), end_date)
        # Define the restart file to use (previous output file)
        restart_file = join(config[WorldLitter.output_folder], F"{get_file_name(name, prev_start_date, prev_end_date, part_n)}{config[WorldLitter.output_file]}")


        print(F" ================================================================================= ")
        print(F" ================================================================================= ")
        print(F" ================================================================================= ")

        # Define the new output file name
        part_n += 1
        cur_name = get_file_name(name, start_date, cur_end_date, part_n)
        print(F"{start_date.strftime(time_format)} {cur_end_date.strftime(time_format)} winds={winds} diff={diffusion} " \
          F"unbeaching={unbeaching} name={cur_name}")
        sequential(start_date, cur_end_date, config, cur_name, winds=winds, unbeaching=unbeaching, diffusion=diffusion, restart_file=restart_file)

        # Wait for this segment's output before opening it as the next restart.
        if MPI:
            print(F"----Waiting for file to be saved proc {MPI.COMM_WORLD.Get_rank()} ... -------------", flush=True)
            MPI.COMM_WORLD.Barrier()
            print("Done!", flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 6:
        # Print all the arguments received
        print("Number of arguments: ", len(sys.argv), "arguments.")

        start_date = datetime.strptime(sys.argv[1], "%Y-%m-%d:%H")
        end_date = datetime.strptime(sys.argv[2], "%Y-%m-%d:%H")
        winds = str2bool(sys.argv[3])
        diffusion = str2bool(sys.argv[4])
        unbeaching = str2bool(sys.argv[5])
        name = sys.argv[6]
        config = get_op_config()

        print(F"Start date: {start_date} End date: {end_date} winds={winds} diffusion={diffusion} unbeaching={unbeaching}")
        print(F"Name: {name}")

        if len(sys.argv) >= 8:
            restart_file = sys.argv[7]
            execution_days = int(sys.argv[8])
            if os.path.exists(restart_file):
                print(F"Running from restart ({execution_days})!!!!!  {restart_file} ")
                runWithRestart(execution_days, config, start_date, end_date, winds, diffusion, unbeaching, name, restart_file=restart_file)
            else:
                print(f"WARNING Path doesn't exist, running without restart: {restart_file}")
                print("Running with restart. This is the first time step (without restart)!!!!!")
                runWithRestart(execution_days, config, start_date, end_date, winds, diffusion, unbeaching, name)
        else:
            # Running without restart file
            print("Running without restart!!!!!")
            sequential(start_date, end_date, config, name, winds=winds, unbeaching=unbeaching, diffusion=diffusion)
