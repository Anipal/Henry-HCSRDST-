
import geopandas as gpd
import os
from geopy import distance
import multiprocessing
from shapely.geometry import shape, mapping,MultiPolygon
import pdb
import glob
from tqdm import tqdm
import numpy as np
import time
import json
import fiona
import pyproj
# from geojson_precision import _set_precision
import shapely.wkt
from functools import partial
import pandas as pd
import multiprocessing
from utils.spatial_utils import iou as calc_iou
import argparse
from rtree import index
from utils.polygons import *
import operator

parser = argparse.ArgumentParser(description="Raster to shapefile")
parser.add_argument('--save_dir', type=str, default='/media/ssd1/data/sanborn',
                        help='put the path to root directory')
parser.add_argument('--geo1_dir', type=str, default='pmap_dpn/',
                        help='put the path to save geojson')
parser.add_argument('--geo2_dir', type=str, default='pmap_dpn/',help='put the path to image directory')
parser.add_argument('--change_threshold', type=float, default=0.3,help='start (default: 0.6)')

args = parser.parse_args()

def change_calc(poly_list_1,poly_list_2,idx,args):
    flag1 = np.zeros((len(poly_list_1)), dtype = 'uint8')
    for i in tqdm(range(len(poly_list_1))):
            hits1 = list(idx.intersection((poly_list_1[i].bounds), objects = True))
            for box in hits1:
                item_poly = box.object
                if (item_poly).intersects(poly_list_1[i]):
                        inter = (item_poly).intersection(poly_list_1[i])
                        union = (item_poly).union(poly_list_1[i])
                        iou = float(inter.area / union.area)                   
                        if iou > args.change_threshold :
                            flag1[i] = 1
    return flag1, poly_list_2

def flag_compare(flag,poly_list):
    unq = []

    for i in tqdm(range(len(poly_list))):
        if flag[i] != 1:
                unq.append(poly_list[i])
    return unq

########################################################################################################################
#READING POLYGON INTO LIST
# pdb.set_trace()
poly_list_before,failure = polygon_list(args.geo1_dir)
poly_list_after,failure = polygon_list(args.geo2_dir)

#######################################################################################################################

year_before = args.geo1_dir.split('/')[-1].split('_')[0]
year_after = args.geo2_dir.split('/')[-1].split('_')[0]
#######################################################################################################################
#CREATING GRAPHS

idx_before = graphs(poly_list_before)
idx_after = graphs(poly_list_after)
#######################################################################################################################

print('Before',len(poly_list_before))
print('After',len(poly_list_after))

#######################################################################################################################
##CHANGE

print('MAIN 1')
#Calling change function and comparing after polygons with before rtree to find all new constructions or additions
poly_list_before = set([str(x) for x in poly_list_before])
flag_after_nochange, poly_list_before = change_calc(poly_list_after, poly_list_before, idx_before,args)
change_after = flag_compare(flag_after_nochange,poly_list_after)

#Converting poly_list_before back to a polygon list
poly_list_before = list(poly_list_before)
poly_list_before = [shapely.wkt.loads(x) for x in poly_list_before]

#Calling change function and comparing before polygons with after rtree to find all demolitions
poly_list_after = set([str(x) for x in poly_list_after])
flag_before_nochange, poly_list_after = change_calc(poly_list_before, poly_list_after, idx_after,args)
change_before = flag_compare(flag_before_nochange,poly_list_before)


print('CHANGE ')
print('change_after',len(change_after))
print('change_before',len(change_before))
change_all = change_after+change_before
year_change = [year_after+'_v_'+year_before]*len(change_all)
type_change = ['new']*len(change_after) + ['old']*len(change_before)




#######################################################################################################################
##SAVING CHANGE GEOJSON


change_all = MultiPolygon(change_all)

if len(change_all.geoms) > 1:
            geojson_df = gpd.GeoDataFrame(({'geometry':change_all,'year':year_change,'change_type':type_change}), crs={'init': 'epsg:4326'})
            # geojson_df.columns = ['geometry']
            if not(os.path.exists(os.path.join(args.save_dir,(year_after+'_v_'+year_before)))):
                os.makedirs(os.path.join(args.save_dir,(year_after+'_v_'+year_before)))
            geojson_df.to_file((os.path.join(args.save_dir,(year_after+'_v_'+year_before),(year_after+'_v_'+year_before+'.shp'))))


elif len(change_all.geoms) == 1 and change_all[0].area > 0.0:
                geojson_df = gpd.GeoDataFrame(({'geometry':change_all,'year':year_change,'change_type':type_change}), crs={'init': 'epsg:4326'})
                # geojson_df.columns = ['geometry']
                geojson_df.to_file((os.path.join(args.save_dir,(year_after+'_v_'+year_before),(year_after+'_v_'+year_before+'.shp'))))
