"""
Created on Mon Jul 17 15:19:53 2023

@author: Lyric Haylow
Averaging some data, putting two dataframes with that data together, and finding the differences. 
Some work likely done on Excel
"""
import pandas as pd
import os

### Main file, run in terminal
if __name__ == '__main__':
    os.chdir('C:\\Users\lyrich237339\Documents\QuickWorkFarnaz')
    jordanDF = pd.read_csv('JordanDF.csv')
    seriDF = pd.read_csv('SeriDF.csv')
    
    # print(len(jordanDF.index)) # 15103
    # print(len(seriDF.index)) # 13441
    
    #Generating means for each file part, already accomplished
    
    if 'Unnamed:0' in jordanDF:
        jordanDF = jordanDF.drop('Unnamed:0')
    new_Jordan = jordanDF.iloc[0:, [3,4,5,6,7,8,9,10,11,12]]
    print(new_Jordan)
    jordanDF['AverageJordan'] = new_Jordan.mean(axis = 1)
    # jordanDF = jordanDF.drop('Unnamed:0')
    jordanDF.to_csv('JordanDF.csv')
    print(jordanDF)
    
    if 'Unnamed:0' in seriDF:
        seriDF = seriDF.drop('Unnamed:0')
    new_Seri = seriDF.iloc[0:, [3,4,5,6,7]]
    seriDF['AverageSeri'] = new_Seri.mean(axis = 1)
    seriDF.to_csv('SeriDF.csv')
    
    
    both_combined = jordanDF.iloc[:, [0,1]]
    both_combined = pd.merge(jordanDF, seriDF, on=['Number of Bus', 'ID'])
    
    
    both_combined.to_csv('Put_together_averages.csv')
    print(len(both_combined.index))
    
    

    
 # 5255
 # 12269