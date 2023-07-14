#!/bin/bash
# Set the -e option
set -e
#python Video_LED_Sync_using_ICA.py -i './input_files' -o './outpath/'
#python join_views.py ./input_files/
python TrackerYolov3-Colab.py -i './input_files/stitched.mp4' -o './outpath/'
