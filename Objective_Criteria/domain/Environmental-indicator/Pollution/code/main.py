import geopandas as gpd
import os
import argparse
import pdb
from tqdm import tqdm
import numpy as np
import pandas as pd
from shapely import geometry, ops
import pyproj
import sys
from shapely.geometry import Polygon, LineString
import pdb

def noise(poly, road, buffer):
    # pdb.set_trace()
    road = road.to_crs(3857)
    road_buffer = road['geometry'][0].buffer(buffer)
    if (poly).intersects(road_buffer):
        return 1
    else:
        return 0


def air(poly, road, buffer):
    
    road = road.to_crs(3857)
    road_buffer = road['geometry'][0].buffer(buffer)
    if (poly).intersects(road_buffer):
        return 1
    else:
        return 0
def merge(df):
    multi_line = geometry.MultiLineString(df['geometry'].tolist())
    merged_line = ops.linemerge(multi_line)
    return merged_line

def main():
    parser = argparse.ArgumentParser(description="Raster to shapefile")
    parser.add_argument('--save_dir', type=str, default='/media/ssd1/data/sanborn',help='put the path to root directory')
    parser.add_argument('--parcels', type=str, default='pmap_dpn/',help='put the path to image directory')
    parser.add_argument('--road', type=str, default='pmap_dpn/',help='put the path to image directory')
    args = parser.parse_args()    
    air_pollution = []
    noise_pollution = []
    buffer_air = 5*1000
    buffer_noise = 5*1000
    parcels = gpd.read_file(args.parcels).to_crs(3857)
    road = gpd.read_file(args.road)

    
    l1 = merge(road[road['NAME'] == 'I-75 / GA-401 SOUTHBOUND'])
    l2 = merge(road[road['NAME'] == 'I-75 / GA-401 NORTHBOUND'])
    p = Polygon([*list(l1.coords), *list(l2.coords)])
    road_df = gpd.GeoDataFrame({'geometry':[p]})
    road_df.crs = road.crs
    
    for poly in tqdm(parcels['geometry'], total = len(parcels['geometry'])):
        noise_pollution.append(noise(poly, road_df, buffer_noise))
        air_pollution.append(air(poly, road_df, buffer_air))

    parcels['air_pollution'] = air_pollution
    parcels['noise_pollution'] = noise_pollution
    parcels = parcels.to_crs(2697)
    name_dir = 'environment'
    file_name = 'pollution.shp'

    # pdb.set_trace()
    if not(os.path.exists(os.path.join(args.save_dir,name_dir))):
        os.makedirs(os.path.join(args.save_dir,name_dir))
    print(os.path.join(args.save_dir,name_dir,(file_name)))
    parcels.to_file(os.path.join(args.save_dir,name_dir,(file_name)))
    # geojson_buffer.to_file(os.path.join(args.save_dir,name_dir,(file_name_2)))
if __name__ == "__main__":
    main()   

