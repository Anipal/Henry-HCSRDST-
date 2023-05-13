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

'''
Calculating the distance of each parcel to the major freight corridoor
INPUT: Parcel data (geopandas DataFrame), Road data with only entrance and exit ramps for major corridoor (geopandas DataFrame)
'''

def distance_corridoor(geo1, geo2):
    # pdb.set_trace()
    dist = []

    #Defining projection for distance calculation 
    geod = pyproj.Geod(ellps = 'WGS84')  
    #Iterating through each parcel 
    for i in tqdm(range(len(geo1['geometry']))):
        #Assigining variable with max int value 
        best_d = sys.maxsize
        #Iterating through each Line geometry in the road data 
        for j in range(len(geo2['geometry'])):
            line = geo2['geometry'][j]
            poly = geo1['geometry'][i]

            #p1 and p2 represent the points on both geometry which are closest to each other 
            p1,p2 = nearest_points(poly.boundary, line)

            #Finding the distance between the nearest points on both geometries 
            d = p2.distance(p1)

            #If this value is less than the nearest distance found so far then we update the value of the nearest distance of a parcel to major freight
            if(d <best_d):
                best_d = d
            # d = nearest[1].distance(poly)
        dist.append(best_d)

    #Normalizing the points, subtracting from 1 becuase we want the parcels to favour closeness to the freight
    #1 indicates most favourable and 0 indicates least favourable 
    dist_ratio = list(1-((np.array(dist))/max(max(dist),1e-10)))

    #Assigning variable MajorCor the value of the distance ratio 
    geo1['MajorCor'] = dist_ratio
    return geo1

'''
Calculating the intersection between polygon geometry and several line geometries 
and finding the line geometry with the maximum length of overlap
INPUT: Road data (rtree index), Parcel data (geopandas DataFrame)
'''
def calc_LOS( idx,poly):
  
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


'''
LOS - Parcels with LOS information of closest road 
INPUT: Parcels data(geopandas polygon dataframe), Road data (geopandas line dataframe), Road data (rtree index), Buffer in m(int)
OUTPUT: Parcels data with added column 'LOS', LOS information in float values b/w 0-1
'''

def LOS_geo(geo1, geo2, idx1, buffer_distance = 500):

    #Assigning a new column LOS to the road data and initializing it with the value of 5 
    geo2['LOS'] = [5]*len(geo2)
    los = []
    # Adding buffer to the parcels data for intersection calculation
    geo1['buffer'] = geo1.buffer(distance = buffer_distance)
    #Obtaining the list of bufferred polygons 
    poly_list = geo1['buffer']

    #Combing amlos and pmlos by or operation and assigning numeric values to LOS, with 1 (F)being the worst and 5 (A/B) the best LOS
    for i in range(len(geo2)):
        if(geo2['amlos'][i] =='F') or (geo2['pmlos'][i] == 'F'):
            geo2['LOS'][i] = 1
        elif(geo2['amlos'][i] =='E') or (geo2['pmlos'][i] == 'E'):
            geo2['LOS'][i] = 2
        elif(geo2['amlos'][i] =='D') or (geo2['pmlos'][i] == 'D'):
            geo2['LOS'][i] = 3
        elif(geo2['amlos'][i] =='C') or (geo2['pmlos'][i] == 'C'):
            geo2['LOS'][i] = 4

    #Iterating through each buffered polygon
    for poly_1 in tqdm(poly_list, total = len(poly_list)):

        #Finding the intersection of the parcel with the longest road segment and assigning the LOS of that to the parcel
        poly = calc_LOS(idx1,poly_1)
        if not(poly == 0):
            #Finding the index of the intersecting line segment 
            idx_ = geo2[geo2.contains(poly)]
            #If more than one value of idx_ exists then taking the one with the largest intersection or if equal length then taking the worst LOS 
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
        # If no intersection exists for the parcel then LOS is assigned as 0
        else:
            los.append(0)
    # Assigning LOS column with the value of the normalized LOS values 0-1, with 0 being least favourable and 1 most
    geo1['LOS'] = list(np.array(los)/max(max(los),1e-10))
    geo1 = geo1.drop('buffer', axis=1)

    return geo1