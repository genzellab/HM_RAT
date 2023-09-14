Dependencies: To-add. 

# Convertion from .rec to .mda
```
./trodesexport -mountainsort -rec /mnt/genzel/Rat/HM/Rat_HM_Ephys/Rat_HM_Ephys_Rat5_406576/Rat_HM_Ephys_Rat5_406576_20210614/Rat_Hm_Ephys_Rat5_406576_20210614_presleep/Rat_Hm_Ephys_Rat5_406576_20210614_presleep.rec -sortingmode 1
./trodesexport -mountainsort -rec
```

# DownsamplingMDAfile
DownsamplingMDAfile
## Installation 


# Hexmaze Rat scripts
Repository for Hexmaze Rat project. 

## Main scripts: :file_folder: 
```
pip install numpy
pip install pandas
pip install scipy
```

## LFP analysis (Emanuele Ciardo)
_**Data preprocessing:**_ 
You need to add the file mdaio to the python path

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

## Event Characteristics: Sara Rostami

_**Data pooling:**_ 
data from different study days for different rats are pooled in order to run the event_charachteristics script on it & extract the features from our raw data.

  * _pooling_data.m_ : The script receives the preprocessed data of rat 1, 2, 4, 7 and 8 for different study days and pools them in 6 files in *pre/post_condition.mat* format (`example: postsleep_homecage.mat`).


_**Event Characteristics Analysis:**_ 
by running the event_charachteristics script on the raw data, the features were extracted and saved in `X.mat`.

  * _making_event_characteristics_file.m_ : The script receives the feature extracted data of events (ripple,spindle and delta) and outputs the feature extracted data in _.csv_ format.
  * _violin_plots_ripple_events.ipynb_ : This notebook contains the violin plots of ripple events.
  * _model&test.ipynb_ : Exploratory/Predictive analysis of feature extracted ripple events, using correlation matrix, pairwise scatter plot and models like Decision Tree, Random Forest, SGBDT, and KNN.
  * _event_charachteristics_plots_ : This notebook contains a number of plots for the feature extracted events to compare and visualize the features in the 4 hour sleeping session after learning a new goal location.

these two documents contain the reports and plots of the above scripts:
* https://docs.google.com/document/d/1gvLbRoj9SJaflvzC6W12gw_GmWY8hxWR6e2fygoqZa0/edit#
* https://docs.google.com/document/d/1oe6Gip6X3RxoDDiwbFWX5XeOop_DhHowTUK5JEEMFok/edit#heading=h.2gazcsgmxkub
