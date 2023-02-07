import shapely
import geopandas as gpd 
import argparse
import pandas as pd
import fiona 
from centroid_coords import *
import pdb
import os
import pandas as pd, numpy as np, matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from geopy.distance import great_circle
from shapely.geometry import MultiPoint
from sklearn.neighbors import NearestNeighbors
from shapely.geometry import Point
from sklearn import preprocessing, cluster
parser = argparse.ArgumentParser(description="Raster to shapefile")
parser.add_argument('--save_dir', type=str, default='/media/ssd1/data/sanborn',
                        help='put the path to root directory')
parser.add_argument('--centroid_change', type=str, default='pmap_dpn/',
                        help='put the path to save geojson')
parser.add_argument('--centroid_str', type=str, default='pmap_dpn/',help='put the path to image directory')
args = parser.parse_args()


kms_per_radian = 6371.0088
eps = 0.5 / kms_per_radian
ms = 500

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
# pdb.set_trace()
db = DBSCAN(eps=eps, min_samples=ms, algorithm='ball_tree', metric='haversine').fit(np.radians(df_combined[['lat','lon']]))
# model = cluster.KMeans(n_clusters=15, init='k-means++')
df_combined['cluster_labels'] = db.labels_
geometry = [Point(xy) for xy in zip(df_combined.Lon, df_combined.Lat)]
df_combine = df_combined.drop(['Lon', 'Lat'], axis=1)
gdf = gpd.GeoDataFrame(df_combined, crs="EPSG:4326", geometry=geometry)
gdf.to_file((os.path.join(args.save_dir,'clustering_analysis_centroids_2.shp')))
labels_change = np.unique(np.array(df_combined.iloc[:len(df1_change_coords)]['cluster_labels'])) 
df2_str['labels'] = df_combined.iloc[len(df1_change_coords):]['cluster_labels']
df2_str["PROP_USE_D"] = df2_str["PROP_USE_D"].fillna('')
cluster_density_res = {}
cluster_density_consv = {}
cluster_density_comm = {}
cluster_number = {}
cluster_public = {}
df_cluster_significance = pd.DataFrame(columns = ["Cluster", "Centroid_lon", "Centroid_lat", "Residential","Conservation","Industrial","Public","Total"])
pdb.set_trace()
k = 0
for j,i in enumerate(labels_change):
    # np.sum(np.array(df2_str((df2_str['labels'] == i) and (df2_str["PROP_USE_D"].str.contains("RESIDENTIAL")))))/np.sum(np.array(df2_str((df2_str['labels'] == i))))
    try:
        df3 = df2_str[(df2_str['labels'] == i)]
        centroid_lon = np.mean(np.array(df1_str_coords[(df2_str['labels'] == i)]['lon']), axis = 0)
        centroid_lat = np.mean(np.array(df1_str_coords[(df2_str['labels'] == i)]['lat']), axis = 0)
        res = len(df3[df3["PROP_USE_D"].str.contains("RESIDENTIAL")])+len(df3[df3["PROP_USE_D"].str.contains("HOME")]) + len(df3[df3["PROP_USE_D"].str.contains("APARTMENT")])+len(df3[df3["PROP_USE_D"].str.contains("FAMILY")]) + len(df3[df3["PROP_USE_D"].str.contains("CONDO")])
        consv = len(df3[df3["PROP_USE_D"].str.contains("CONSV")]) + len(df3[df3["PROP_USE_D"].str.contains("FOREST")])
        comm = len(df3[df3["PROP_USE_D"].str.contains("COMMERCIAL")]) + len(df3[df3["PROP_USE_D"].str.contains("INDUSTRIAL")])
        df_cluster_significance.loc[k] = [i,centroid_lon,centroid_lat,res/len(df3),consv/len(df3),comm/len(df3),len(df3[df3["PROP_USE_D"].str.contains("EDU")]) + len(df3[df3["PROP_USE_D"].str.contains("HOSPITAL")]),len(df3)]
        k = k+1
    except:
        continue
    # cluster_density_res[i] = res/len(df3)
    # cluster_density_consv[i] = consv/len(df3)
    # cluster_density_comm[i] = comm/len(df3)
    # cluster_public[i] = len(df3[df3["PROP_USE_D"].str.contains("EDU")]) + len(df3[df3["PROP_USE_D"].str.contains("HOSPITAL")])
    # cluster_number[i] = len(df3)
geometry = [Point(xy) for xy in zip(df_cluster_significance.Centroid_lon, df_cluster_significance.Centroid_lat)]
df_cluster_significance = df_cluster_significance.drop(['Centroid_lon', 'Centroid_lat'], axis=1)
gdf = gpd.GeoDataFrame(df_cluster_significance, crs="EPSG:4326", geometry=geometry)
gdf.to_file((os.path.join(args.save_dir,'clustering_analysis_centroids_2.shp')))
df2_str.to_file((os.path.join(args.save_dir,'clustering_analysis_all_points_2.shp')))
print(db.labels)
neighbors = NearestNeighbors(n_neighbors=20)
neighbors_fit = neighbors.fit(np.radians(df_combined[['lat','lon']]))
distances, indices = neighbors_fit.kneighbors()
distances = np.sort(distances, axis=0)
distances = distances[:,1]
plt.plot(distances)
plt.show()