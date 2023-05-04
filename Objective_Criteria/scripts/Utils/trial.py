from sklearn.cluster import KMeans
import numpy as np
import geopandas as gpd
from tqdm import tqdm
from shapely.geometry import Point, LineString
import pandas as pd
import json
import pdb




geo1 = gpd.read_file("../../../../data/Henry_County_data/change_analysis/combined_5.shp").to_crs(4326)
coords = []
for i in range(len(geo1)):
    coords.append([np.asarray(geo1['geometry'][i].coords.xy[0])[0], np.asarray(geo1['geometry'][i].coords.xy[1])[0]])
pdb.set_trace()
coordinates = np.array(coords)
kmeans = KMeans(n_clusters=50)
kmeans.fit(coordinates)
geo1['CLUSTER_ID'] = kmeans.labels_
geo1.to_file('../../../../data/Henry_County_data/Objective-Criteria/processed_files/clusters.shp')