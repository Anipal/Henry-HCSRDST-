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
sys.path.append('../../../../scripts/Utils/')
from poly_utils import polygon_list_plain, graphs
from matplotlib import pyplot as plt
import warnings
from functools import partial
warnings.filterwarnings("ignore")

def overlap_calc(idx,poly):
    # print(type(idx))
    # pdb.set_trace()
    hits = list(idx.intersection((poly.bounds), objects = True))
    poly_accept = 0
    iou_max = 0
    for box in hits:
        item_poly = box.object
        if (item_poly).intersects(poly):
                inter = (item_poly).intersection(poly)
                if((inter.area/item_poly.area)>iou_max):
                    iou_max =  inter.area/item_poly.area
                    poly_accept = item_poly
    return poly_accept
                    
                      

def main():
    parser = argparse.ArgumentParser(description="Raster to shapefile")
    parser.add_argument('--save_dir', type=str, default='/media/ssd1/data/sanborn',help='put the path to root directory')
    parser.add_argument('--parcels', type=str, default='pmap_dpn/',help='put the path to image directory')
    parser.add_argument('--flu', type=str, default='pmap_dpn/',help='put the path to image directory')
    parser.add_argument('--zoning', type=str, default='pmap_dpn/',help='put the path to image directory')
    args = parser.parse_args()

    geo1 = (gpd.read_file(args.parcels)).to_crs(2697)
    # poly2,failure = polygon_list_plain(args.flu)
    # poly3,failure = polygon_list_plain(args.zoning)
    geo2 = (gpd.read_file(args.flu)).to_crs(2697)
    geo3 = (gpd.read_file(args.zoning)).to_crs(2697)
    idx1 = graphs( geo2['geometry'])  
    idx2 = graphs( geo3['geometry'])
    # pdb.set_trace()
    

    flu = []
    pool = multiprocessing.Pool(os.cpu_count())
    func_flu = partial(overlap_calc,idx1)
    poly_list = geo1['geometry']
    # pdb.set_trace()
    for poly_1 in tqdm(poly_list, total = len(poly_list)):
        poly = overlap_calc(idx1,poly_1)
    # for poly in tqdm(pool.imap_unordered(func_flu, poly_list), total = len(poly_list)):
        if not(poly == 0):
            idx_ = geo2[geo2.contains(poly)]
            flu.append((idx_['FLU']).to_string(index=False))  
        else:
            flu.append('NA')
    # pdb.set_trace()
    # pool.close()
    # pool.join()


    zoning = [] 
    # pool = multiprocessing.Pool(os.cpu_count())
    # func_zoning = partial(overlap_calc,idx2)
    pdb.set_trace()
    for poly_1 in tqdm(poly_list, total = len(poly_list)):
        poly = overlap_calc(idx2,poly_1)
    # for poly in pool.imap_unordered(func_zoning, poly_list):
    # for poly_1 in tqdm(poly_list, total = len(poly_list)):
    #     poly = overlap_calc(idx2,poly_1)
        if not(poly == 0):
            idx_ = geo3[geo3.contains(poly)]
            zoning.append((idx_['ZONING']).to_string(index=False))
        else:
            zoning.append('NA')
    # pool.close()
    # pool.join()

    # pdb.set_trace()
    geo1['flu_large'] = flu
    geo1['zoning'] = zoning
    name_dir = 'landuse'
    file_name = 'landuse.shp'

    if not(os.path.exists(os.path.join(args.save_dir,name_dir))):
        os.makedirs(os.path.join(args.save_dir,name_dir))
    print(os.path.join(args.save_dir,name_dir,(file_name)))
    geo1.to_file(os.path.join(args.save_dir,name_dir,(file_name)))
if __name__ == "__main__":
    main()


