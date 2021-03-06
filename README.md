Dependencies: To-add. 


# Hexmaze Rat scripts
Repository for Hexmaze Rat project. 

## Main scripts: :file_folder: 

## LFP analysis (Emanuele Ciardo)
_**Data preprocessing:**_ 

  * main.m : The script receives as an input an .mda file - which has already been downsampled - that the user can select once the pop-up is opened. The main action it perform are:
-select the NREM portion of the recording. This is done by loading a second file where the sleepscoring file “states” is stored

_**IC selection:**_ 
  
  *main_ica : The script receives as input the output of the script ‘main’. It has the purpose to assess which independent components are to be removed. Since this approach has been ruled out, this script should be greatly modified. Another purpose of this script is to select the channels of interest (1 for PFC, 1 for HPC)
 
_**Event detection:**_ 
  
  * main_event : The script receives as input the output of the script ‘main_ica’. It performs 2 actions:

-removes artefacts.  It is done in 2 ways: 1) for normal movement artefacts it relies on an amplitude-based threshold; 2) for the resetting artefact it relies on a slightly finer algorithm, which takes into account the second derivative of the signal and the distance between detected artefacts, thus exploting the periodic nature of the artefact

-parces the signal into NREM bouts. This step is required for the subsequent event detection

-event detection. The user can choose what to detect: ripples, spindles, delta or all of them. The user can then, while examining the plotted detections, decide to modify the thresholds for the detection.




**Data analysis:**_ 
  
  * main_analysis: performs basic analysis: counting of the events and detection of sequences and cooccurrences of events

## Spikesorting : (Kayvan Combadiere) :file_folder: 

_**Square Shape Artefact removal:**_ 
  
  * Preprocessing_squareArtefact.py 

This file will performe concatenation and removal of the "square shape artefact". Depending on the size of the files it use a lot of memory usage.
This Python script works by concatenating the file 

File to preprocess should be in 3 different Folder :
  * mda_extracted_presleep
  * mda_extracted_maze
  * mda_extracted_postsleep

Each folder the mda extraction from trode of the files.

The script will ask : the directory of those folder, which rat, on what study day and the TNU number of the rat.

It will create a new folder named preprocess with the concated and preprocess file in it group by rat and studyday.

_**Detrending:**_ 

  * TestChronux.m

This process will detrend the signal of a recording. This MATLAB script use the local detrend function from Chronux to create a linear regression
on a moving local window of 0.1 second

How to Use it :
- decompress the folder chronux2.12. in the folder

- In matlab go to your directory with the function, add the chronux folder and subfolder to the path.

- Change the directory to the recording (MDA file) of the file you want to detrend in sig = readmda('PATH').

- Change the name of the output recording file

_**Spike sorting:**_ 

  * scriptConsensus.py

This script will do the spike sorting.The Python script use spikeinterface library to implement a consensus between MountainSort4 IronClust and tridesclous.(Further Sorter can be installed). The output of this file is a folder for PHY visualisation and manual curation.

How to Use it :
- Change the list_tetrode[] with the number of tetrode you want to use.

- Change the path to the recording (MDA file)
