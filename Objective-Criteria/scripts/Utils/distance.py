
import geopandas as gpd
import os
import pdb
from tqdm import tqdm
import argparse
from shapely.geometry import Point, MultiPoint
from shapely.ops import nearest_points, transform
import pyproj
from functools import partial
import numpy as np

parser = argparse.ArgumentParser(description="Raster to shapefile")
parser.add_argument('--save_dir', type=str, default='/media/ssd1/data/sanborn',
                        help='put the path to root directory')
parser.add_argument('--geo1_dir', type=str, default='pmap_dpn/',
                        help='put the path to save geojson')
parser.add_argument('--geo2_dir', type=str, default='pmap_dpn/',help='put the path to image directory')

args = parser.parse_args()

# pdb.set_trace()
def distance_calc(df1, df2, factor):
    
    dist = []
    point = MultiPoint(df2.geometry)
    geod = pyproj.Geod(ellps = 'WGS84')
    for i in tqdm(range(len(df1['geometry']))):
        poly = df1['geometry'][i].centroid   
        nearest = nearest_points(poly, point)
        _,_,d = geod.inv(nearest[1].x, nearest[1].y, poly.x, poly.y)  
        # d = nearest[1].distance(poly)
        dist.append(d/1000)
    # pdb.set_trace()
    dist_ratio = list((factor*np.array(dist))/max(dist))
    df1['nearest-distance'] = dist
    df1['nearest-distance-ratio'] = dist_ratio
    return df1


project = partial(
    pyproj.transform,
    pyproj.Proj('EPSG:4326'),
    pyproj.Proj('EPSG:32633'))

# geo1 =  transform(project,gpd.read_file(args.geo1_dir))
# geo2 =  transform(project,gpd.read_file(args.geo2_dir))
geo1 = gpd.read_file(args.geo1_dir)
geo2 = gpd.read_file(args.geo2_dir)
factor = 10
geojson_df = distance_calc(geo1,geo2, factor)


name_dir = args.geo2_dir.split('/')[-1].split('.')[0]
file_name = args.geo2_dir.split('/')[-1]

if not(os.path.exists(os.path.join(args.save_dir,name_dir))):
    os.makedirs(os.path.join(args.save_dir,name_dir))
print(os.path.join(args.save_dir,name_dir,(file_name)))
geojson_df.to_file(os.path.join(args.save_dir,name_dir,(file_name)))







