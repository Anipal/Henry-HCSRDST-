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
import ast
from pandas.io.json import json_normalize
def list_of_dicts(ld):
    '''
    Create a mapping of the tuples formed after 
    converting json strings of list to a python list   
    '''
    return dict([(list(d.values())[1], list(d.values())[0]) for d in ast.literal_eval(ld)])

def only_dict(d):
    '''
    Convert json string representation of dictionary to a python dict
    '''
    return ast.literal_eval(d)

kms_per_radian = 6371.0088
eps = 0.5 / kms_per_radian
ms = 500

# pdb.set_trace()
collection_change = list(fiona.open(args.centroid_change,'r'))
collection_str = list(fiona.open(args.centroid_str,'r'))
df1_change = pd.DataFrame(collection_change)
df1_str = pd.DataFrame(collection_str)
# df2_str = gpd.read_file(args.centroid_str)

df1_change_new_field = add_fields(df1_change, 1)
df1_str_new_field = add_fields(df1_str, 0)

df1_change_coords = add_coords(df1_change_new_field)
df1_str_coords = add_coords(df1_str_new_field)
pdb.set_trace()
df_combined = pd.concat([df1_change_coords, df1_str_coords], ignore_index=True)
A = df_combined["properties"].apply(pd.Series)
geometry = [Point(xy) for xy in zip(df_combined.Lon, df_combined.Lat)]
df = df_combined.drop(['properties'], axis=1)
df = pd.concat([df, A], axis=1)
gdf = gpd.GeoDataFrame(df, crs="EPSG:4326", geometry=geometry)

gdf.to_file((os.path.join(args.save_dir,'combined_5.shp')))