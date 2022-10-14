import shapely
import geopandas as gpd 
import argparse
import pandas as pd
import fiona 
from centroid_coords import *
import pdb
import pandas as pd, numpy as np, matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from geopy.distance import great_circle
from shapely.geometry import MultiPoint
from sklearn.neighbors import NearestNeighbors

parser = argparse.ArgumentParser(description="Raster to shapefile")
parser.add_argument('--save_dir', type=str, default='/media/ssd1/data/sanborn',
                        help='put the path to root directory')
parser.add_argument('--centroid_change', type=str, default='pmap_dpn/',
                        help='put the path to save geojson')
parser.add_argument('--centroid_str', type=str, default='pmap_dpn/',help='put the path to image directory')
args = parser.parse_args()


kms_per_radian = 6371.0088
eps = 0.2 / kms_per_radian
ms = 10

collection_change = list(fiona.open(args.centroid_change,'r'))
collection_str = list(fiona.open(args.centroid_str,'r'))
df1_change = pd.DataFrame(collection_change)
df1_str = pd.DataFrame(collection_str)
df2_str = gpd.read_file(args.centroid_str)
df1_change_new_field = add_fields(df1_change, 1)
df1_str_new_field = add_fields(df1_str, 0)

df1_change_coords = add_coords(df1_change_new_field)
df1_str_coords = add_coords(df1_str_new_field)
df_combined = pd.concat([df1_change_coords, df1_str_coords], ignore_index=True)
# df_combined = pd.concat([df1_change_coords, df1_str_coords], ignore_index=True)
pdb.set_trace()
db = DBSCAN(eps=eps, min_samples=ms, algorithm='ball_tree', metric='haversine').fit(np.radians(df_combined[['lat','lon']]))
df_combined['cluster_labels'] = db.labels_
labels_change = np.unique(np.array(df_combined.iloc[:len(df1_change_coords)]['cluster_labels'])) 
df2_str['labels'] = df_combined.iloc[len(df1_change_coords):]['cluster_labels']
cluster_density = {}
for i in labels_change:
    # np.sum(np.array(df2_str((df2_str['labels'] == i) and (df2_str["PROP_USE_D"].str.contains("RESIDENTIAL")))))/np.sum(np.array(df2_str((df2_str['labels'] == i))))
    cluster_density[i] = np.sum(np.array(df2_str((df2_str['labels'] == i) and (df2_str["PROP_USE_D"].str.contains("RESIDENTIAL")))))/np.sum(np.array(df2_str((df2_str['labels'] == i))))


# print(db.labels)
# neighbors = NearestNeighbors(n_neighbors=20)
# neighbors_fit = neighbors.fit(np.radians(df_combined[['lat','lon']]))
# distances, indices = neighbors_fit.kneighbors()
# distances = np.sort(distances, axis=0)
# distances = distances[:,1]
# plt.plot(distances)
# plt.show()