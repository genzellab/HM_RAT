# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 14:23:54 2022

@author: olivier
"""

import cv2
import glob
import os
import numpy as np

# Getting videos from each eye 
path = r'E:\Documents\EPF\PFE\Work\Codes\check\Videos\*.mp4'
filelist = glob.glob(path)
filelist.pop() # removing the last video because in my file it is the Stitched video

# Where to save the overlay video and all the frames
dirOverlay = r'E:\Documents\EPF\PFE\Work\Codes\Overlayed'


# Settings for creating the stitched videos 
x = 91  # Number of pixel tp crop at the bottom and the top of the frame 
y = 98  # Number of pixel to crop at the left and the right of the frame 
p_overlay = 30 # number of pixel overlay
nbf = 10 # number of frame to record from the video to create the overlay one
Start_record = 20 # in frame, frame at which we will start to record the 'nbf' frames

# Creating variables
Frames = [[0 for x in range(nbf)] for y in range(12)] 
FFrames = [[0 for x in range(nbf)] for y in range(12)] 
lx = (800-2*x)
ly = (600-2*y)
len_c = 6*ly
len_r = 2*lx
Fstitched = np.zeros((2*len_r, len_c,3), dtype = 'uint8')
Mmask = []
OST = np.zeros((len_r, len_c,3), dtype = 'uint8')

# Dictionnary for corner eyes
d = {0 : ((y, x, y-p_overlay, x-p_overlay)),
     5 : ((y-p_overlay, x, y, x-p_overlay)),
     6 : ((y, x, y-p_overlay, x-p_overlay)),
     11 : ((y-p_overlay, x, y, x-p_overlay))}


def ffmpeg(cmd):
    os.system(cmd)
    
def Overlay(Frames): 
    # This function will crop the frames from each eye, taking the over into considaration
    for g in range(len(Frames[0])):
        for c in range(len(filelist)):    
            if c in d:
                FFrames[c][g] = Frames[c][g][d[c][1]:-d[c][3], d[c][0]:-d[c][2], :]
                if len(Mmask) < 12:
                    Mmask.append(np.ones((len(FFrames[c][g]), len(FFrames[c][g][0]), 3), dtype= 'uint8'))
            else :
                FFrames[c][g] = Frames[c][g][x:-(x-p_overlay),y-p_overlay:-(y-p_overlay),:]
                if len(Mmask) < 12:
                    Mmask.append(np.ones((len(FFrames[c][g]), len(FFrames[c][g][0]), 3), dtype= 'uint8'))
    return FFrames
    
def StitchedOverlay(FFrames, n, mask):

    Stitched = np.zeros((len_r, len_c,3), dtype = 'uint64')
    Stitched[:len(FFrames[0][n]),:len(FFrames[0][1][n]),:] += FFrames[0][n]
    Stitched[:len(FFrames[0][n]),ly-p_overlay:p_overlay + 2*ly,:] += FFrames[1][n]
    Stitched[:len(FFrames[0][n]),2*ly-p_overlay:p_overlay + 3*ly,:] += FFrames[2][n]
    Stitched[:len(FFrames[0][n]),3*ly-p_overlay:p_overlay + 4*ly,:] += FFrames[3][n]
    Stitched[:len(FFrames[0][n]),4*ly-p_overlay:p_overlay + 5*ly,:] += FFrames[4][n]
    Stitched[:len(FFrames[0][n]),5*ly-p_overlay:,:] += FFrames[5][n]
    Stitched[lx-p_overlay:,:len(FFrames[6][1][n]),:] += FFrames[6][n]
    Stitched[lx-p_overlay:,ly-p_overlay:p_overlay + 2*ly,:] += FFrames[7][n]
    Stitched[lx-p_overlay:,2*ly-p_overlay:p_overlay + 3*ly,:] += FFrames[8][n]
    Stitched[lx-p_overlay:,3*ly-p_overlay:p_overlay + 4*ly,:] += FFrames[9][n]
    Stitched[lx-p_overlay:,4*ly-p_overlay:p_overlay + 5*ly,:] += FFrames[10][n]
    Stitched[lx-p_overlay:,5*ly-p_overlay:,:] += FFrames[11][n]
    
    Stitched = Stitched*mask
    Stitched = Stitched.astype(np.uint8)
    filename = 'Frames_' + '{:03}'.format(n) + '.png'
    
    cv2.imwrite(filename, cv2.cvtColor(Stitched, cv2.COLOR_RGB2BGR))
    

    
#%% Main

# Getting the needed frames from each eye
for f in range(len(filelist)):
    cap = cv2.VideoCapture(filelist[f])
    while cap.isOpened():
        id = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        print(id)
        res, frame = cap.read() # Read Current Frame
        if not res or id > Start_record + 50 + nbf :
            break
        if Start_record <= id < Start_record + nbf:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            Frames[f][id-Start_record] = frame_rgb

FFrames = Overlay(Frames)

# Flipping the 6 lower cameras frames
for p in range(6):
    for s in range(len(Frames[0])):
        FFrames[6+p][s] = np.flip(FFrames[6+p][s], (0, 1))

# creating the mask, taking into consideration the overlay length
mask = np.zeros((len_r, len_c,3), dtype = 'uint8')
mask[:len(Mmask[0]),:len(Mmask[0][1]),:] += Mmask[0]
mask[:len(Mmask[0]),ly-p_overlay:p_overlay + 2*ly,:] += Mmask[1]
mask[:len(Mmask[0]),2*ly-p_overlay:p_overlay + 3*ly,:] += Mmask[2]
mask[:len(Mmask[0]),3*ly-p_overlay:p_overlay + 4*ly,:] += Mmask[3]
mask[:len(Mmask[0]),4*ly-p_overlay:p_overlay + 5*ly,:] += Mmask[4]
mask[:len(Mmask[0]),5*ly-p_overlay:,:] += Mmask[5]
mask[lx-p_overlay:,:len(Mmask[6][1]),:] += Mmask[6]
mask[lx-p_overlay:,ly-p_overlay:p_overlay + 2*ly,:] += Mmask[7]
mask[lx-p_overlay:,2*ly-p_overlay:p_overlay + 3*ly,:] += Mmask[8]
mask[lx-p_overlay:,3*ly-p_overlay:p_overlay + 4*ly,:] += Mmask[9]
mask[lx-p_overlay:,4*ly-p_overlay:p_overlay + 5*ly,:] += Mmask[10]
mask[lx-p_overlay:,5*ly-p_overlay:,:] += Mmask[11]

mask = np.where(mask == 4, 1/4, mask)
mask = np.where(mask == 3, 1/3, mask)
mask = np.where(mask == 2, 1/2, mask)

os.chdir(dirOverlay)
print('Starting to create Stitched Frames (Overlay)')

for n in range(nbf):
    StitchedOverlay(FFrames, n, mask)

# creating the video from the frames
ffmpeg('''ffmpeg -framerate 30 -i Frames_%03d.png -c:v libx264 -vf format=yuv420p Stitched_overlay.mp4''')
  





