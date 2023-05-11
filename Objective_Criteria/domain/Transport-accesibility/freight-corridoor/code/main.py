import geopandas as gpd
import os
import sys
import pdb
import argparse
import pyproj
from tqdm import tqdm 
import numpy as np
import sys
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points

def distance_corridoor(geo1, geo2):
    # pdb.set_trace()
    dist = []
    geod = pyproj.Geod(ellps = 'WGS84')  
    for i in tqdm(range(len(geo1['geometry']))):
        best_d = sys.maxsize
        for j in range(len(geo2['geometry'])):
            line = geo2['geometry'][j]
            poly = geo1['geometry'][i]
            p1,p2 = nearest_points(poly.boundary, line)
            d = p2.distance(p1)
            if(d <best_d):
                best_d = d
            # d = nearest[1].distance(poly)
        dist.append(best_d)
    # pdb.set_trace()
    dist_ratio = list(1-((np.array(dist))/max(dist)))
    geo1['freight-distance'] = dist
    geo1['freight-distance-ratio'] = dist_ratio
    return geo1


parser = argparse.ArgumentParser(description="Raster to shapefile")
parser.add_argument('--save_dir', type=str, default='/media/ssd1/data/sanborn',
                        help='put the path to root directory')
parser.add_argument('--road', type=str, default='pmap_dpn/',
                        help='put the path to save geojson')
parser.add_argument('--parcel', type=str, default='pmap_dpn/',help='put the path to image directory')

args = parser.parse_args()

# pdb.set_trace()
geo1 = gpd.read_file(args.parcel).to_crs(3857)
geo2 = gpd.read_file(args.road).to_crs(3857)

geo2_ = geo2[geo2.NAME.str.contains('^I-75(?:(?=.*ENTRANCE)|(?=.*EXIT)).*', regex= True, na=False)]
geo2_ = geo2_.reset_index(drop=True)



# factor = 10
# geojson_df = distance_corridoor(geo1,geo2, factor)
geojson_df = distance_corridoor(geo1,geo2_)


name_dir = 'major-freight_corridoor'
file_name = 'major-freight_corridoor.shp'

if not(os.path.exists(os.path.join(args.save_dir,name_dir))):
    os.makedirs(os.path.join(args.save_dir,name_dir))
print(os.path.join(args.save_dir,name_dir,(file_name)))
geojson_df.to_file(os.path.join(args.save_dir,name_dir,(file_name)))