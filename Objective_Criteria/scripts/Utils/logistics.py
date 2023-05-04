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
from poly_utils import polygon_list_plain, graphs
from matplotlib import pyplot as plt

def convert_flu(flu):
    flu = np.array(flu)
    flu[np.where((flu=='RR')| (flu=='PRC'))] = 0
    flu[np.where((flu=='HD') | (flu=='LD'))] = 1
    flu[np.where(flu=='MD')] = 2
    flu[np.where(flu=='MX')] = 3
    flu[np.where((flu=='COMM') | (flu=='COM'))] = 4
    flu[np.where((flu=='INDUS')| (flu=='PI')| (flu=='TCU') | (flu=='NA'))] = 5

    flu = list(flu)
    return flu

def convert_zoning(zoning):
    zoning = np.array(zoning)
    zoning[np.where((zoning=='RA')| (zoning=='R1') | (zoning=='R2') |(zoning=='R3') | (zoning=='R4') | (zoning=='R5') | (zoning=='RS')| (zoning=='RD'))] = 0
    zoning[np.where((zoning=='RM') | (zoning=='RMH')| (zoning=='DTRC')| (zoning=='MR1')| (zoning=='MR2'))] = 1
    zoning[np.where((zoning=='O1')| (zoning=='OI')|(zoning=='CITY')| (zoning=='DTMU') | (zoning=='MU'))] = 2
    zoning[np.where((zoning=='C1')| (zoning=='C2'))] = 3
    zoning[np.where((zoning=='C3')| (zoning=='IAC'))] = 4
    zoning[np.where((zoning=='M1') | (zoning=='M2')| (zoning=='PD'))] = 5
    zoning = list(zoning)
    return zoning

def overlap_calc(idx,poly):
    # print(type(idx))
    # pdb.set_trace()
    if not(poly.is_valid):
        poly = poly.buffer(0)
    if(poly.is_valid):
        hits = list(idx.intersection((poly.bounds), objects = True))
        poly_accept = 0
        iou_max = 0
        for box in hits:
            item_poly = box.object
            if not(item_poly.is_valid):
                item_poly = item_poly.buffer(0)
            if(item_poly.is_valid):
                try:
                    if (item_poly).intersects(poly):
                            inter = (item_poly).intersection(poly)
                            if((inter.area/item_poly.area)>iou_max):
                                iou_max =  inter.area/item_poly.area
                                poly_accept = item_poly
                except:
                    pass
        return poly_accept


def landuse_geo(geo1,geo3, geo4, idx2,idx3):
    flu = []
    zoning = [] 
    poly_list = geo1['geometry']
    # pdb.set_trace()
    for poly_1 in tqdm(poly_list, total = len(poly_list)):
        poly = overlap_calc(idx3,poly_1)
        if not(poly == 0):
            idx_ = geo4[geo4.contains(poly)]
            zoning.append((idx_['ZONING'].iloc[0]))
        else:
            zoning.append('NA')
    for poly_2 in tqdm(poly_list, total = len(poly_list)):
        poly = overlap_calc(idx2,poly_2)
        if not(poly == 0):
            idx_ = geo3[geo3.contains(poly)]
            flu.append((idx_['FLU'].iloc[0]))  
        else:
            flu.append('NA')
    pdb.set_trace()
    flu_final = convert_flu(flu)
    zoning_final = convert_zoning(zoning)
    geo1['flu'] = list(((np.array(flu_final))/max(flu_final)))
    geo1['zoning'] = list(((np.array(zoning_final))/max(zoning_final)))

    return geo1


def area_geo(geo1, idx):
    constr_area = []
    poly_area = []
    geo1 = geo1.to_crs(4326)
    # pdb.set_trace()
    for i in tqdm(range(len(geo1))):
        poly = geo1['geometry'][i]
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
        poly_area.append(poly_.area)
        hits = list(idx.intersection((poly.bounds), objects = True))
        area = poly_.area
        for box in hits:
            item_poly = box.object
            if (item_poly).intersects(poly):
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
                    if iou > 1e-5 :
                        area = area - inter.area
    
        constr_area.append(area)
        
    # pdb.set_trace()
    ## Adjust the area difference - check if it is correct(linear metric system )

    geo1['constr_area'] = list(((np.array(constr_area))/max(constr_area)))
    geo1 = geo1.to_crs(3857)
    return geo1

