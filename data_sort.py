import time
import pyautogui as py
import pandas as pd
import matplotlib.pyplot as plt
import tqdm
import os



# this function is primarily for walking through a bunch of folders and returning 
# the path of all the Excel files it finds in those folders.
def walk_through_files(path, file_extension='.csv'):
    # file_extension describes which kind of file you're looking for
   for (dirpath, dirnames, filenames) in os.walk(path):
      for filename in filenames:
         if filename.endswith(file_extension): 
            yield filename
            

def find_values_opf(inputFrame, typeValue):
    
    df_max_min_avg = inputFrame.iloc[:, [0, 1, 2]]
    max_vals = []
    max_times = []
    min_vals = []
    min_times = []
    avg_vals = []
    
    for i in range(len(inputFrame)):
        ### MW list making
        load_list = inputFrame.iloc[i, 3:].values.tolist()
        max_vals.append(max(load_list))
        max_times.append(load_list.index(max(load_list)) + 1)
        
        min_vals.append(min(load_list))
        min_times.append(load_list.index(min(load_list)) + 1)
        
        avg_vals.append(sum(load_list)/len(load_list))
    
    df_max_min_avg['Max_' + str(typeValue)] = max_vals
    df_max_min_avg['Max_Time_' + str(typeValue)] = max_times
    df_max_min_avg['Min_' + str(typeValue)] = min_vals
    df_max_min_avg['Min_Time_' + str(typeValue)] = min_times
    df_max_min_avg['Avg_' + str(typeValue)] = avg_vals
    
    df_max_min_avg.to_csv('df_max_min_avg_' + str(typeValue) + '.csv')
    
    # print(df_max_min_avg)

### Currently outputs file that has all coords from hours listed for comparison
def opf_compare_coords(filesToCheck):
    total_lat = pd.DataFrame()
    total_long = pd.DataFrame()

    holder = pd.read_csv('opf_load_data_X1.csv')
    total_lat['SubNum'] = pd.Series(holder['SubNum'])
    total_long['SubNum'] = pd.Series(holder['SubNum'])

    counter = 0
    for file in filesToCheck: # Going through files in correct order now
        counter = counter + 1 # for tracking the 24 lats and longs
        
        cur_df = pd.read_csv(file)
        cur_df = cur_df.rename(columns={"Latitude:1":"Lat" + str(counter), "Longitude:1": "Long" + str(counter)})
        lat_to_add = cur_df["Lat" + str(counter)]
        long_to_add = cur_df["Long" + str(counter)]

        total_lat = total_lat.join(lat_to_add)
        total_long = total_long.join(long_to_add)
    
    for column in total_lat: # Checks all lats vs a single one and returns how many dont match, should be 1
        if(total_lat['Lat1'].equals(total_lat[column])):
            pass
        else:
            print("This doesn't match others (lat): " + str(column))
            
    for column in total_long: # Checks all longs vs a single one and returns how many dont match, should be 1
        if(total_long['Long1'].equals(total_long[column])):
            pass
        else:
            print("This doesn't match others (long): " + str(column))
            
    ### Optional conversion of dataframes to csv
    # cwd_held = os.getcwd()
    # os.chdir('..')
    # total_lat.to_csv('lats_compiled.csv')
    # total_long.to_csv('longs_compiled.csv')
    # os.chdir(cwd_held)

### Currently compiles all the loads across 24 hours into one dataframe for use, returns said dataframe
def opf_compile_loads(filesToCompile, whereToGo = '/OPF'):
    os.chdir(os.getcwd() + whereToGo)
    holder = pd.read_csv('opf_load_data_X1.csv')
    total_loads = holder.iloc[:, [1, 7, 8]]
    total_loads = total_loads.rename(columns = {"Latitude:1":"Lat", "Longitude:1":"Long"})
    # print(total_loads) # before loads added
    
    counter = 0
    for file in fileSort: # Going through files in correct order now
        counter = counter + 1
        # print(file)
        
        cur_df = pd.read_csv(file)
        cur_df = cur_df.rename(columns={"LoadMW":"LoadMW_" + str(counter), 
                                        "LoadMVR":"LoadMVR_" + str(counter),
                                        "BusPUVolt":"BusPUVolt_" + str(counter)})
        MW_to_add = cur_df["LoadMW_" + str(counter)]
        MVR_to_add = cur_df["LoadMVR_" + str(counter)]
        PU_to_add = cur_df["BusPUVolt_" + str(counter)]
        
        total_loads = total_loads.join(MW_to_add)
        total_loads = total_loads.join(MVR_to_add)
        total_loads = total_loads.join(PU_to_add)
    
    ### Optional conversion of dataframes to csv
    os.chdir('..')
    total_loads.to_csv('total_loads_compiled.csv')
    
    ### Optional return if desired
    # return total_loads

def do_it_all(filesSorted, folderToSearch = '\OPF'):
    opf_compile_loads(filesSorted, folderToSearch)
        
    all_loads = pd.read_csv('total_loads_compiled.csv')
    load_MW = all_loads.iloc[:, [1, 2, 3]]
    load_MVR = load_MW
    load_BusPU = load_MW
    for column in all_loads:
        works = all_loads[column]
        if 'Sub' in column or 'Lat' in column or 'Long' in column or 'Unn' in column:
            pass
        elif 'MW' in column:
            load_MW = load_MW.join(works)
        elif 'MVR' in column:
            load_MVR = load_MVR.join(works)
        elif 'Bus' in column:
            load_BusPU = load_BusPU.join(works)
        
    load_MW.to_csv('Load_MW.csv')
    load_MVR.to_csv('Load_MVR.csv')
    load_BusPU.to_csv('Load_BusPU.csv')
     
    find_values_opf(load_MW, 'MW')
    find_values_opf(load_MVR, 'MVR')
    find_values_opf(load_BusPU, 'BusPU')
    # print(df_max_min_avg_MW)
    print()
        
def combine_mma_files():
    first = pd.read_csv('df_max_min_avg_MW.csv')
    second = pd.read_csv('df_max_min_avg_MVR.csv')
    third = pd.read_csv('df_max_min_avg_BusPU.csv')
    
    combined_df = pd.concat([first, second.iloc[:, [4,5,6,7,8]]], axis = 1, join = 'outer')
    combined_df = pd.concat([combined_df, third.iloc[:, [4,5,6,7,8]]], axis = 1, join = 'outer')
    combined_df.drop(['Unnamed'], axis=1)
    combined_df.to_csv('combined_df_max_min_avg.csv')
    
    ### To remove the df_max_min_avg files should you desire
    os.remove('df_max_min_avg_MW.csv')
    os.remove('df_max_min_avg_MVR.csv')
    os.remove('df_max_min_avg_BusPU.csv')


### Main function to run, use in terminal
if __name__ == '__main__':
    # os.chdir('D:\\Aug.6') # Changes to the D directory, local use
    os.chdir('D:\\Full-Co-Simulation\\Co-Simulation-Results\\Aug. 6\\Old_Data_No_Cost') # For the server
    
    numOfSims = 1
    for i in (range(numOfSims)): # Loops through all sims designated
        actual = i + 1 # starts at 1, not 0
        # cSim = '\D_Loads_' + str(actual) + '_simulation_output_combined_remap_D-mapped'
        cSim = '\\' + str(actual) + '_simulation_output_combined_remap_D_Loads_'
        try:
            os.chdir(os.getcwd() + cSim) # Changes directory to each folder sim case
        except FileNotFoundError:
            continue
        folderToSearch = '\OPF'     # specific folder we want to search
        
        # Orders the files by number, not alphabetically
        fileSort = []
        for fname in walk_through_files(os.getcwd() + folderToSearch):
            fileSort.append(fname)
        fileSort.sort(key=lambda s: int('_'.join(c for c in s if c.isdigit()))) # Sorts the files numerically
        
        # os.chdir(os.getcwd() + folderToSearch)
        # opf_compare_coords(fileSort)
        do_it_all(fileSort, folderToSearch)
        # combine_mma_files()
        
        # print(os.getcwd())
        
        
        ### For plotting some stuff
        '''
        to_plot = pd.read_csv('combined_df_max_min_avg.csv')
        to_plot.plot(x='Max_Time_MW', y='Max_MW', kind = 'scatter', color = 'red')
        # plt.savefig('Max_MW_scatter.png')
        to_plot.plot(x='Min_Time_MW', y='Min_MW', kind = 'scatter', color = 'blue')
        # plt.savefig('Min_MW_scatter.png')
        
        to_plot.plot(x='Max_Time_MVR', y='Min_MW', kind = 'scatter', color = 'red')
        plt.savefig('Max_MVR_scatter.png')
        to_plot.plot(x='Min_Time_MVR', y='Min_MW', kind = 'scatter', color = 'blue')
        plt.savefig('Min_MVR_scatter.png')

        to_plot.plot(x='Max_Time_BusPU', y='Min_MW', kind = 'scatter', color = 'red')
        plt.savefig('Max_BusPU_scatter.png')
        to_plot.plot(x='Min_Time_BusPU', y='Min_MW', kind = 'scatter', color = 'blue')
        plt.savefig('Min_BusPU_scatter.png')
        
        plt.show()
        '''
        os.chdir('D:\\Aug.6') # Goes back to main directory for next loop, local use
        # os.chdir('D:\\Full-Co-Simulation\\Co-Simulation-Results\\Aug. 6') # For the server
