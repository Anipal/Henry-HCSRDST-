print('Starting')
import geopandas as gpd
import os
import sys
import pdb
import argparse
import pyproj
from tqdm import tqdm 
import numpy as np
import sys
import time
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points
import geopandas as gpd
sys.path.append('Utils/')
from Utils.poly_utils import graphs
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
parser.add_argument('--svi', type=str, default='../',help='put the path to svi shapefile')
parser.add_argument('--buffer_LOS', type=int, default=500,help='distance in m within which a parcel should have a road')
parser.add_argument('--buffer_air', type=int, default=5000,help='distance in m indicating the distance from a road air particles travel')
parser.add_argument('--buffer_noise', type=int, default=5000,help='distance in m indicating the distance from a road noise pollution is significant')
parser.add_argument('--buffer_density', type=int, default=1000,help='distance in m indicating the distance from a parcel for calculating the density of residential buildings')
parser.add_argument('--regenerate',action='store_true',help='enable if regeneration of the landuse clusters is required')
args = parser.parse_args()

'''
Starting the timer to clock time taken to run script
'''
start = time.time()

'''
Reading all the shapefiles into geopandas for further processing
Converting to EPSG:3857 for easy calculation in meters, EPSG 4326 for others
'''
print('Reading shapefiles')
geo1 = gpd.read_file(args.parcel).to_crs(3857)
geo2 = gpd.read_file(args.road).to_crs(3857)
geo3 = gpd.read_file(args.flu).to_crs(3857)
geo4 = gpd.read_file(args.zoning).to_crs(3857)
geo5 = gpd.read_file(args.buildings).to_crs(4326)
geo6 = gpd.read_file(args.res_centroids).to_crs(4326)
geo7 = gpd.read_file(args.schools).to_crs(4326)
geo8 = gpd.read_file(args.hospitals).to_crs(4326)
geo9 = gpd.read_file(args.parks).to_crs(4326)
geo10 = gpd.read_file(args.svi).to_crs(3857)

'''
If new zoning files have been created then the clustering shapefile 'areas' has to be regenerated for proper results
'''
if(args.regenerate):
    print('Rcreating areas file')
    area_calc(args.parcel_before, args.parcel_after, args.buildings, args.res_centroids)
'''
Generating rtree idx for the required geopandas for quick computation
'''

idx1 = graphs( geo2['geometry'])
idx2 = graphs( geo3['geometry'])  
idx3 = graphs( geo4['geometry'])
idx4 = graphs(geo5['geometry'])



'''
Residential Proximity - Proximity of parcels to residential clusters 
Inputs: Parcels data(geopandas polygon dataframe), Area clusters data (geopandas polygon dataframe)
Output: Parcels data with added column 'near-res', ratio of distance to nearest residential cluster
'''
print('Residential Proximity')
geo1 = res_geo(geo1,geo6)


'''
Proximity to Major freight corridoor - Proximity of parcels to Major Freight Corridoors 
Inputs: Parcels data(geopandas polygon dataframe), Road data containing only entry and exit ramps (geopandas line dataframe)
Output: Parcels data with added column 'MajorCor', ratio of distance to entrance or exit ramp to major highways
'''
print('Proximity to Major freight corridoor')
geo2_ = geo2[geo2.NAME.str.contains('^I-75(?:(?=.*ENTRANCE)|(?=.*EXIT)).*', regex= True, na=False)]
geo2_ = geo2_.reset_index(drop=True)
geo1 = distance_corridoor(geo1,geo2_)

 
'''
LOS - Parcels with LOS information of closest road 
Inputs: Parcels data(geopandas polygon dataframe), Road data (geopandas line dataframe), Road data (rtree index), Buffer in m(int)
Output: Parcels data with added column 'LOS', LOS information in float values b/w 0-1
'''
print('LOS')
geo1 = LOS_geo(geo1, geo2, idx1, args.buffer_LOS)

'''
Pollution - Parcels containg information about vulnerability of parcel to pollution  
Inputs: Parcels data(geopandas polygon dataframe), Road data (geopandas line dataframe),Distance from I-75 where air pollution levels will be high(int), Distance from I-75 where noise pollution levels will be high(int)
Output: Parcels data with added columns 'air_poll', 'noise_poll'
''' 
print('Pollution')
geo1 = pollution_geo(geo1,geo2,args.buffer_air, args.buffer_noise)

'''
Flood Plain - Parcels vulnerable to flooding  
Inputs: Parcels data(geopandas polygon dataframe)
Output: Parcels data with added columns 'flood', indicating if the parcel is vulnerable to flood with 0 being vulnerable and 1 being suitable for construction
''' 
print('Flood Plain')
geo1 = flood_plain(geo1)

'''
Landuse - Parcels suitable for construction based on land use and zoning type  
Inputs: Parcels data(geopandas polygon dataframe), Land Use data(geopandas polygon dataframe), Zoning data(geopandas polygon dataframe), Land Use data(rtree index), Zoning data(rtree index)
Output: Parcels data with added columns 'flu','zoning' normalized scores between 0-1.
''' 
print('Landuse')
geo1 = landuse_geo(geo1, geo3, geo4, idx2,idx3)

'''
Construction Area - Parcels most suitable for construction based on amount of free area available within the parcel  
Inputs: Parcels data(geopandas polygon dataframe), Buildings data(rtree index)
Output: Parcels data with added columns 'flu','zoning' normalized scores between 0-1.
''' 
print('Construction Area')
geo1 = area_geo(geo1,idx4)

'''
Public Proximity - Parcels most suitable for construction based on their proximity from schools and hospitals  
Inputs: Parcels data(geopandas polygon dataframe), Schools data(geopandas polygon dataframe), Hospitals data(geopandas polygon dataframe)
Output: Parcels data with added column 'near-pub', normalized scores between 0-1.
''' 

print('Public Proximity')
geo1 = public_geo(geo1, geo7, geo8)

'''
Environmental Proximity - Parcels most suitable for construction based on their proximity from environmentally sensitive areas
Inputs: Parcels data(geopandas polygon dataframe), Parks data(geopandas polygon dataframe)
Output: Parcels data with added column 'near-env', normalized scores between 0-1.
''' 
print('Environmental Proximity') 
geo1 = env_geo(geo1, geo9)

'''
Social Vulnerability - Parcels most suitable for construction based on their Social Vulnerability Index (SVI) Score
Inputs: Parcels data(geopandas polygon dataframe), SVI score geodataframe
Output: Parcels data with added column 'svi', normalized scores between 0-1.
''' 
print("Social Vulnerability")
geo1 = svi_geo(geo1, geo10)


'''
Structural Density - Parcels most suitable for construction based on residential density around the parcel
Inputs: Parcels data(geopandas polygon dataframe), Buildings data only for residential buildings (rtree index)
Output: Parcels data with added column 'struct_density', normalized scores between 0-1.
''' 
print('Structural Density')
geo5_ = geo5[geo5.PROP_USE_D.str.contains('(RES COM)|(HOME)|(APARTMENT)|(FAMILY)|(CONDO)|(RESIDENTIAL)', na=False)]
geo5_ = geo5_.reset_index(drop=True)
geo5_ = geo5_.to_crs(3857)
idx5_ = graphs(geo5_['geometry'])
geo1 = struct_density(geo1, idx5_, args.buffer_density)
geo1 = geo1.to_crs(26967)

name_dir = 'criteria'
file_name = 'criteria.shp'

if not(os.path.exists(os.path.join(args.save_dir,name_dir))):
    os.makedirs(os.path.join(args.save_dir,name_dir))

geo1.to_file(os.path.join(args.save_dir,name_dir,(file_name)))

print('Saving the file to the following location',os.path.join(args.save_dir,name_dir,(file_name)))

print('It took', time.time()-start, 'seconds.')
total_time = (time.time()-start)/3600
print('It took', total_time, 'hours.')

