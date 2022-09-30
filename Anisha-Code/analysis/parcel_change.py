
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

def change_calc(poly_list_1,poly_list_2,class_1,class_2,args):
    flag1 = np.zeros((len(poly_list_1)), dtype = 'uint8')
    class_3 = ['no']*len(flag1)
    for i in tqdm(range(len(poly_list_1))):
        for j in tqdm(range(len(poly_list_2))):
            item_poly = poly_list_2[j]
            if (item_poly).intersects(poly_list_1[i]):
                    inter = (item_poly).intersection(poly_list_1[i])
                    union = (item_poly).union(poly_list_1[i])
                    iou = float(inter.area / union.area)                   
                    if iou > 0.5 :
                        # pdb.set_trace()
                        if not(class_1[i]==class_2[j]):
                            flag1[i] = 1
                            class_3[i] = class_2[j] + '_to_' + class_1[i]     
 

    return flag1, class_3

def flag_compare(flag,poly_list,class_3):
    unq = []
    class_4 = []
    for i in tqdm(range(len(poly_list))):
        if flag[i] == 1:
                unq.append(poly_list[i])
                class_4.append(class_3[i])
    return unq,class_4

########################################################################################################################
#READING POLYGON INTO LIST
# pdb.set_trace()
poly_list_before,failure,class_before = polygon_list_class(args.geo1_dir)
poly_list_after,failure,class_after = polygon_list_class(args.geo2_dir)

#######################################################################################################################

year_before = args.geo1_dir.split('/')[-1].split('_')[0]
year_after = args.geo2_dir.split('/')[-1].split('_')[0]
#######################################################################################################################
#CREATING GRAPHS


#######################################################################################################################

print('Before',len(poly_list_before))
print('After',len(poly_list_after))

#######################################################################################################################
##CHANGE

print('MAIN 1')

flag_after_nochange, class_3 = change_calc(poly_list_after, poly_list_before,class_after,class_before,args)
change_after,class_4 = flag_compare(flag_after_nochange,poly_list_after,class_3)




print('CHANGE ')
print('change_after',len(change_after))





#######################################################################################################################
##SAVING CHANGE GEOJSON


change_after = MultiPolygon(change_after)

if len(change_after.geoms) > 1:
            geojson_df = gpd.GeoDataFrame(({'geometry':change_after,'change_type':class_4}), crs={'init': 'epsg:4326'})
            # geojson_df.columns = ['geometry']
            if not(os.path.exists(os.path.join(args.save_dir,(year_after+'_v_'+year_before)))):
                os.makedirs(os.path.join(args.save_dir,(year_after+'_v_'+year_before)))
            geojson_df.to_file((os.path.join(args.save_dir,(year_after+'_v_'+year_before),(year_after+'_v_'+year_before+'.shp'))))


elif len(change_after.geoms) == 1 and change_after[0].area > 0.0:
                geojson_df = gpd.GeoDataFrame(({'geometry':change_after,'change_type':class_4}), crs={'init': 'epsg:4326'})
                # geojson_df.columns = ['geometry']
                geojson_df.to_file((os.path.join(args.save_dir,(year_after+'_v_'+year_before),(year_after+'_v_'+year_before+'.shp'))))
