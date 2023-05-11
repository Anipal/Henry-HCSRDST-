import geopandas
import pandas as pd
import numpy as np
import os

#Path to shapfile
path = os.getcwd() + '\\Input Shapefiles\\Parcels.shp'
#Read in shapefile as geodataframe
df = geopandas.read_file(path)

#Generate scores with some sort of spatial component
df['score_vuln'] = np.random.uniform(low = 0, high = 0.75, size = df.shape[0])
df.loc[df['US_CONGRES'] == 10,'score_vuln'] = np.random.uniform(low = 0.5, high = 1, size = df.loc[df['US_CONGRES'] == 10,'score_vuln'].shape[0])

df['score_envi'] = np.random.uniform(low = 0.5, high = 1, size = df.shape[0])
df.loc[df['US_CONGRES'] == 10,'score_envi'] = np.random.uniform(low = 0, high = 0.6, size = df.loc[df['US_CONGRES'] == 10,'score_envi'].shape[0])

df['score_lu'] = np.random.uniform(low = 0, high = 0.2, size = df.shape[0])
df.loc[df['US_CONGRES'] == 10,'score_lu'] = np.random.uniform(low = 0.7, high = 1, size = df.loc[df['US_CONGRES'] == 10,'score_lu'].shape[0])

df['score_tran'] = np.random.uniform(low = 0, high = 1, size = df.shape[0])
df.loc[df['US_CONGRES'] == 10,'score_tran'] = np.random.uniform(low = 0, high = 1, size = df.loc[df['US_CONGRES'] == 10,'score_tran'].shape[0])

#Write file
outPath = os.getcwd() + '\\Output Shapefiles\\dummy_suitability.shp'
df.to_file(outPath)