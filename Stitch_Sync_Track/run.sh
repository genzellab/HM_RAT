#!/bin/bash
# Set the -e option
set -e
# First step extracts the DIO files from the ephys .rec files using Trodes v2.3.2 for Ubuntu 20.04
for i in `find . -wholename "$1/*.rec" -type f`; do
    ./Trodes_2-3-2_Ubuntu2004/trodesexport -dio -rec $i
done

# Comment the next line using "#" at the start to skip Synchronisation
python Video_LED_Sync_using_ICA.py -i $1 -o $2 -f 20000

# Comment the next line using "#" at the start to skip Stitching
python join_views.py ./input_files/

# Comment the next line using "#" at the start to skip Tracking
python TrackerYolov3-Colab.py -i $1'/stitched.mp4' -o '$2'
