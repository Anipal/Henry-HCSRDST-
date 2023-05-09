import geopandas as gpd
import os
import argparse
import pdb
from tqdm import tqdm
import numpy as np
import pandas as pd
from shapely.ops import transform
import pyproj
import sys
sys.path.append('../../../../../scripts/Utils')
from poly_utils import buffer, polygon_list, graphs



def struct_density(geo1, idx, buffer_distance):
   
    struct = []
    density_list = []
    geo1['buffer'] = geo1.buffer(distance = buffer_distance)
    # pdb.set_trace()
    for i in tqdm(range(len(geo1))):
        poly = geo1['buffer'][i]
        hits = list(idx.intersection((poly.bounds), objects = True))
        total_hits = 0
        for box in hits:
            item_poly = box.object
            if (item_poly).intersects(poly):
                    inter = (item_poly).intersection(poly)
                    iou = float(inter.area / poly.area)                   
                    if iou > 1e-5 :
                        total_hits += 1

        
        area_diff = geo1['buffer'][i].area - geo1['geometry'][i].area
        density = total_hits/max(area_diff,1e-10)
        struct.append(total_hits)
        # area.append(area_diff)
        density_list.append(density)
    # pdb.set_trace()
    ## Adjust the area difference - check if it is correct(linear metric system )
    # geo1['area_diff'] = area
    geo1['structures'] = struct
    geo1['struct_density'] = list(1-(np.array(density_list))/(max(density_list),1e-10))
    geo1 = geo1.drop('buffer', axis=1)
    return geo1
    