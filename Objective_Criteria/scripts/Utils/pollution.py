import geopandas as gpd
from tqdm import tqdm
import numpy as np
import pandas as pd
from shapely import geometry, ops
import sys
from shapely.geometry import Polygon, LineString

'''
Calculatig  the density of residential buildings surrounding a given parcel given a buffer distance
INPUTS: Parcels data(geopandas polygon dataframe)
OUTPUT: Parcels data with added columns 'flood', indicating if the parcel is vulnerable to flood with 0 being vulnerable and 1 being suitable for construction
'''
def flood_plain(geo):
    # Getting the value of FLOOD_PLAI for all the parcels
    flood = geo['FLOOD_PLAI']
    flood = np.array(flood)
    # Assigning 0 if the parcel is a flood plain and 1 if it is not
    flood[np.where(flood == 'YES') or np.where(flood == 'yes')] = 0
    flood[np.where(flood == 'NO')] = 1
    geo['flood'] = list(flood)
    return geo

#Finding if the polygon intersects the road
def inter(poly, road):
    if (poly).intersects(road):
        return 0
    else:
        return 1

#Merging two line geometries into a polygon
def merge(df):
    multi_line = geometry.MultiLineString(df['geometry'].tolist())
    merged_line = ops.linemerge(multi_line)
    return merged_line

'''
Pollution - Parcels containg information about vulnerability of parcel to pollution  
INPUTS: Parcels data(geopandas polygon dataframe), Road data (geopandas line dataframe),Distance from I-75 where air pollution levels will be high(int), Distance from I-75 where noise pollution levels will be high(int)
OUTPUT: Parcels data with added columns 'air_poll', 'noise_poll'
''' 
def pollution_geo(parcels, road, buffer_air = 5000, buffer_noise = 5000):
    air_pollution = []
    noise_pollution = []
    #Finding the two major road segments in I-75
    l1 = merge(road[road['NAME'] == 'I-75 / GA-401 SOUTHBOUND'])
    l2 = merge(road[road['NAME'] == 'I-75 / GA-401 NORTHBOUND'])

    #Combining the two segments to create a polygon 
    p = Polygon([*list(l1.coords), *list(l2.coords)])
    road_df = gpd.GeoDataFrame({'geometry':[p]})
    road_df.crs = road.crs
    road_df = road_df.to_crs(3857)

    #Adding buffers to the polygon based on noise pollution buffer and air pollution buffer
    road_noise = road_df['geometry'][0].buffer(buffer_noise)
    road_air = road_df['geometry'][0].buffer(buffer_air)

    #Finding which parcels intersect with teh bufferred polygon, hence being vulnerable to pollution
    for poly in tqdm(parcels['geometry'], total = len(parcels['geometry'])):
        noise_pollution.append(inter(poly, road_noise))
        air_pollution.append(inter(poly, road_air))

    parcels['air_poll'] = air_pollution
    parcels['noise_poll'] = noise_pollution

    return parcels