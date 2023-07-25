"""
Created on Tue Jul 25 14:56:09 2023

@author: Lyric Haylow
Made to parse through a txt file that Dr. Farnaz gave me a sort by long, lat, and some descriptors
Bus number is also going to be introduced
"""

import os
import pandas as pd
import numpy as np
from tqdm import tqdm
import json

if __name__ == '__main__':
    os.chdir('C:\\Users\lyrich237339\Documents\QuickWorkFarnaz')
    
    cleaned_up = pd.DataFrame(columns=['Longitude','Latitude', 'City/Town', 'State', 'County', 'BusNum'])
    with open('24000_mods.txt') as f:
        for line in f.readlines():
            if(line[0].isdigit() or line.startswith('-') or line.startswith('<')):
                continue
            dict_string = line[14:]
            # print(dict_string)
            new_dude = dict_string.replace("'", '"')
            huh = json.loads(new_dude)
            # print(huh)
            list_to_add = []
            if line[6].isdigit():
                list_to_add.append(line[2:7]) 
                list_to_add.append(line[8:14])
            else:
                list_to_add.append(line[2:6])
                list_to_add.append(line[7:13])
            try:
                list_to_add.append(huh['city'])
            except:
                try: 
                    list_to_add.append(huh['town'])
                except:
                    list_to_add.append('N\A')
            list_to_add.append(huh['state'])
            list_to_add.append(huh['county'])
            list_to_add.append(0) # Accounts for BusNum missing right now
            # print(list_to_add)
            '''
            try:
                cleaned_up.iloc[counter, 'city'] = huh['city']
                cleaned_up.iloc[counter, 'state'] = huh['state']
                cleaned_up.iloc[counter, 'county'] = huh['county']
            except :
                pass
            '''
            cleaned_up.loc[len(cleaned_up)] = list_to_add
    cleaned_up.to_csv('24000_mods_cleaned.csv')
    f.close()

