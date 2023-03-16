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
from poly_utils import polygon_list, graphs
from matplotlib import pyplot as plt
import warnings
from functools import partial
warnings.filterwarnings("ignore")

def overlap_calc(poly,idx):
    hits = list(idx.intersection((poly.bounds), objects = True))
    for box in hits:
        item_poly = box.object
        if (item_poly).intersects(poly):
                inter = (item_poly).intersection(poly)
                if((inter.area/item_poly.area)>=0.1):
                     return item_poly 

def main():
    parser = argparse.ArgumentParser(description="Raster to shapefile")
    parser.add_argument('--save_dir', type=str, default='/media/ssd1/data/sanborn',help='put the path to root directory')
    parser.add_argument('--parcels_save', type=str, default='pmap_dpn/',help='put the path to image directory')
    parser.add_argument('--flu', type=str, default='pmap_dpn/',help='put the path to image directory')
    parser.add_argument('--zoning', type=str, default='pmap_dpn/',help='put the path to image directory')
    args = parser.parse_args()

    geo1 = gpd.read_file(args.parcels_save)
    geo2,failure = polygon_list(args.flu)
    geo3,failure = polygon_list(args.zoning)
    idx1 = graphs(geo2)  
    idx2 = graphs(geo3)

    

    flu = []
    pool = multiprocessing.Pool(os.cpu_count())
    func_flu = partial(overlap_calc,idx1)
    for poly,i in tqdm(pool.imap_unordered(func_flu, geo1), total = len(geo1)):
        if(poly):
            idx = geo2[geo2.contains(poly)]
            flu.append(geo2.iloc[idx]['FLU'])  
        else:
            flu.append('NA')
    pool.close()
    pool.join()


    zoning = [] 
    pool = multiprocessing.Pool(os.cpu_count())
    func_zoning = partial(overlap_calc,idx2)
    for poly,i in tqdm(pool.imap_unordered(func_zoning, geo2), total = len(geo2)):
        if(poly):
            idx = geo2[geo2.contains(poly)]
            zoning.append(geo2.iloc[idx]['ZONING'])
        else:
            zoning.append('NA')
    pool.close()
    pool.join()


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


