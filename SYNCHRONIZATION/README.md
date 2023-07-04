## Synchronization files
[Description](https://docs.google.com/document/d/1C5po2i44sqhHxwp52voB_3vZT7CsPBjcpynkymEkAQY/edit)

For the LED ICA extraction there are some older versions from which the newest script was based on. 
The newest script is the Video_LED_Sync_using_ICA.py 
The notebook version for step by step debugging is Video_LED_Sync_using_ICA.ipynb

# - Video_LED_Sync_using_ICA.py and Video_LED_Sync_using_ICA.ipynb
Latest version of script and notebook
python Video_LED_Sync_using_ICA.py -i '/home/genzel/param/sync_inp_files' -o '/home/genzel/param/outpath/'

# - Extract_LEDs_28_01_2023.ipynb:
Older version. Compiled from previous code and scripts

# - Extract_LEDs (1).ipynb: 
Oldest version, has missing YUV and HSV methods.


# - Extract_LEDs_0519.ipynb:
If I'm not mistaken there was an LED that had a problem when trying to apply ICA so it needed a little polishing for that specific LED.


# - synch_editedbyOzge.py:
This file is based on the synchronization script, this is where the synchronization of the video and ephys should happen taking into account the results from the LED extraction files and the scripts needed for the synchronization from the ephys part.

# - synchronization.py:
Older version from which synch_editedbyOzge.py was based on.


## Needed files to run the scripts
The files needed to run the Extract_LEDs_28_01_2023.ipynb are the videos found at /media/genzel/Data/Hexmaze/maze_videos on the Ireland pc.
