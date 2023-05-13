import geopandas as gpd
import os
import argparse
import pdb
import multiprocessing
from tqdm import tqdm
import numpy as np
import pandas as pd
from shapely.ops import transform
import pyproj
from functools import partial
import sys
import shapely.ops as ops
from poly_utils import graphs
import warnings
warnings.filterwarnings("ignore")

'''
Scoring the future land use scores based on their suitability for developement . 
With 0 being least suitable and 1 most
INPUT: Future Land Use list
OUTPUT: List containing numerical scoring of Future Land Use 
'''

def convert_flu(flu):
    flu = np.array(flu)
    flu[np.where((flu=='RR')| (flu=='PRC'))] = 0
    flu[np.where((flu=='HD') | (flu=='LD'))] = 1
    flu[np.where((flu=='MD') | (flu =='OI') | (flu =='CITY'))] = 2
    flu[np.where(flu=='MX')] = 3
    flu[np.where((flu=='COMM') | (flu=='COM'))] = 4
    flu[np.where((flu=='INDUS')| (flu=='PI')| (flu=='TCU') | (flu=='NA'))] = 5

    flu = flu.astype(np.int64)
    flu = list(flu)
    return flu

'''
Scoring the current zoning scores based on their suitability for developement . 
With 0 being least suitable and 1 most
INPUT: Current Zoning list
OUTPUT: List containing numerical scoring of Current Zoning 
'''

def convert_zoning(zoning):
    zoning = np.array(zoning)
    zoning[np.where((zoning=='RA')| (zoning=='R1') | (zoning=='R2') |(zoning=='R3') | (zoning=='R4') | (zoning=='R5') | (zoning=='RS')| (zoning=='RD') | (zoning=='PD'))] = 0
    zoning[np.where((zoning=='RM') | (zoning=='RMH')| (zoning=='DTRC')| (zoning=='MR1')| (zoning=='MR2'))] = 1
    zoning[np.where((zoning=='O1')| (zoning=='OI')|(zoning=='CITY')| (zoning=='DTMU') | (zoning=='MU'))] = 2
    zoning[np.where((zoning=='C1')| (zoning=='C2'))] = 3
    zoning[np.where((zoning=='C3')| (zoning=='IAC'))] = 4
    zoning[np.where((zoning=='M1') | (zoning=='M2')|(zoning=='NA'))] = 5
    zoning = zoning.astype(np.int64)
    zoning = list(zoning)
    
    return zoning

'''
Calculating the overlap for each parcel in Parcel Data with any other shapefile. 
Finding the polygon with maximum intersection with that particular parcel 
INPUT: rtree index , Parcel data (geopandas DataFrame)
'''
def overlap_calc(idx,poly):
    if not(poly.is_valid):
        poly = poly.buffer(0)
    if(poly.is_valid):
        hits = list(idx.intersection((poly.bounds), objects = True))
        poly_accept = 0
        iou_max = 0
        for box in hits:
            item_poly = box.object

            #Checking if polygon is valid
            if not(item_poly.is_valid):
                item_poly = item_poly.buffer(0)
            if(item_poly.is_valid):
                try:
                    if (item_poly).intersects(poly):
                            inter = (item_poly).intersection(poly)
                            #Finding percentage overlap, if it exceeds the maximum overlap so far out of the other hits then it is taken
                            if((inter.area/item_poly.area)>iou_max):
                                iou_max =  inter.area/item_poly.area
                                poly_accept = item_poly
                except:
                    pass
        return poly_accept

'''
Landuse - Parcels suitable for construction based on land use and zoning type  
Inputs: Parcels data(geopandas polygon dataframe), Land Use data(geopandas polygon dataframe), Zoning data(geopandas polygon dataframe), Land Use data(rtree index), Zoning data(rtree index)
Output: Parcels data with added columns 'flu','zoning' normalized scores between 0-1.
''' 

def landuse_geo(geo1,geo3, geo4, idx2,idx3):
    flu = []
    zoning = [] 
    poly_list = geo1['geometry']
    # pdb.set_trace()
    for poly_1 in tqdm(poly_list, total = len(poly_list)):
        poly = overlap_calc(idx3,poly_1)
        if not(poly == 0):

            #Finding the index of the intersecting polygon and corresponding zoning information
            idx_ = geo4[geo4.contains(poly)]
            zoning.append((idx_['ZONING'].iloc[0]))
        else:
            zoning.append('NA')
    for poly_2 in tqdm(poly_list, total = len(poly_list)):
        poly = overlap_calc(idx2,poly_2)
        if not(poly == 0):
            #Finding the index of the intersecting polygon and corresponding future land use information
            idx_ = geo3[geo3.contains(poly)]
            flu.append((idx_['FLU'].iloc[0]))  
        else:
            flu.append('NA')
   
    flu_final = convert_flu(flu)
    zoning_final = convert_zoning(zoning)

    #Assigning the normalized values with 0 being least favourable and 1 most
    geo1['flu'] = list(((np.array(flu_final))/max(flu_final)))
    geo1['zoning'] = list(((np.array(zoning_final))/max(zoning_final)))

    return geo1

'''
Construction Area - Parcels most suitable for construction based on amount of free area available within the parcel  
INPUTS: Parcels data(geopandas polygon dataframe), Buildings data(rtree index)
OUTPUT: Parcels data with added columns 'flu','zoning' normalized scores between 0-1.
''' 
def area_geo(geo1, idx):
    constr_area = []
    poly_area = []
    #Converting crs to 4336 for area calculation in m^2
    geo1 = geo1.to_crs(4326)
    for i in tqdm(range(len(geo1))):
        poly = geo1['geometry'][i]
        #Defining the projection for calculating area is metric units
        poly_= ops.transform(partial(
        pyproj.transform,
        pyproj.Proj(init='EPSG:4326'),
        pyproj.Proj(
            proj='aea',
            lat_1=poly.bounds[1],
            lat_2=poly.bounds[3]
        )
    ),
    poly)

        #Caulculating the area of the parcel
        poly_area.append(poly_.area)
        #Finding how many buildings are located within the parcel
        hits = list(idx.intersection((poly.bounds), objects = True))
        area = poly_.area
        for box in hits:
            item_poly = box.object
            if (item_poly).intersects(poly):

                    #Transforming each intersecting polygon to Parcel polygon coordinates
                    item_poly_= ops.transform(partial(
                    pyproj.transform,
                    pyproj.Proj(init='EPSG:4326'),
                    pyproj.Proj(
                        proj='aea',
                        lat_1=item_poly.bounds[1],
                        lat_2=item_poly.bounds[3]
                    )
                ),
                item_poly)                    
                    inter = (item_poly_).intersection(poly_)
                    iou = float(inter.area / poly_.area)
                    #Subtracting area of each building within parcel from total parcel area to find area left for constrcution                   
                    if iou > 1e-5 :
                        area = area - inter.area
    
        constr_area.append(area)
        
    # pdb.set_trace()
    ## Adjust the area difference - check if it is correct(linear metric system )

    #Normalizing area in the range of 0-1 with 0 being least favourable and 1 being most
    geo1['constr_area'] = list(((np.array(constr_area))/max(max(constr_area),1e-10)))
    #Converting CRS back to 3857 for further processing 
    geo1 = geo1.to_crs(3857)
    return geo1

