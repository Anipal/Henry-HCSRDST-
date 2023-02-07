import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os
import pdb
df = gpd.read_file('/mnt/c/Users/apal72/Documents/Anisha/data/Henry_County_data/change_analysis/cluster_density_50_xtra.shp')
df_area = pd.DataFrame(columns = df.columns)

df_area["Area"] = ""
df_area["growth"] = ""
indus_mean = df['Industrial'].mean()
comm_mean = df['Commercial'].mean()
res_mean = df['Residentia'].mean()
pub_mean= df['Public'].mean()
pdb.set_trace()
k = 0
for i in range(len(df)):
    if df['Residentia'].iloc[i] <res_mean and df['Public'].iloc[i]<pub_mean :
        if df['Industrial'].iloc[i] >indus_mean:
            df_area.loc[k] = [df.Cluster.iloc[i], df.Lon.iloc[i], df.Lat.iloc[i], df.Residentia.iloc[i],df.Conservati.iloc[i],df.Industrial.iloc[i],df.Commercial.iloc[i],df.Public.iloc[i],df.Rec.iloc[i],df.Gov.iloc[i],df.State.iloc[i],df.Others.iloc[i],df.Total.iloc[i], df.Change.iloc[i],df.geometry.iloc[i],'Industrial','Y']
            k = k+1
        else:
            df_area.loc[k] = [df.Cluster.iloc[i], df.Lon.iloc[i], df.Lat.iloc[i], df.Residentia.iloc[i],df.Conservati.iloc[i],df.Industrial.iloc[i],df.Commercial.iloc[i],df.Public.iloc[i],df.Rec.iloc[i],df.Gov.iloc[i],df.State.iloc[i],df.Others.iloc[i],df.Total.iloc[i], df.Change.iloc[i],df.geometry.iloc[i],'Industrial','N']
            k = k+1
        if df['Commercial'].iloc[i] >comm_mean:
            df_area.loc[k] = [df.Cluster.iloc[i], df.Lon.iloc[i], df.Lat.iloc[i], df.Residentia.iloc[i],df.Conservati.iloc[i],df.Industrial.iloc[i],df.Commercial.iloc[i],df.Public.iloc[i],df.Rec.iloc[i],df.Gov.iloc[i],df.State.iloc[i],df.Others.iloc[i],df.Total.iloc[i], df.Change.iloc[i],df.geometry.iloc[i],'Commercial','Y']
            k = k+1
        else:
            df_area.loc[k] = [df.Cluster.iloc[i], df.Lon.iloc[i], df.Lat.iloc[i], df.Residentia.iloc[i],df.Conservati.iloc[i],df.Industrial.iloc[i],df.Commercial.iloc[i],df.Public.iloc[i],df.Rec.iloc[i],df.Gov.iloc[i],df.State.iloc[i],df.Others.iloc[i],df.Total.iloc[i], df.Change.iloc[i],df.geometry.iloc[i],'Commercial','N']
            k = k+1
    elif df['Residentia'].iloc[i] >res_mean and df['Public'].iloc[i]<pub_mean:
        df_area.loc[k] = [df.Cluster.iloc[i], df.Lon.iloc[i], df.Lat.iloc[i], df.Residentia.iloc[i],df.Conservati.iloc[i],df.Industrial.iloc[i],df.Commercial.iloc[i],df.Public.iloc[i],df.Rec.iloc[i],df.Gov.iloc[i],df.State.iloc[i],df.Others.iloc[i],df.Total.iloc[i], df.Change.iloc[i],df.geometry.iloc[i],'Public','N']
        k = k+1
        df_area.loc[k] = [df.Cluster.iloc[i], df.Lon.iloc[i], df.Lat.iloc[i], df.Residentia.iloc[i],df.Conservati.iloc[i],df.Industrial.iloc[i],df.Commercial.iloc[i],df.Public.iloc[i],df.Rec.iloc[i],df.Gov.iloc[i],df.State.iloc[i],df.Others.iloc[i],df.Total.iloc[i], df.Change.iloc[i],df.geometry.iloc[i],'Residential','Y']
        k = k+1
    else:
        df_area.loc[k] = [df.Cluster.iloc[i], df.Lon.iloc[i], df.Lat.iloc[i], df.Residentia.iloc[i],df.Conservati.iloc[i],df.Industrial.iloc[i],df.Commercial.iloc[i],df.Public.iloc[i],df.Rec.iloc[i],df.Gov.iloc[i],df.State.iloc[i],df.Others.iloc[i],df.Total.iloc[i], df.Change.iloc[i],df.geometry.iloc[i],'NO DEV','N']
        k = k+1
pdb.set_trace()
geometry = [Point(xy) for xy in zip(df_area.Lon, df_area.Lat)]
gdf = gpd.GeoDataFrame(df_area, crs="EPSG:4326", geometry=geometry)
gdf.to_file((os.path.join('/mnt/c/Users/apal72/Documents/Anisha/data/Henry_County_data/change_analysis','areas.shp')))
 

