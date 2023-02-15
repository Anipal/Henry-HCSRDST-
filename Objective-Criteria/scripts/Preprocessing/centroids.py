import shapely
import geopandas as gpd 
import argparse
import pandas as pd 
import json 
from tqdm import tqdm 
import pyproj
import argparse
import pdb
import os

parser = argparse.ArgumentParser(description="Calculate centroids")
parser.add_argument('--geo_dir', type=str, default='pmap_dpn/',help='put the path to image directory')
parser.add_argument('--save_dir', type=str, default='pmap_dpn/',help='put the path to image directory')
args = parser.parse_args()

# pdb.set_trace()
def add_coords(df1):
    pdb.set_trace()
    df1 = df1.to_crs({'init': 'epsg:4326'}) 
    if (df1.geom_type == 'Polygon').any():
        df1['Cent_Lon'] = df1['geometry'].centroid.x
        df1['Cent_Lat'] = df1['geometry'].centroid.y
    else:
        df1['Cent_Lon'] = df1['geometry'].x
        df1['Cent_Lat'] = df1['geometry'].y
    return df1

geojson_df = add_coords( gpd.read_file(args.geo_dir))
name_dir = args.geo_dir.split('/')[-1].split('.')[0]
if not(os.path.exists(os.path.join(args.save_dir,name_dir))):
    os.makedirs(os.path.join(args.save_dir,name_dir))
geojson_df.to_file(os.path.join(args.save_dir,name_dir,(args.geo_dir.split('/')[-1])))


