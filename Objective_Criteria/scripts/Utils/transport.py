import geopandas as gpd
import os
import sys
import pdb
import argparse
import pyproj
from tqdm import tqdm 
import numpy as np
import sys
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points



def distance_corridoor(geo1, geo2):
    # pdb.set_trace()
    dist = []
    geod = pyproj.Geod(ellps = 'WGS84')  
    for i in tqdm(range(len(geo1['geometry']))):
        best_d = sys.maxsize
        for j in range(len(geo2['geometry'])):
            line = geo2['geometry'][j]
            poly = geo1['geometry'][i]
            p1,p2 = nearest_points(poly.boundary, line)
            d = p2.distance(p1)
            if(d <best_d):
                best_d = d
            # d = nearest[1].distance(poly)
        dist.append(best_d)
    # pdb.set_trace()
    dist_ratio = list(1-((np.array(dist))/max(max(dist),1e-10)))
    geo1['MajorCor'] = dist_ratio
    return geo1

def calc_LOS( idx,poly):
    # pdb.set_trace()
    hits = list(idx.intersection((poly.bounds), objects = True))
    l = 0
    poly_1 = 0
    for box in hits:
        item_poly = box.object
        if (item_poly).intersects(poly):
            if(item_poly.length>l):
                l = item_poly.length
                poly_1 = item_poly
    return poly_1


def LOS_geo(geo1, geo2, idx1, buffer_distance = 500):
    geo2['LOS'] = [5]*len(geo2)
    los = []
    geo1['buffer'] = geo1.buffer(distance = buffer_distance)
    poly_list = geo1['buffer']
    for i in range(len(geo2)):
        if(geo2['amlos'][i] =='F') or (geo2['pmlos'][i] == 'F'):
            geo2['LOS'][i] = 1
        elif(geo2['amlos'][i] =='E') or (geo2['pmlos'][i] == 'E'):
            geo2['LOS'][i] = 2
        elif(geo2['amlos'][i] =='D') or (geo2['pmlos'][i] == 'D'):
            geo2['LOS'][i] = 3
        elif(geo2['amlos'][i] =='C') or (geo2['pmlos'][i] == 'C'):
            geo2['LOS'][i] = 4


    for poly_1 in tqdm(poly_list, total = len(poly_list)):
        poly = calc_LOS(idx1,poly_1)
        if not(poly == 0):
            idx_ = geo2[geo2.contains(poly)]
            if(len(idx_)>1):
                length = 0
                los_i = -1
                for i in range(len(idx_)):
                    inter = (idx_.iloc[i]['geometry'].intersection(poly)).length
                    if(inter > length):
                        length = inter
                        los_i = idx_.iloc[i]['LOS']
                    elif(inter  == length):
                        if(idx_.iloc[i]['LOS'] >= los_i):
                            los_i = idx_.iloc[i]['LOS']
                los.append(los_i)
            else:
                los.append(idx_['LOS'].iloc[0])  
        else:
            los.append(0)
    geo1['LOS'] = list(np.array(los)/max(max(los),1e-10))
    geo1 = geo1.drop('buffer', axis=1)

    return geo1