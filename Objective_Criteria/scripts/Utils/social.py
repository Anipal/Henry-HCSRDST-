import geopandas as gpd
import pandas as pd
import os
import pdb
from tqdm import tqdm
import argparse
from shapely.geometry import Point, MultiPoint
from shapely.ops import nearest_points, transform
import pyproj
from functools import partial
import numpy as np
import requests
import pygris


'''

Calculates the distance of a parcel to the nearest point from a DataFrame of many points
INPUTS: Parcel data (geopandas DataFrame), point data (geopandas DataFrame)
OUTPUT: normalized nearest distance to a point for each parcel 
'''

def distance_calc(df1, point):

    #Converting crs to 4326 for proper conversion 
    df1 = df1.to_crs(4326)
    dist = []

    #Setting the projection 
    geod = pyproj.Geod(ellps = 'WGS84')
    for i in tqdm(range(len(df1['geometry']))):

        #Finding centroid of the parcel
        poly = df1['geometry'][i].centroid   
        #Finding the nearest point geometry in point geoDataFrame from the given parcel  
        nearest = nearest_points(poly, point)
        #Calculating the distance in m to the nearest point 
        _,_,d = geod.inv(nearest[1].x, nearest[1].y, poly.x, poly.y)  
        # d = nearest[1].distance(poly)
        dist.append(d)
    #Normalizing the distance 
    dist_ratio = list((np.array(dist))/max(dist))
    return dist, dist_ratio

def apportion(df1, df2, join_fields):

    if type(join_fields) == str:
        join_fields = [join_fields]

    #Spatial join intersect df2 with df1 via intersection, calculate area.
    #Set index for df1
    df1_ = df1.copy()
    df1_['spatial_index'] = df1_['geometry'].to_wkt()

    #Get intersection of df1 and df2
    inter = gpd.overlay(df1_, df2, how = 'intersection')

    #Group by spatial index
    inter['area'] = inter['geometry'].area
    #Group by parcel geometry, then select max area from the intersection
    cleaned = inter.groupby('spatial_index').max('area').reset_index()[['spatial_index'] + join_fields]

    #Append back to original dataframe
    final = df1_.merge(cleaned, on = 'spatial_index', how = 'left').drop('spatial_index', axis = 1)

    #Return final
    return final

'''
Residential Proximity - Proximity of parcels to residential clusters 
INPUTS: Parcels data(geopandas polygon dataframe), Area clusters data (geopandas polygon dataframe)
OUTPUT: Parcels data with added column 'near-res', ratio of distance to nearest residential cluster
'''

def res_geo(df1, df2):

    #Filtering only those clusters which are either tagged as Residential or NO DEV 
    df2_ = df2[(df2['Area']=='NO DEV') | (df2['Area']=='Residential')]
    #For the filtered values to be sequential dropping their index 
    df2_ = df2_.reset_index(drop=True)
    #Converting the filtered cluster points to a MultiPoint geometry 
    point = MultiPoint(df2_.geometry)
    dist, dist_ratio = distance_calc(df1,point)

    #Assigning the near-res column the normalized value of the distance to the closest cluster point
    # df1['nearest-distance'] = dist
    df1['near-res'] = dist_ratio
    return df1


'''
Public Proximity - Parcels most suitable for construction based on their proximity from schools and hospitals  
INPUTS: Parcels data(geopandas polygon dataframe), Schools data(geopandas polygon dataframe), Hospitals data(geopandas polygon dataframe)
OUTPUT: Parcels data with added column 'near-pub', normalized scores between 0-1.
''' 


def public_geo(df1, df2, df3):

    #Combining all the points from Schools and Hospitals to create a new DataFrame 
    point = MultiPoint(df2['geometry'].tolist() + df3['geometry'].tolist())
    #Calculating distance of each parcel to nearest vulnerable point
    _ , dist_ratio = distance_calc(df1,point)

    #Assigning the near-pub column the normalized value of the distance to the closest School or Hospital point
    df1['near-pub'] = dist_ratio
    return df1

'''
Environmental Proximity - Parcels most suitable for construction based on their proximity from environmentally sensitive areas
INPUTS: Parcels data(geopandas polygon dataframe), Parks data(geopandas polygon dataframe)
OUTPUT: Parcels data with added column 'near-env', normalized scores between 0-1.
''' 

def env_geo(df1, df2):

    #Converting the environmentally sensitive area Points geometry into a MultiPoint geometry
    point = MultiPoint(df2.geometry)
    #Finding distance of each parcel to the nearest environmentally sensitive area
    _ , dist_ratio = distance_calc(df1,point)
    #Assigning the near-env column the normalized value of the distance to the closest environmentally sensitive area
    df1['near-env'] = dist_ratio
    return df1

'''
Social Vulnerability (SVI) - Parcels most suitable for construction based on the Social Vulnerability Index (SVI) of their containing census tract.
INPUTS: Parcels data(geopandas polygon dataframe), SVI data(geopandas polygon dataframe), variable name of the SVI score from the SVI dataframe(refer to SVI documentation online).
OUTPUT: Parcels data with added column 'svi', normalized scores between 0-1.
''' 

def svi_geo(df1, df2, varname='RPL_THEMES'):
    svi = df2.copy()[[varname, 'geometry']].to_crs(df1.crs)

    #Replace invalid values with zero / 1
    svi.loc[svi[varname] < 0, varname] = 0
    svi.loc[svi[varname] > 1, varname] = 1

    #Append SVI score to df1
    df1 = apportion(df1, svi, varname).rename(columns={varname:'svi'})
    #Update score to reverse, so a higher SVI is bad
    df1['svi'] = 1 - df1['svi']

    return df1


'''
Population Density - Parcels most suitable for construction based on the population density of their containing census tract.
INPUTS: Parcels data(geopandas polygon dataframe), ACS-5 Year, ACS-5 population variable(may change based on newer survey releases), FIPS code for Henry County
OUTPUT: Parcels data with added column 'pop-dens', normalized scores between 0-1.
'''

def pop_density(df1, year=2021, varname='B01001_001E', fips:str='13151'):

    #URL for pulling population estimates for each tract.
    furl = 'https://api.census.gov/data/{}/acs/acs5?get={}&for=tract:*&in=state:{}+county:{}'.format(str(year), varname, fips[:2], fips[-3:])
    #Execute request
    raw = requests.get(furl).json()
    #Convert to dataframe
    df2 = pd.DataFrame(raw[1:], columns = raw[0]).rename(columns={varname:'pop'})
    #Get geometries using pygris, setting to EPSG:26967 to depict population density in km^2
    geoms = pygris.tracts(year=year, state=fips[:2], county=fips[-3:])[['STATEFP', 'COUNTYFP', 'TRACTCE', 'geometry']].rename(columns={'STATEFP':'state','COUNTYFP':'county','TRACTCE':'tract'}).to_crs('EPSG:26967')
    #Calculate area in km
    geoms['area'] = geoms['geometry'].area * 1e-6
    #Merge geometries to population density frame
    df2_ = df2.merge(geoms, on = ['state','county','tract'], how = 'left')
    #Convert to geodataframe
    df2_ = gpd.GeoDataFrame(df2_)
    #Calculate population density
    df2_['pop_dens'] = df2_['pop'].apply(float) / df2_['area'].apply(float)
    #Min-max transformation to normalize, then reverse so a higher population density is bad
    df2_['pop-dens'] = (df2_['pop_dens'] - np.min(df2_['pop_dens'])) / (np.max(df2_['pop_dens']) - np.min(df2_['pop_dens']))
    df2_['pop-dens'] = 1-df2_['pop-dens']
    #Re-project
    df2_ = df2_.to_crs(df1.crs)
    #Apportion with parcels
    final = apportion(df1, df2_, 'pop-dens')

    return final




    