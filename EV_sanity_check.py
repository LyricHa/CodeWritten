"""
Created on Fri Jul 21 13:33:21 2023

@author: Lyric Haylow
To compare the df_max_min_avg_MW files across the scenarios and ensure they're varying
"""
import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import tqdm
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
        
        ### Copys all the LoadMW files together
        # before_path = str(os.getcwd()) + '\\Load_MW.csv'
        # new_path = 'D:\\Full-Co-Simulation\\Co-Simulation-Results\\Aug. 6\\All_total_MWs\\Load_MW_scen_' + str(actual) + '.csv'
        # shutil.copyfile(before_path, new_path)

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
    # os.chdir('D:\\Full-Co-Simulation\\Co-Simulation-Results\\Aug. 6\\Old_Data_No_Cost') # For the server
    
    
    ### Cleans up files and puts them into list
    fileSort = []
    All_MWs_path = str(os.getcwd()) + '\\All_total_MWs'
    for fname in walk_through_files(All_MWs_path):
        fileSort.append(fname)
    fileSort.sort(key=lambda s: int('_'.join(c for c in s if c.isdigit()))) # Sorts the files numerically
    
    ### Begins creation of mega file
    os.chdir(All_MWs_path)
    temp = pd.read_csv('Load_MW_scen_3.csv')
    names = temp.columns.values[4:]
    names = np.insert(names, 0, 'Scenario')
    names = np.append(names, 'total_MW_summed')
    big_mama = pd.DataFrame(columns = names)
    
    scen_count = 1
    for stuff in fileSort:
        summed_list = []
        current = pd.read_csv(stuff)
        for column in current[4:28]:
            summed_list.append(current[column].sum())
        summed_list = summed_list[4:]
        summed_list = np.append(summed_list, sum(summed_list))
        summed_list = np.insert(summed_list, 0, scen_count)
        big_mama.loc[len(big_mama)] = summed_list
        scen_count = scen_count + 1
        
    big_mama.to_csv('All_MWs_with_EV.csv')
    
        
        