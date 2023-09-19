# -*- coding: utf-8 -*-
"""
Created on Mon May 23 14:08:05 2022

@author: Olivier
"""

# imports
    # Use Easy OCR for 10 first frame_index, NO index from METADATA
    
from pathlib import Path
import numpy as np
import cv2
from sklearn.linear_model import LinearRegression
# import ffmpeg
import os
import matplotlib.pyplot as plt
from tqdm.notebook import tqdm, tnrange
from sklearn.decomposition import FastICA
from sklearn.cluster import KMeans
import pandas as pd

# directories
    # Dio
    # where to save rgb
basepath = Path('D:\Hexmaze\maze_videos')
videos = list(sorted(basepath.glob('eye*.mp4')))
metadata = list(sorted(basepath.glob('eye*.meta')))


# functions 

def Sync_Ts(metadata):
    data = Read_Meta(metadata)
    Corrected_ts = Correct_gpu_cpu(data['callback_gpu_ts'], data['callback_clock_ts'])
    # plt.plot(data['callback_gpu_ts'])
    # plt.plot(data['callback_clock_ts'])
    return Corrected_ts, data
    

def Read_Meta(metadata):
    data = np.genfromtxt(metadata, delimiter=',', names=True)
    return data

def Correct_gpu_cpu(gpu, cpu):
    reg = LinearRegression().fit(gpu.reshape(-1, 1), cpu)
    reg_ts = reg.predict(gpu.reshape(-1, 1))-cpu
    offset = reg_ts[:1000].mean()
    Corr_ts = reg_ts - offset
    return Corr_ts


# DETECT_LED_CENTER (ffmpeg)

def Get_LED_center():
    crop_instruct = Path(basepath / videos[0].name[6:]).with_suffix('.led_crop')
    print(crop_instruct, "-- Exists:", crop_instruct.exists())
    return crop_instruct

# Crop and to RGB

def LED_to_RGB(crop_instruct):
    with open(crop_instruct) as f:
        crop_txt = f.readlines()

    overwrite = False
    crop = 16
    FFMPEG_CMD = 'ffmpeg -hide_banner -y -i "{infile}" -vf crop={crop}:{crop}:{x}:{y} -c:v rawvideo -pix_fmt {fmt} "{outfile}"'
    formats = {'rgb': 'rgb24'}  # , 'yuv': 'yuv444p'
    for line in tqdm(crop_txt):
        try:
            v, x, y = line.split(',')
            x, y = int(x), int(y)
        except ValueError:
            print("Faulty line:", line, 'Maybe led coordinates are missing?')
            break
        
        infile = basepath / Path(v).name
        print(infile)
        #print(v, infile.exists(), x, y)
        for ext, fmt in formats.items():
            outfile = basepath / Path(v).with_suffix('.'+ext).name
            print(outfile)
            if overwrite or not outfile.exists():
                cmd = FFMPEG_CMD.format(infile=str(infile), crop=crop, x=x-crop//2, y=y-crop//2, fmt=fmt, outfile=str(outfile))
                os.system(cmd)

# ICA 

def ICA_LED():
    nc = 3
    ica = FastICA(n_components=nc, random_state=0)
    X = rgb_frames.reshape(rgb_frames.shape[0], -1).astype(float)
    demixed = ica.fit_transform(X)
    # mix_matrix = ica.mixing_
    
    # N = 2000
    # fig, ax = plt.subplots(2, figsize=(28, 8), sharex=True)
    # col = ['r', 'g', 'b']
    # for n in range(3):
    #     ax[0].plot((rgb_frames[:N,:,:,n].astype(float)*hv_mask).mean(axis=1).mean(axis=1)+10*n, c=col[n])
    #     ax[1].plot(demixed[:N,n]+0.007*n, c=f'C{2-n}')
    
    Blue_LED, Red_LED = LED_quality(demixed)
    
    return Blue_LED, Red_LED




def LED_quality(demixed):
    
    # Function to define which ICA component correspond to LED signal and which is noise, so we can use the good signals (function to be updated)
    
    eD = 0.5
    dD = np.zeros(demixed.shape[1])  # distance to expected Duty cycle of 0.5
    ef_red = 0.5
    df_red = np.zeros(demixed.shape[1])  # distance to expected frequency of 0.5 Hz
    ef_blue = 2.5
    df_blue = np.zeros(demixed.shape[1])  # distance to expected frequency of 2.5 Hz
    
    # fig, ax = plt.subplots(1, 2, figsize=(24, 8))
    
    kmeans = []
    
    for n in range(demixed.shape[1]):
        km = KMeans(n_clusters=2, random_state=0).fit(demixed[:, n].reshape(-1, 1))
        y_km = km.predict(demixed[:, n].reshape(-1, 1))
        kmeans.append(y_km)
        centers = km.cluster_centers_
        
        # check center location, flip polarity if necessary to match pulse polarity
        if centers[0] > centers[1]:
            print('flip!', centers)
            y_km = np.abs(y_km-1)
    
    #     ax[0].plot(y_km[:100]+1.2*(2-n))
    #     duty_cycle = y_km.sum()/len(y_km)
    #     freq = (np.diff(y_km)>0).sum()/len(y_km) * 30
    #     dD[n] = abs(eD-duty_cycle)
    #     df_red[n] = abs(ef_red - freq)
    #     df_blue[n] = abs(ef_blue - freq)
    #     print(f'D={duty_cycle*100:.2f}%, f={freq:.2f} Hz')
    # ax[1].matshow(np.c_[dD<eD/10, df_red<ef_red/10, df_blue<ef_blue/10])
    # ax[1].set_xticks(range(3))
    # ax[1].set_xticklabels(['Duty cycle OK', 'frequency Red', 'frequency Blue'])
    # print(f'Expected D={eD*100}%, f_red={ef_red} Hz, f_blue={ef_blue} Hz')
    
    return df_blue, df_red



# Center of mass 




# main

# if __name__ == "__main__":
    
crop_instruct = Get_LED_center()
LED_to_RGB(crop_instruct)   
    

for m in range(len(metadata)) :
    # correct the timestamps from the metadata
    timestamps, data = Sync_Ts(metadata[m])
    plt.plot(timestamps)
    
    # Get LED states from the RGB files
    rgb_frames = np.fromfile(videos[m].with_suffix('.rgb'), dtype=np.uint8).reshape(-1, 16, 16, 3)
    hsv_frames = np.zeros_like(rgb_frames)
    for n in range(rgb_frames.shape[0]):
        hsv_frames[n,:,:,:] = cv2.cvtColor(rgb_frames[n,:,:,:], cv2.COLOR_RGB2HSV).astype(float)
    hv = hsv_frames[:,:,:,1].astype(float) * hsv_frames[:,:,:,2].astype(float)
    hv_mask = hv.mean(axis=0)
    hv_mask = (hv_mask -hv_mask.min()) / (hv_mask.max() - hv_mask.min())
    hvs = hv.mean(axis=1).mean(axis=1)
    
    Blue_ICA_LED, Red_ICA_LED = ICA_LED()
    
    break
    
    # # Opening the video 
    # cap = cv2.VideoCapture(videos[m].as_posix())
    
    # while (cap.isOpened()):

    #     res, frame = cap.read() # Read Current Frame
    #     frame_index = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) # Current Frame Index

    # TO DO (in iter):
        # Identify Blue and red ICA signals and save them 
        # update the functions in order to use the one ronny created 

    


# Out of iter :

# Load all LED ICA signals

# Find center of Mass for both the ICA signals (x12) and the DIO (x1)

# FInd offset and drift between LED and DIO

# Correct ts 

######################

# Change Ts from the tracker

  