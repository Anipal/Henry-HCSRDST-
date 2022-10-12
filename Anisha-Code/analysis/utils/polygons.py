from shapely.ops import cascaded_union
from shapely import geometry
import geopandas as gpd
import os
import multiprocessing
from shapely.geometry import shape, mapping,MultiPolygon
import pdb
import glob
from tqdm import tqdm
import numpy as np
import time
import json
import fiona
# from geojson_precision import _set_precision
import shapely.wkt
from functools import partial
import pandas as pd
from rtree import index
import pyproj
# from geojson_precision import _set_precision
import shapely
# INTRO- Function to reduce the floating point precision of the geojson to improve memory efficiency
# INPUT - geojson coordinates, floating point precision value
# OUTPUT - list of reduced precision cordinates
# def set_precision(coords, precision):
#     result = []
#     try:
#         return round(coords, int(precision))
#     except TypeError:
#         for coord in coords:
#             result.append(_set_precision(coord, precision))
#     return result

# INTRO- Returns all individual polygons from a particular geojson
# INPUT - Geojson path
# OUTPUT - list of polygons
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
    test_gj = gpd.GeoDataFrame.from_features(collection)
    del collection
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
           # pdb.set_trace()
           # print(test_gj['geometry'])
            if(poly.is_valid == False):
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
    # return poly_list



# INTRO- Returns rtree of the polygon list
# INPUT - Polygon list
# OUTPUT - rtree 

def graphs(poly_list):
    props = index.Property()
    idx = index.Index(properties = props)

    for i, p in tqdm(enumerate(poly_list)):
        bounds  = p.bounds
        if(bounds):
            idx.insert(i, bounds, obj = p)

    return idx

def polygon_zoning(geo_dir,accepted_zones):
    failure = []
    collection = list(fiona.open(geo_dir,'r'))
    df1 = pd.DataFrame(collection)
    collection = json.loads(df1.to_json(orient='records'))
    del df1
    #Convert to geodataframe
    test_gj = gpd.GeoDataFrame.from_features(collection)
    del collection
    poly_list = []
    
    for i in tqdm(range(len(test_gj['geometry']))):
        try:
            if(test_gj['ZONING'][i] in accepted_zones):
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
                # pdb.set_trace()
                # print(test_gj['geometry'])
                    if(poly.is_valid == False):
                        # failure.append(poly)
                        poly = poly.simplify(tolerance=1e-8, preserve_topology=True)
                        if(poly.is_valid == False and poly.buffer(0).is_empty == False):
                            poly = poly.buffer(0)
                    if(poly.is_valid):
                        poly_list.append(poly)
                    else:
                        failure.append(poly)
        except:
            if(test_gj['ZONING_1'][i] in accepted_zones):
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
                # pdb.set_trace()
                # print(test_gj['geometry'])
                    if(poly.is_valid == False):
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