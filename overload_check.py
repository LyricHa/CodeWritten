"""
Created on Mon Jul 24 13:12:33 2023

@author: Lyric Haylow
To sort through Overloads and compile them together, compare them, and find the worst cases
"""
import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import os
import shutil

def run_scen_iteration():
    numOfSims = 96
    for i in (range(numOfSims)): # Loops through all sims designated
        actual = i + 1 # starts at 1, not 0
        # cSim = '\D_Loads_' + str(actual) + '_simulation_output_combined_remap_D-mapped'
        cSim = '\\' + str(actual) + '_simulation_output_combined_remap_D_Loads'
        try: # Checks if the file is there, and if not then it continues to next file
            os.chdir(os.getcwd() + cSim) # Changes directory to each folder sim case
        except FileNotFoundError:
            continue
        
        os.chdir('D:\\Full-Co-Simulation\\Co-Simulation-Results\\Aug. 6')

# this function is primarily for walking through a bunch of folders and returning 
# the path of all the Excel files it finds in those folders.
def walk_through_files(path, file_extension='.csv'):
    # file_extension describes which kind of file you're looking for
   for (dirpath, dirnames, filenames) in os.walk(path):
      for filename in filenames:
         if filename.endswith(file_extension): 
            yield filename

### Main function to run, use in terminal
if __name__ == '__main__':
    os.chdir('C:\\Users\lyrich237339\Documents\EV_data_sorting') # Changes to the D directory, local use
    # os.chdir('D:\\Full-Co-Simulation\\Co-Simulation-Results\\Aug. 6') # For the server

    path_to_dig = "C:\\Users\lyrich237339\Documents\EV_data_sorting\\X1"
    fileSort = []
    for fname in walk_through_files(path_to_dig):
        fileSort.append(fname)
    fileSort.sort(key=lambda s: int('_'.join(c for c in s if c.isdigit()))) # Sorts the files numerically
        
    os.chdir(path_to_dig)
    holder = pd.read_csv('overloads_ev_p11rhs34_1247.csv')
    # holder = holder[(holder['%Normal'] > holder['%Emergency'])]
    # print(holder)
    # normal = holder.iloc[0, 6]
            
    col_names = holder.columns.values[:]
    col_names = np.insert(col_names, 0 , 'Parent_file')
    big_hubba = pd.DataFrame(columns = col_names)
            
    # test_df = pd.DataFrame(columns = col_names)
    # test  = []
    # test.append('overloads_ev_p112uhs14_1247.csv')
    # test.append(np.where(holder['%Normal']>holder['%Emergency'],))
            
    for file in tqdm(fileSort):
        cur_df = pd.read_csv(file)
        if len(cur_df) == 0:
            continue
                # if cur_df[' %Normal']:
                    # cur_df(columns={' %Normal':'%Normal', ' %Emergency':'%Emergency'}, inplace=True)
        cur_df.rename({' %Normal': '%Normal', ' %Emergency': '%Emergency'}, axis=1, inplace = True)
                # print(cur_df.columns.values)
                
        cur_df = cur_df[(cur_df['%Normal'] > cur_df['%Emergency'])] # If normal above emergency, disregard
        if len(cur_df) == 0:
            continue
        to_add_df = cur_df.assign(Parent_file = file)
        to_add_df = to_add_df[['Parent_file'] + [col for col in to_add_df.columns if col != 'Parent_file']]
        frames = [big_hubba, to_add_df]
        big_hubba = pd.concat(frames)
        # big_hubba.drop([' %Normal', ' %Emergency'], axis=1, inplace=True)
            # col_order = [0,1,2,3,4,5,6,10,11,7,8,9]
            # big_hubba = big_hubba[[big_hubba[i] for i in col_order]]
                
            
        big_hubba.to_csv('all_overloads_X1.csv')
        # os.chdir('../Overloads_EV')
            
   #  os.chdir('../Aug. 6')
    
    # 442
            
            
            
    # end

        
