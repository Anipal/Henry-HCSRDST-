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
import requests


def distance_calc(df1, point):
    df1 = df1.to_crs(4326)
    dist = []
    geod = pyproj.Geod(ellps = 'WGS84')
    for i in tqdm(range(len(df1['geometry']))):
        poly = df1['geometry'][i].centroid   
        nearest = nearest_points(poly, point)
        _,_,d = geod.inv(nearest[1].x, nearest[1].y, poly.x, poly.y)  
        # d = nearest[1].distance(poly)
        dist.append(d)
    dist_ratio = list((np.array(dist))/max(dist))
    return dist, dist_ratio

def apportion(df1, df2, join_fields):

    if type(join_fields) == str:
        join_fields = [join_fields]

    #Spatial join intersect df2 with df1 via intersection, calculate area.
    #Set index for df1
    df1_ = df1.copy()
    df1_['spatial_index'] = df1_['geometry'].to_wkt()

    #Get intersection of df1 and df2
    inter = gpd.overlay(df1_, df2, how = 'intersection')

    #Group by spatial index
    inter['area'] = inter['geometry'].area
    #Group by parcel geometry, then select max area from the intersection
    cleaned = inter.groupby('spatial_index').max('area').reset_index()[['spatial_index'] + join_fields]

    #Append back to original dataframe
    final = df1_.merge(cleaned, on = 'spatial_index', how = 'left').drop('spatial_index', axis = 1)

    #Return final
    return final

def res_geo(df1, df2):
    df2_ = df2[(df2['Area']=='NO DEV') | (df2['Area']=='Residential')]
    df2_ = df2_.reset_index(drop=True)
    point = MultiPoint(df2_.geometry)
    dist, dist_ratio = distance_calc(df1,point)
    df1['nearest-distance'] = dist
    df1['near-res'] = dist_ratio
    return df1

def public_geo(df1, df2, df3):
    point = MultiPoint(df2['geometry'].tolist() + df3['geometry'].tolist())
    _ , dist_ratio = distance_calc(df1,point)
    df1['near-pub'] = dist_ratio
    return df1

def env_geo(df1, df2):
    point = MultiPoint(df2.geometry)
    _ , dist_ratio = distance_calc(df1,point)
    df1['near-env'] = dist_ratio
    return df1

def svi_geo(df1, df2):
    svi = df2.copy()[['RPL_THEMES', 'geometry']].to_crs(df1.crs)

    #Replace invalid values with zero / 1
    svi.loc[svi['RPL_THEMES'] < 0, 'RPL_THEMES'] = 0
    svi.loc[svi['RPL_THEMES'] > 1, 'RPL_THEMES'] = 1

    #Append SVI score to df1
    df1 = apportion(df1, svi, 'RPL_THEMES').rename(columns={'RPL_THEMES':'svi'})

    return df1




    