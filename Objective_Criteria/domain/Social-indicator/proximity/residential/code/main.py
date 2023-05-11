import geopandas as gpd
import os
import sys
import pdb
sys.path.append('../../../../../scripts/Utils')
pdb.set_trace()
from distance import distance_calc
# import Objective_Criteria
import argparse


parser = argparse.ArgumentParser(description="Raster to shapefile")
parser.add_argument('--save_dir', type=str, default='/media/ssd1/data/sanborn',
                        help='put the path to root directory')
parser.add_argument('--centroids', type=str, default='pmap_dpn/',
                        help='put the path to save geojson')
parser.add_argument('--parcels', type=str, default='pmap_dpn/',help='put the path to image directory')

args = parser.parse_args()

pdb.set_trace()
geo1 = gpd.read_file(args.parcels)
geo2 = gpd.read_file(args.centroids)
geo2_ = geo2[geo2['Area']=='Residential']
geo2_ = geo2_.reset_index(drop=True)



factor = 10
geojson_df = distance_calc(geo1,geo2, factor)


name_dir = 'residential'
file_name = 'residential.shp'

if not(os.path.exists(os.path.join(args.save_dir,name_dir))):
    os.makedirs(os.path.join(args.save_dir,name_dir))
print(os.path.join(args.save_dir,name_dir,(file_name)))
geojson_df.to_file(os.path.join(args.save_dir,name_dir,(file_name)))
