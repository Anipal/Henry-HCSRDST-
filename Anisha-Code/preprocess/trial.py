import osmnx as ox
import geopandas as gpd
import os
from datetime import datetime
from tqdm import tqdm
def get_shp(bb,tags,date,save_path):
    gdf = ox.geometries_from_bbox(bb[0],bb[1],bb[2],bb[3],tags)
    # gdf = ox.geometries_from_place("Henry County, Georgia, USA", tags)

    gf1 = gdf[gdf.geometry.geom_type == 'Polygon']
    gf2 = gdf[gdf.geometry.geom_type == 'Point' ]

    gdf_save_1 = gf1.applymap(lambda x: str(x) if isinstance(x, list) else x)
    gdf_save_1.to_file(os.path.join(save_path,date,(date+'_poly.shp')))

    gdf_save_2 = gf2.applymap(lambda x: str(x) if isinstance(x, list) else x)
    gdf_save_2.to_file(os.path.join(save_path,date,(date+'_points.shp')))

save_path = '/mnt/c/Users/apal72/Documents/Anisha/data/sample_data/OSM'
tags = {"building": True}
date = ["10-Sep-2022-15:59:02","10-Sep-2021-15:59:02","10-Sep-2020-15:59:02","10-Sep-2019-15:59:02","10-Sep-2018-15:59:02","10-Sep-2017-15:59:02","10-Sep-2016-15:59:02","10-Sep-2015-15:59:02","10-Sep-2014-15:59:02","10-Sep-2013-15:59:02","10-Sep-2012-15:59:02","10-Sep-2011-15:59:02"]
bbox = [33.4627578429999986,33.4112425320000028, -84.1123744390000070,-84.2104397300000045]
for i in tqdm(date, total = len(data)):
    d = datetime.strptime(i, "%d-%b-%Y-%H:%M:%S")
    k = d.strftime("%Y-%m-%dT%H:%M:%SZ")
    overpass = '[out:json][timeout:90][date:"'+k+'"]'
    ox.settings.overpass_settings =overpass
    year = i.split('-')[2]
    if not os.path.exists(os.path.join(save_path,year)):
        os.makedirs(os.path.join(save_path,year))
    get_shp(bbox,tags,year,save_path)