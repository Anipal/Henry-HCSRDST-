import geopandas as gpd
import os
import pdb
from tqdm import tqdm
import argparse
from shapely.geometry import Point, MultiPoint
from shapely.ops import nearest_points, transform
import pyproj
from functools import partial
import numpy as np


def distance_calc(df1, point):

    #Transforming to EPSG 4326 for easy conversion to metric values
    df1 = df1.to_crs(4326)
    dist = []

    #Projecting to a metric systems projection
    geod = pyproj.Geod(ellps = 'WGS84')
    for i in tqdm(range(len(df1['geometry']))):

        #Finding the centroid of the parcel
        poly = df1['geometry'][i].centroid 

        #Finding the nearest point to the the parcel  
        nearest = nearest_points(poly, point)

        #Finding the distance to the nearest point
        _,_,d = geod.inv(nearest[1].x, nearest[1].y, poly.x, poly.y)  
        # d = nearest[1].distance(poly)
        dist.append(d)
        
    #Normalizing by dividing with the maximum distance between a polygon and its nearest point
    dist_ratio = list((np.array(dist))/max(max(dist),1e-10))
    return dist, dist_ratio

'''
Residential Proximity - Proximity of parcels to residential clusters 
INPUTS: Parcels data(geopandas polygon dataframe), Area clusters data (geopandas polygon dataframe)
OUTPUT: Parcels data with added column 'near-res', ratio of distance to nearest residential cluster
'''

def res_geo(df1, df2):

    #Taking only the Residential and No Developement clusters 
    df2_ = df2[(df2['Area']=='NO DEV') | (df2['Area']=='Residential')]
    df2_ = df2_.reset_index(drop=True)

    #Converting the cluster point geometry to MultiPoint
    point = MultiPoint(df2_.geometry)
    dist, dist_ratio = distance_calc(df1,point)
    #df1['nearest-distance'] = dist
    df1['near-res'] = dist_ratio
    return df1

'''
Public Proximity - Parcels most suitable for construction based on their proximity from schools and hospitals  
INPUTS: Parcels data(geopandas polygon dataframe), Schools data(geopandas polygon dataframe), Hospitals data(geopandas polygon dataframe)
OUTPUT: Parcels data with added column 'near-pub', normalized scores between 0-1.
''' 

def public_geo(df1, df2, df3):

    #Combining the schools and the hospitals point and converting the resulting Point geometry to MultiPoint
    point = MultiPoint(df2['geometry'].tolist() + df3['geometry'].tolist())
    _ , dist_ratio = distance_calc(df1,point)
    df1['near-pub'] = dist_ratio
    return df1

'''
Environmental Proximity - Parcels most suitable for construction based on their proximity from environmentally sensitive areas
INPUTS: Parcels data(geopandas polygon dataframe), Parks data(geopandas polygon dataframe)
OUTPUT: Parcels data with added column 'near-env', normalized scores between 0-1.
''' 

def env_geo(df1, df2):

    #Converting the environment point geometry to MultiPoint
    point = MultiPoint(df2.geometry)
    _ , dist_ratio = distance_calc(df1,point)
    df1['near-env'] = dist_ratio
    return df1