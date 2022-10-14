import shapely
import geopandas as gpd 
import argparse
import pandas as pd 
import json 
from tqdm import tqdm 
import pyproj



def add_coords(df1):
    df = pd.DataFrame(columns = ['lat','lon','change'])
    # df_1 = pd.DataFrame(columns = ['lat','lon','change'])
    df['change'] = df1['change']
    collection = json.loads(df1.to_json(orient='records'))
    test_gj = gpd.GeoDataFrame.from_features(collection)
    test_gj.crs = "EPSG:2240"
    test_gj = test_gj.to_crs({'init': 'epsg:4326'}) 
    df['lon'] = test_gj['geometry'].x
    df['lat'] = test_gj['geometry'].y
    return df

def add_fields(df1,change):
    if(change):
        df1['change'] =['Y']*len(df1)
    else:
       df1['change'] =['N']*len(df1) 
    return df1 




