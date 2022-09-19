import osmnx as ox
import networkx as nx
import geopandas as gpd
import pdb
import os
from datetime import datetime
from tqdm import tqdm
import sys

def get_shp(bb,tags,date,save_path,type_,area):
    # pdb.set_trace()
    # gdf = ox.geometries_from_bbox(bb[0],bb[1],bb[2],bb[3],tags)
    if(type_ == 'graph'):
        if(area =='small_area'):
            gdf = ox.graph_from_bbox(bb[0],bb[1],bb[2],bb[3],network_type='drive')
        elif(area =='Georgia'):
            gdf = ox.graph_from_place("Georgia, USA", network_type='drive')
    elif(type_ == 'geometries'):
        gdf = ox.geometries_from_bbox(bb[0],bb[1],bb[2],bb[3],tags)

        # gdf = ox.graph_from_place("Georgia, USA", network_type='drive')
    if(type_ == "geometries"):
        gf1 = gdf[gdf.geometry.geom_type == 'Polygon']
        gf2 = gdf[gdf.geometry.geom_type == 'Point' ]
        gdf_save_1 = gf1.applymap(lambda x: str(x) if isinstance(x, list) else x)
        gdf_save_2 = gf2.applymap(lambda x: str(x) if isinstance(x, list) else x)
        gdf_save_2.to_file(os.path.join(save_path,date,(date+'_buildings_points.shp')))
        gdf_save_1.to_file(os.path.join(save_path,date,(date+'_roads_poly.shp')))
    elif(type_ == 'graph'):
        gdf_save_1 = gdf
        ox.save_graphml(gdf_save_1, os.path.join(save_path,date,(date+'_roads.gml')))
        if not(os.path.exists(os.path.join(save_path,date,'nx_shpfiles'))):
            os.makedirs(os.path.join(save_path,date,'nx_shpfiles'))
        ox.save_graph_shapefile(gdf_save_1, os.path.join(save_path,date,'nx_shpfiles/'))

area = sys.argv[1]
save_path = '/mnt/c/Users/apal72/Documents/Anisha/data/sample_data/OSM/' +area
if not (os.path.exists(save_path)):
    os.makedirs(save_path)
tags = {"natural": 'water'}
type_ = "graph" #can give graph or geometries
date = ["10-Sep-2022-15:59:02","10-Sep-2021-15:59:02","10-Sep-2020-15:59:02","10-Sep-2019-15:59:02","10-Sep-2018-15:59:02","10-Sep-2017-15:59:02","10-Sep-2016-15:59:02","10-Sep-2015-15:59:02","10-Sep-2014-15:59:02","10-Sep-2013-15:59:02","10-Sep-2012-15:59:02","10-Sep-2011-15:59:02"]
bbox = [33.4627578429999986,33.4112425320000028, -84.1123744390000070,-84.2104397300000045]
for i in tqdm(date,total = len(date)):
    d = datetime.strptime(i, "%d-%b-%Y-%H:%M:%S")
    k = d.strftime("%Y-%m-%dT%H:%M:%SZ")
    # overpass = '[out:json][timeout:90]'
    overpass = '[out:json][timeout:90][date:"'+k+'"]'
    ox.settings.overpass_settings =overpass
    year = i.split('-')[2]
    if not os.path.exists(os.path.join(save_path,year)):
        os.makedirs(os.path.join(save_path,year))
    # pdb.set_trace()
    get_shp(bbox,tags,year,save_path,type_,area)