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
import geopandas as gpd
sys.path.append('Utils/')
from Utils.poly_utils import buffer, polygon_list, graphs
from Utils.transport import *
from pollution import *
from logistics import *
from social import *
from density import *
from kmeans import *
import warnings
warnings.filterwarnings("ignore")


parser = argparse.ArgumentParser(description="Calculating objective criteria")
parser.add_argument('--save_dir', type=str, default='../',
                        help='put the path directory for saving the processed shapefile')
parser.add_argument('--road', type=str, default='../',
                        help='put the path to road shapefile')
parser.add_argument('--parcel', type=str, default='../',help='put the path to parcel shapefile')
parser.add_argument('--flu', type=str, default='../',help='put the path to flu shapefile')
parser.add_argument('--zoning', type=str, default='../',help='put the path to zoning shapefile')
parser.add_argument('--buildings', type=str, default='../',help='put the path to buildings shapefile')
parser.add_argument('--res_centroids', type=str, default='../',help='put the path to centroids shapefile')
parser.add_argument('--schools', type=str, default='../',help='put the path to schools shapefile')
parser.add_argument('--hospitals', type=str, default='../',help='put the path to hospitals shapefile')
parser.add_argument('--parcel_before', type=str, default='../',help='put the path to preceding years parcel shapefile')
parser.add_argument('--parcel_after', type=str, default='../',help='put the path to current years parcel shapefile')
parser.add_argument('--parks', type=str, default='../',help='put the path to parks shapefile')
parser.add_argument('--buffer_LOS', type=int, default=500,help='distance in m within which a parcel should have a road')
parser.add_argument('--buffer_air', type=int, default=5000,help='distance in m indicating the distance from a road air particles travel')
parser.add_argument('--buffer_noise', type=int, default=5000,help='distance in m indicating the distance from a road noise pollution is significant')
parser.add_argument('--buffer_density', type=int, default=5000,help='distance in m indicating the distance from a parcel for calculating the density of residential buildings')
parser.add_argument('--regenerate',action='store_true',help='enable if regeneration of the landuse clusters is required')
args = parser.parse_args()

geo1 = gpd.read_file(args.parcel).to_crs(3857)
geo2 = gpd.read_file(args.road).to_crs(3857)
geo3 = gpd.read_file(args.flu).to_crs(3857)
geo4 = gpd.read_file(args.zoning).to_crs(3857)
geo5 = gpd.read_file(args.buildings).to_crs(4326)
if(args.regenerate):
    area_calc(args.parcel_before, args.parcel_after, args.buildings, args.res_centroids)

geo6 = gpd.read_file(args.res_centroids).to_crs(4326)
geo7 = gpd.read_file(args.schools).to_crs(4326)
geo8 = gpd.read_file(args.hospitals).to_crs(4326)
geo9 = gpd.read_file(args.parks).to_crs(4326)
idx1 = graphs( geo2['geometry'])
idx2 = graphs( geo3['geometry'])  
idx3 = graphs( geo4['geometry'])
idx4 = graphs(geo5['geometry'])
#Proximity to Major freight corridoor
geo2_ = geo2[geo2.NAME.str.contains('^I-75(?:(?=.*ENTRANCE)|(?=.*EXIT)).*', regex= True, na=False)]
geo2_ = geo2_.reset_index(drop=True)
geo1 = distance_corridoor(geo1,geo2_)

# #LOS 
geo1 = LOS_geo(geo1, geo2, idx1, args.buffer_LOS)

#Pollution 
geo1 = pollution_geo(geo1,geo2,args.buffer_air, args.buffer_noise)

#Flood Plain
geo1 = flood_plain(geo1)

#Landuse
geo1 = landuse_geo(geo1, geo3, geo4, idx2,idx3)

#Construction Area
geo1 = area_geo(geo1,idx4)

#Residential Proximity
geo1 = res_geo(geo1,geo6)

#Public Proximity 
geo1 = public_geo(geo1, geo7, geo8)

#Environmental Proximity 
geo1 = env_geo(geo1, geo9)

#Density
#Include only residential buildings
geo1 = struct_density(geo1, idx4, args.buffer_density)

name_dir = 'criteria'
file_name = 'criteria.shp'

if not(os.path.exists(os.path.join(args.save_dir,name_dir))):
    os.makedirs(os.path.join(args.save_dir,name_dir))
print(os.path.join(args.save_dir,name_dir,(file_name)))
geo1.to_file(os.path.join(args.save_dir,name_dir,(file_name)))


