import pandas as pd
import os


#Root path
root = '/mnt/c/Users/apal72/Documents/Anisha/data/productDownload_2022-10-12T110640'
#list of files to access
files = ['ACSST1Y2021.S1701-Data.csv','ACSST5Y2020.S1701-Data.csv','ACSST5Y2019.S1701-Data.csv','ACSST5Y2018.S1701-Data.csv','ACSST5Y2017.S1701-Data.csv','ACSST5Y2016.S1701-Data.csv']
df1 = pd.DataFrame(columns= ['NAME','S1701_C02_001E','S1701_C03_001E','YEAR'])
cols = ['NAME','S1701_C02_001E','S1701_C03_001E']
for i in files:
    df = pd.read_csv(os.path.join(root,i),usecols = cols,skiprows=[1])
    df['YEAR'] = i.split('Y')[-1].split('.')[0]
    df1 = pd.concat([df1, df], ignore_index=True)
df1.to_csv(os.path.join(root,'consolidated.csv'), encoding='utf-8', index=False)