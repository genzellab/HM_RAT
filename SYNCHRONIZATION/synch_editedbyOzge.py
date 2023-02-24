#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 03:11:46 2022

@author: Ozge
"""

'''
INPUT: 
1.1) red_ica (x12)
1.2) blue_ica (x12)
1.3) corrected timestamps (x12) ... time_meta (for each eye)
2.1) path of dio timestamps ... dio_time_fname (for example: r'/media/genzel/Data/Hexmaze/Rat4_20201109/Rat4_20201109_maze.DIO/Rat4_20201109_maze.dio_MCU_Din1.dat')
2.2) path of red dio ... red_dio_fname (for example: r'/media/genzel/Data/Hexmaze/Rat4_20201109/Rat4_20201109_maze_merged.DIO/Rat4_20201109_maze_merged.dio_MCU_Din2.dat')
2.3) path of blue dio ... blue_dio_fname (for example: r'/media/genzel/Data/Hexmaze/Rat4_20201109/Rat4_20201109_maze_merged.DIO/Rat4_20201109_maze_merged.dio_MCU_Din1.dat')

PROCESSES:
1)EXTRACT_LED_INTENSITIES (x2 for blue_ica)
    1.1) merge timestamps (key) & red_ica in a dataframe (x12) .... df0, df1, df2, ...
    1.2) merge dataframes for all eyes in one list ... dfs
    1.3) merge the list and sort wrt 'key' and fill nan values with interpolated values ... df_final
    1.4) sum the red_ica values in the list along each eye ... df_total
    1.5) Threshold summed red ica to binarize it ... ica_thresh
    1.6) Save binarized and summed red ica and corresponding timestamps ... ica_red
    
2) EXTRACT_DIOS (adapted from script of Mutu & Juan)
    2.1) use the dio timestamp, red dio and blue dio and extract dio dataframes ... blue_DIO_df and red_DIO_df

3) EXTRACT CENTER OF MASS (COM) OF LED INTENSITIES AND DIOS (x2 for blue led)
    3.1) Find com of red_dio in dataframe ... com_dio
    3.2) Find com of red led intensity in dataframe using summed and binarized red ica ... com_ica

4) COMPARE COMS OF LED INTENSITIES AND DIOS (x2 for blue led)
    4.1) Visually determine initial pulses ... give an input quantity of shift (for example: 4) ... shift
    4.2) Align the beginning pulses of led intensities and dio ... com_dio2 & com_ica2 
    4.3) Find the difference between coms wrt timestamps ... com_diff
    
OUTPUT:
1) time shift between GPU and Spike Gadgets wrt pulse no ... com_diff
''' 

'''
# 1.1 red ICA (x12)
demixed = red_ica
for n in range(12):
    df_temp = pandas.DataFrame({'key' : [], "Red_LED_Intensity_%s" %(n) : []})
    df_temp['key'] = time_meta[0:(len(demixed[:N, n]-1))]
    df_temp["Red_LED_Intensity_%s" %(eye)] = demixed[:N, n]
    if n==0:
        df0 = df_temp
    if n==1:
        df1 = df_temp
    if n==2:
        df2 = df_temp
    if n==3:
        df3 = df_temp
    if n==4:
        df4 = df_temp
    if n==5:
        df5 = df_temp
    if n==6:
        df6 = df_temp
    if n==7:
        df7 = df_temp
    if n==8:
        df8 = df_temp
    if n==9:
        df9 = df_temp
    if n==10:
        df10 = df_temp
    if n==11:
        df11 = df_temp

        
# 1.2 Merge dataframes for all eyes in one list
dfs = [df0, df1, df2, df3, df4, df5, df6, df7, df8, df9, df10, df11]   


# 1.3 Merge the list and sort wrt 'key' and fill nan values with interpolated values
df_final = ft.reduce(lambda left, right: pd.merge(left, right, on='key', how='outer', suffixes=(None, None)), dfs)  
df_final = df_final.sort_values('key')
df_final.interpolate(inplace=True
                    ) 


# 1.4 sum the red ICA values in the list along each eye
for eye in range(12):
    # ax.plot(df_final['key'][:100], df_final["Red_LED_Intensity_%s" %(eye)][:100])
    df_total = df_total + df_final[f"Red_LED_Intensity_{eye}"]


# 1.5 Threshold summed red ICA to binarize it
ica_thresh = df_total.values > 0


# 1.6 Save binarized and summed red ICA and correspnding timstamps
ica_red = pandas.DataFrame({'Time_in_seconds' : [], 'ICA_red' : []})
ica_red.Time_in_seconds = df_final['key']
ica_red.ICA_red = ica_thresh
'''

# 2.1 Extract DIOS
from datetime import datetime , time , timedelta
import pandas as pd
import numpy as np
import re
def readTrodesExtractedDataFile(filename):
    with open(filename, 'rb') as f:
        # Check if first line is start of settings block
        if f.readline().decode('ascii').strip() != '<Start settings>':
            raise Exception("Settings format not supported")
        fields = True
        fieldsText = {}
        for line in f:
            # Read through block of settings
            if(fields):
                line = line.decode('ascii').strip()
                # filling in fields dict
                if line != '<End settings>':
                    vals = line.split(': ')
                    fieldsText.update({vals[0].lower(): vals[1]})
                # End of settings block, signal end of fields
                else:
                    fields = False
                    dt = parseFields(fieldsText['fields'])
                    fieldsText['data'] = np.zeros([1], dtype = dt)
                    break
        # Reads rest of file at once, using dtype format generated by parseFields()
        dt = parseFields(fieldsText['fields'])
        data = np.fromfile(f, dt)
        fieldsText.update({'data': data})
        return fieldsText
# Parses last fields parameter (<time uint32><...>) as a single string
# Assumes it is formatted as <name number * type> or <name type>
# Returns: np.dtype
def parseFields(fieldstr):
    # Returns np.dtype from field string
    sep = re.split('\s', re.sub(r"\>\<|\>|\<", ' ', fieldstr).strip())
    # print(sep)
    typearr = []
    # Every two elmts is fieldname followed by datatype
    for i in range(0,sep.__len__(), 2):
        fieldname = sep[i]
        repeats = 1
        ftype = 'uint32'
        # Finds if a <num>* is included in datatype
        if sep[i+1].__contains__('*'):
            temptypes = re.split('\*', sep[i+1])
            # Results in the correct assignment, whether str is num*dtype or dtype*num
            ftype = temptypes[temptypes[0].isdigit()]
            repeats = int(temptypes[temptypes[1].isdigit()])
        else:
            ftype = sep[i+1]
        try:
            fieldtype = getattr(np, ftype)
        except AttributeError:
            print(ftype + " is not a valid field type.\n")
            exit(1)
        else:
            typearr.append((str(fieldname), fieldtype, repeats))
    return np.dtype(typearr)
#Path to maze recording that contains the system time at creation information
dio_time_fname  = r'/media/genzel/Data/Hexmaze/Rat4_20201109/Rat4_20201109_maze.DIO/Rat4_20201109_maze.dio_MCU_Din1.dat'
dict_dio = readTrodesExtractedDataFile(dio_time_fname)
#Path to maze recording with headstage recording data
blue_dio_fname = r'/media/genzel/Data/Hexmaze/Rat4_20201109/Rat4_20201109_maze_merged.DIO/Rat4_20201109_maze_merged.dio_MCU_Din1.dat'
blue_dict_dio = readTrodesExtractedDataFile(blue_dio_fname)
blue_DIO = blue_dict_dio['data']
red_dio_fname = r'/media/genzel/Data/Hexmaze/Rat4_20201109/Rat4_20201109_maze_merged.DIO/Rat4_20201109_maze_merged.dio_MCU_Din2.dat'
red_dict_dio = readTrodesExtractedDataFile(red_dio_fname)
red_DIO = red_dict_dio['data']
sys_time = int(readTrodesExtractedDataFile(dio_time_fname)['system_time_at_creation'])/1000
timestamp_at_creation = int(readTrodesExtractedDataFile(dio_time_fname)['timestamp_at_creation'])#/1000
dt_object = datetime.utcfromtimestamp(sys_time)
# Get timestamps of Trodes signals
blue_DIO_ts = [((dt_object + timedelta(seconds = (i[0]-timestamp_at_creation)/ 30000)).timestamp() , i[1]) for i in blue_DIO]
red_DIO_ts = [((dt_object + timedelta(seconds = (i[0]-timestamp_at_creation)/ 30000)).timestamp() , i[1]) for i in red_DIO]
blue_DIO_df  = pd.DataFrame({"Time_Stamp_(DIO)" : [str(datetime.fromtimestamp(i[0]))[11:]  for i in blue_DIO_ts], "Time_in_seconds_(DIO)" : [str(i[0]) for i in blue_DIO_ts], "State": [i[1] for i in blue_DIO_ts]} )
red_DIO_df  = pd.DataFrame({"Time_Stamp_(DIO)" : [str(datetime.fromtimestamp(i[0]))[11:]  for i in red_DIO_ts], "Time_in_seconds_(DIO)" : [str(i[0]) for i in red_DIO_ts], "State": [i[1] for i in red_DIO_ts]} )

'''
# 3.1 find com of red DIO in dataframe
import pandas
com_dio = pandas.DataFrame({'Center_of_mass' : []})  
# for i in range(len(time_dio_r)):
if state_dio_r[0]==1:
    for i in range(2, len(state_dio_r), 2):
        com_dio.at[(i-2)/2, 'Center_of_mass'] = (time_dio_r[i]+time_dio_r[i-2])/2
else:
    for i in range(3, len(state_dio_r), 2):
        com_dio.at[(((i-1)/2)-1), 'Center_of_mass'] = (time_dio_r[i]+time_dio_r[i-2])/2        


# 3.2 find com of led intensity in dataframe using summed and binarized red ICA
time_ica = ica_red['Time_in_seconds']
ica_int = ica_red['ICA_red']
red_med = np.array(np.diff(ica_int))
red_med = np.append(0, red_med)
rising_edge_red = np.asarray(np.where(red_med==1)).flatten()
falling_edge_red = np.asarray(np.where(red_med==-1)).flatten()
com_ica = pandas.DataFrame({'Center_of_mass' : []})  
if time_ica[rising_edge_red[0]] < time_ica[falling_edge_red[0]]:  
    for i in range(min(len(rising_edge_red), len(falling_edge_red))):
        com_ica.at[i, 'Center_of_mass'] = (time_ica[rising_edge_red[i]]+time_ica[falling_edge_red[i]])/2
else:
    for i in range(min(len(rising_edge_red), len(falling_edge_red))):
        com_ica.at[i, 'Center_of_mass'] = (time_ica[rising_edge_red[i]]+time_ica[falling_edge_red[i+1]])/2


# 4.1 visually determine initial pulses
display(ica_red.head())
display(red_DIO_df.head())


#4.2 align the beginning pulses of led intensities and DIO
com_dio2 = np.array(com_dio)
com_ica2 = np.array(com_ica[shift:])


# 4.3 find the difference between coms wrt timestamps
com_diff = -com_ica2 + com_dio2
'''