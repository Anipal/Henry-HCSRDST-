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
from poly_utils import graphs


'''
Finding parcels vulnerable to flooding 
INPUTS: Parcels data(geopandas polygon dataframe), Buildings data only for residential buildings (rtree index), Buffer added to the parcel in m for density calculation (int)
OUTPUT: Parcels data with added column 'struct_density', normalized scores between 0-1.
'''

def struct_density(geo1, idx, buffer_distance):
   
    struct = []
    density_list = []
    # Adding Buffer to each parcel in geo1
    geo1['buffer'] = geo1.buffer(distance = buffer_distance)
    for i in tqdm(range(len(geo1))):
        poly = geo1['buffer'][i]
        #Finding the number of residential buildings intersecting with each parcel
        hits = list(idx.intersection((poly.bounds), objects = True))
        total_hits = 0
        for box in hits:
            item_poly = box.object
        # Checking for proper intersection for each polygon in hits as sometimes rtree takes nearby polygons which are not intersecting
            if (item_poly).intersects(poly):
                    inter = (item_poly).intersection(poly)
                    iou = float(inter.area / poly.area)                   
                    if iou > 1e-5 :
                        total_hits += 1

        # Calculating the exact area in which the buildings are present 
        area_diff = geo1['buffer'][i].area - geo1['geometry'][i].area
        # Calculating density 
        density = total_hits/max(area_diff,1e-10)
        struct.append(total_hits)
        # area.append(area_diff)
        density_list.append(density)
    # geo1['area_diff'] = area
    # geo1['structures'] = struct
    print('Density_list',len(density_list))

    # Normalizing the value of density with 1 being a site most preferable for construction and 0 least preferable 
    geo1['struct_density'] = list(1-(np.array(density_list))/max(max(density_list),1e-10))
    # Dropping buffer geometry column from the geoDataFrame
    geo1 = geo1.drop('buffer', axis=1)
    return geo1
    