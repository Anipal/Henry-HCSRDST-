import geopandas as gpd
import pandas as pd
import numpy as np 
from shapely.geometry import Point
import os
import pdb

df2_str = gpd.read_file('/mnt/c/Users/apal72/Documents/Anisha/data/Henry_County_data/change_analysis/kmeans_50.shp')

df_Y = df2_str[df2_str['change'] =='N']
df =df2_str[df2_str['change'] =='Y']
labels_change = df['CLUSTER_ID'].unique()
df_cluster_significance = pd.DataFrame(columns = ["Cluster", "Lon", "Lat", "Residential","Conservation","Industrial","Commercial","Public","Rec","Gov","State","Others","Total", "Change"])
# pdb.set_trace()
for i,j in enumerate(df2_str['CLUSTER_ID'].unique()):
    df3 = df_Y[df_Y['CLUSTER_ID'] == j]
    lon = (df3['Lon'].mean())
    lat = (df3['Lat'].mean())
    res = len(np.where(df3["PROP_USE_D"].str.contains("RES"))[0])+ len(np.where(df3["PROP_USE_D"].str.contains("HOME"))[0]) + len(np.where(df3["PROP_USE_D"].str.contains("APARTMENT"))[0])+len(np.where(df3["PROP_USE_D"].str.contains("FAMILY"))[0]) + len(np.where(df3["PROP_USE_D"].str.contains("CONDO"))[0])
    consv = len(np.where(df3["PROP_USE_D"].str.contains("CONSV"))[0]) + len(np.where(df3["PROP_USE_D"].str.contains("FOREST"))[0])
    indus = len(np.where(df3["PROP_USE_D"].str.contains("INDUSTRIAL"))[0])
    comm = len(np.where(df3["PROP_USE_D"].str.contains("COMMERCIAL"))[0]) 
    school = len(np.where(df3["PROP_USE_D"].str.contains("EDU"))[0]) + len(np.where(df3["PROP_USE_D"].str.contains("HOSPITAL"))[0])
    rec = len(np.where(df3["PROP_USE_D"].str.contains("REC"))[0])
    gov = len(np.where(df3["PROP_USE_D"].str.contains("CITY"))[0])+len(np.where(df3["PROP_USE_D"].str.contains("COUNTY"))[0])
    state = len(np.where(df3["PROP_USE_D"].str.contains("STATE"))[0])
    others = len(df3) - (res+consv+indus+comm+rec+gov+state+public)
    if(j in labels_change):
        df_cluster_significance.loc[i] = [j,lon,lat,res/len(df3),consv/len(df3),indus/len(df3),comm/len(df3),public/len(df3),rec/len(df3),gov/len(df3),state/len(df3),others/len(df3),len(df3),"Y"]
    else:
        df_cluster_significance.loc[i] = [j,lon,lat,res/len(df3),consv/len(df3),indus/len(df3),comm/len(df3),public/len(df3),rec/len(df3),gov/len(df3),state/len(df3),others/len(df3),len(df3),"N"]
# 
geometry = [Point(xy) for xy in zip(df_cluster_significance.Lon, df_cluster_significance.Lat)]
gdf = gpd.GeoDataFrame(df_cluster_significance, crs="EPSG:4326", geometry=geometry)
gdf.to_file((os.path.join('/mnt/c/Users/apal72/Documents/Anisha/data/Henry_County_data/change_analysis','cluster_density_50_xtra.shp')))

df_cluster_significance_2 = pd.DataFrame(columns = df_Y.columns)
# pdb.set_trace()
for i in labels_change:
    df4 = df_Y[df_Y['CLUSTER_ID'] == i]
    df_cluster_significance_2 = pd.concat([df_cluster_significance_2,df4], ignore_index=True)
# df_cluster_significance_2 = pd.DataFrame(columns = ["Cluster", "Lon", "Lat", "Residential","Conservation","Industrial","Public","Total"])

geometry = [Point(xy) for xy in zip(df_cluster_significance_2.Lon, df_cluster_significance_2.Lat)]
gdf = gpd.GeoDataFrame(df_cluster_significance_2, crs="EPSG:4326", geometry=geometry)
gdf.to_file((os.path.join('/mnt/c/Users/apal72/Documents/Anisha/data/Henry_County_data/change_analysis','cluster_density_categories_50_xtra.shp')))
