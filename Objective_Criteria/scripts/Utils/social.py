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
    df1 = df1.to_crs(4326)
    dist = []
    geod = pyproj.Geod(ellps = 'WGS84')
    for i in tqdm(range(len(df1['geometry']))):
        poly = df1['geometry'][i].centroid   
        nearest = nearest_points(poly, point)
        _,_,d = geod.inv(nearest[1].x, nearest[1].y, poly.x, poly.y)  
        # d = nearest[1].distance(poly)
        dist.append(d)
    dist_ratio = list((np.array(dist))/max(max(dist),1e-10))
    return dist, dist_ratio

def res_geo(df1, df2):
    df2_ = df2[(df2['Area']=='NO DEV') | (df2['Area']=='Residential')]
    df2_ = df2_.reset_index(drop=True)
    point = MultiPoint(df2_.geometry)
    dist, dist_ratio = distance_calc(df1,point)
    #df1['nearest-distance'] = dist
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