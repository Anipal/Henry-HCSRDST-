import geopandas as gpd
from rtree import index
from tqdm import tqdm
import fiona
import pandas as pd
import json
import pdb


def buffer(geo1, buffer_distance):
    geo1 = geo1.to_crs(3857)
    geo1['buffer'] = geo1.buffer(distance = buffer_distance)
    buff_df = geo1.drop(columns=['geometry']).set_geometry('buffer')
    input_crs = geo1.crs
    buff_df = buff_df.to_crs(input_crs)
    return buff_df


def polygon_list(geo_dir):
    failure = []
# def polygon_list(geo_dir):
    # if(flag_class):
    #     transformer = pyproj.Transformer.from_crs("epsg:4326", "esri:54009")
    collection = list(fiona.open(geo_dir,'r'))
    df1 = pd.DataFrame(collection)
    collection = json.loads(df1.to_json(orient='records'))
    del df1
    #Convert to geodataframe
    test_gj_ = gpd.GeoDataFrame.from_features(collection)
    # pdb.set_trace()
    test_gj = test_gj_.where(test_gj_["PROP_USE_D"].str.contains("RES|HOME|FAMILY|APARTMENT|CONDO"))
    test_gj = test_gj.dropna(how='all',axis=0) 
    test_gj = test_gj.reset_index(drop=True)
    test_gj.crs = "EPSG:4326"
    test_gj = test_gj.to_crs(3857)
    del collection
    # wgs84 = pyproj.CRS('EPSG:4326')
    # utm = pyproj.CRS('EPSG:3857')
    # project = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform
    poly_list = []
    for i in tqdm(range(len(test_gj['geometry']))):
        poly = test_gj['geometry'][i]
        if poly.geom_type == 'MultiPolygon':
            poly_single = list(poly)
            for poly2 in poly_single:
                bo = poly2.bounds
                if(poly2.is_valid == False):
                    poly2 = poly2.simplify(tolerance=1e-8, preserve_topology=True)
                    if(poly2.is_valid == False and poly2.buffer(0).is_empty == False):
                        poly2 = poly2.buffer(0)
                if(poly2.is_valid):
                    poly_list.append(poly2)
                else:  
                    failure.append(poly2.exterior.coords.xy)
        else:
            if(poly.is_valid == False):
                # pdb.set_trace()
                # failure.append(poly)
                poly = poly.simplify(tolerance=1e-8, preserve_topology=True)
                if(poly.is_valid == False and poly.buffer(0).is_empty == False):
                    poly = poly.buffer(0)
            if(poly.is_valid):
                poly_list.append(poly)
            else:
                failure.append(poly)
    del test_gj
    # #else:
    return poly_list,failure

def graphs(poly_list):
    props = index.Property()
    idx = index.Index(properties = props)

    for i, p in tqdm(enumerate(poly_list)):
        bounds  = p.bounds
        if(bounds):
            idx.insert(i, bounds, obj = p)

    return idx