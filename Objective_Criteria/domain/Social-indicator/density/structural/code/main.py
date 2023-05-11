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



def density_calc(geo1, idx, buffer_distance, factor):
    # pdb.set_trace()
    struct = []
    area = []
    density_list = []
    input_crs = geo1.crs
    # check if the converted crs is correct 
    geo1 = geo1.to_crs(3857)
    geo1['buffer'] = geo1.buffer(distance = buffer_distance)

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
        density = total_hits/area_diff
        struct.append(total_hits)
        area.append(area_diff)
        density_list.append(density)
    # pdb.set_trace()
    ## Adjust the area difference - check if it is correct(linear metric system )
    geo1['area_diff'] = area
    geo1['structures'] = struct
    geo1['struct_density'] = list((factor*np.array(density_list))/max(density_list))
    # for i in tqdm(range(len(geo1))):
    #     geo1['struct_density'][i] = float(geo1['struct_density'][i])
    geo1 = geo1.drop('buffer', axis=1)
    geo1 = geo1.to_crs(input_crs)
    return geo1


def main():
    parser = argparse.ArgumentParser(description="Raster to shapefile")
    parser.add_argument('--save_dir', type=str, default='/media/ssd1/data/sanborn',help='put the path to root directory')
    parser.add_argument('--parcels', type=str, default='pmap_dpn/',help='put the path to image directory')
    parser.add_argument('--buildings', type=str, default='pmap_dpn/',help='put the path to image directory')
    parser.add_argument('--buffer_distance', type=float, default=1,help='put the path to image directory')
    args = parser.parse_args()
    
    #Decide the buffer from literature
    buffer_distance = args.buffer_distance * 1000
    #Filter out residential parcels
    geo1 = gpd.read_file(args.parcels)
    # pdb.set_trace()
    geo2,failure = polygon_list(args.buildings)
    idx = graphs(geo2)
    
    # pdb.set_trace()
    geojson_df = density_calc(geo1, idx, buffer_distance,factor=10)
    geojson_buffer = buffer(geo1,buffer_distance)

    name_dir = 'structural_density'
    file_name = 'structural_density_2.shp'
    file_name_2 = 'buffer_2.shp'

    if not(os.path.exists(os.path.join(args.save_dir,name_dir))):
        os.makedirs(os.path.join(args.save_dir,name_dir))
    print(os.path.join(args.save_dir,name_dir,(file_name)))
    geojson_df.to_file(os.path.join(args.save_dir,name_dir,(file_name)))
    geojson_buffer.to_file(os.path.join(args.save_dir,name_dir,(file_name_2)))
if __name__ == "__main__":
    main()