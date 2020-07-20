#!/bin/bash

cmd="rm Merge_20*"
echo $cmd
`$cmd`

cmd="rm run20*"
echo $cmd
`$cmd`

cmd="rm CurrentRun20*"
echo $cmd
`$cmd`

cmd="rm slurm-*"
echo $cmd
`$cmd`

