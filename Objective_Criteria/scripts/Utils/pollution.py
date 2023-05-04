import geopandas as gpd
from tqdm import tqdm
import numpy as np
import pandas as pd
from shapely import geometry, ops
import sys
from shapely.geometry import Polygon, LineString

def flood_plain(geo):
    
    flood = geo['FLOOD_PLAI']
    flood = np.array(flood)
    flood[np.where(flood == 'YES') or np.where(flood == 'yes')] = 0
    flood[np.where(flood == 'NO')] = 1
    geo['flood'] = flood
    return geo

def noise(poly, road, buffer):
    # pdb.set_trace()
    road = road.to_crs(3857)
    road_buffer = road['geometry'][0].buffer(buffer)
    if (poly).intersects(road_buffer):
        return 0
    else:
        return 1


def air(poly, road, buffer):
    
    road = road.to_crs(3857)
    road_buffer = road['geometry'][0].buffer(buffer)
    if (poly).intersects(road_buffer):
        return 0
    else:
        return 1
def merge(df):
    multi_line = geometry.MultiLineString(df['geometry'].tolist())
    merged_line = ops.linemerge(multi_line)
    return merged_line

def pollution_geo(parcels, road, buffer_air = 5000, buffer_noise = 5000):
    air_pollution = []
    noise_pollution = []
    l1 = merge(road[road['NAME'] == 'I-75 / GA-401 SOUTHBOUND'])
    l2 = merge(road[road['NAME'] == 'I-75 / GA-401 NORTHBOUND'])
    p = Polygon([*list(l1.coords), *list(l2.coords)])
    road_df = gpd.GeoDataFrame({'geometry':[p]})
    road_df.crs = road.crs
    for poly in tqdm(parcels['geometry'], total = len(parcels['geometry'])):
        noise_pollution.append(noise(poly, road_df, buffer_noise))
        air_pollution.append(air(poly, road_df, buffer_air))

    parcels['air_poll'] = air_pollution
    parcels['noise_poll'] = noise_pollution

    return parcels