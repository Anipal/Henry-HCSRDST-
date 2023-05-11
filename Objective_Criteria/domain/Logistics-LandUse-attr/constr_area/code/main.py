import geopandas as gpd
import os
import argparse
import pdb
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
warnings.filterwarnings("ignore")

def area_calc(geo1, idx):
    # pdb.set_trace()
    constr_area = []
    poly_area = []
    input_crs = geo1.crs
    # check if the converted crs is correct 
    # geo1 = geo1.to_crs(3857)
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
        hits = list(idx.intersection((poly_.bounds), objects = True))
        area = poly_.area
        for box in hits:
            item_poly = box.object
            if (item_poly).intersects(poly):
                    item_poly_ = geo1['geometry'][i]
                    poly_= ops.transform(partial(
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

    geo1['constr_area'] = constr_area
    geo1['area'] = poly_area
    # print('Max ', max(area), 'Min ', min(area))
    # for i in tqdm(range(len(geo1))):
    #     geo1['struct_density'][i] = float(geo1['struct_density'][i])
    geo1 = geo1.to_crs(input_crs)
    return geo1


def main():
    parser = argparse.ArgumentParser(description="Raster to shapefile")
    parser.add_argument('--save_dir', type=str, default='/media/ssd1/data/sanborn',help='put the path to root directory')
    parser.add_argument('--parcels', type=str, default='pmap_dpn/',help='put the path to image directory')
    parser.add_argument('--buildings', type=str, default='pmap_dpn/',help='put the path to image directory')
    args = parser.parse_args()
    
    #Decide the buffer from literature
    #Filter out residential parcels
    geo1 = gpd.read_file(args.parcels)
    # pdb.set_trace()
    geo2,failure = polygon_list(args.buildings)
    idx = graphs(geo2)
    
    # pdb.set_trace()

    geojson_df = area_calc(geo1, idx)
    # pdb.set_trace()
    # quant = geo1['constr_area'].quantile([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
    geo1['area_bins'] = pd.qcut(geo1['constr_area'],q=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1], labels=[1,2,3,4,5,6,7,8,9,10])

    name_dir = 'constr_area'
    file_name = 'constr_area.shp'

    if not(os.path.exists(os.path.join(args.save_dir,name_dir))):
        os.makedirs(os.path.join(args.save_dir,name_dir))
    print(os.path.join(args.save_dir,name_dir,(file_name)))
    geojson_df.to_file(os.path.join(args.save_dir,name_dir,(file_name)))
if __name__ == "__main__":
    main()

    