from sklearn.cluster import KMeans
import numpy as np
import geopandas as gpd
from tqdm import tqdm
from shapely.geometry import Point, LineString
import pandas as pd
import json


def add_coords(df1):
    collection = json.loads(df1.to_json(orient='records'))
    test_gj = gpd.GeoDataFrame.from_features(collection)
    df1['Lon'] = test_gj['geometry'].x
    df1['Lat'] = test_gj['geometry'].y
    return df1

def add_fields(df1,change):
    if(change):
        df1['change'] =['Y']*len(df1)
    else:
       df1['change'] =['N']*len(df1) 
    return df1 

def change_calc(poly_list_1,poly_list_2,class_1,class_2,args):
    flag1 = np.zeros((len(poly_list_1)), dtype = 'uint8')
    class_3 = ['no']*len(flag1)
    for i in tqdm(range(len(poly_list_1))):
        for j in tqdm(range(len(poly_list_2))):
            item_poly = poly_list_2[j]
            if (item_poly).intersects(poly_list_1[i]):
                    inter = (item_poly).intersection(poly_list_1[i])
                    union = (item_poly).union(poly_list_1[i])
                    iou = float(inter.area / union.area)                   
                    if iou > 0.5 :
                        # pdb.set_trace()
                        if not(class_1[i]==class_2[j]):
                            flag1[i] = 1
                            class_3[i] = class_2[j] + '_to_' + class_1[i]     

def flag_compare(flag,poly_list,class_3):
    unq = []
    class_4 = []
    for i in tqdm(range(len(poly_list))):
        if flag[i] == 1:
                unq.append(poly_list[i])
                class_4.append(class_3[i])
    return unq,class_4

def parcel_change(geo_before, geo_after):
    poly_before = geo_before['geometry'].tolist()
    poly_after = geo_after['geometry'].tolist()
    class_before = geo_before['landuse'].tolist()
    class_after = geo_after['landuse'].tolist()
    flag_after_nochange, class_3 = change_calc(poly_after, poly_before,class_after,class_before)
    change_after,class_4 = flag_compare(flag_after_nochange,poly_after,class_3)
    geojson_df = gpd.GeoDataFrame(({'geometry':change_after,'change_type':class_4}), crs={'init': 'epsg:4326'})
    return geojson_df

def centroids(poly):
    points = poly.copy()
    points.geometry = points['geometry'].centroid
    points.crs =poly.crs
    return points

def combine(change, structures):
    df1_str =  pd.DataFrame(centroids(gpd.read_file(structures).to_crs(4326)))
    df1_change = pd.DataFrame(centroids(change))
    df1_change_new_field = add_fields(df1_change, 1)
    df1_str_new_field = add_fields(df1_str, 0)

    df1_change_coords = add_coords(df1_change_new_field)
    df1_str_coords = add_coords(df1_str_new_field)
    df_combined = pd.concat([df1_change_coords, df1_str_coords], ignore_index=True)
    A = df_combined["properties"].apply(pd.Series)
    geometry = [Point(xy) for xy in zip(df_combined.Lon, df_combined.Lat)]
    df = df_combined.drop(['properties'], axis=1)
    df = pd.concat([df, A], axis=1)
    gdf = gpd.GeoDataFrame(df, crs="EPSG:4326", geometry=geometry)
    return gdf

def clustering(geo_before,geo_after,structures):

    geo_change = parcel_change(gpd.read_file(geo_before).to_crs(4326), gpd.read_file(geo_after).to_crs(4326))
    geo1 = combine(geo_change, structures)
    coords = []
    for i in range(len(geo1)):
        coords.append([np.asarray(geo1['geometry'][i].coords.xy[0])[0], np.asarray(geo1['geometry'][i].coords.xy[1])[0]])
    coordinates = np.array(coords)
    kmeans = KMeans(n_clusters=50)
    kmeans.fit(coordinates)
    geo1['CLUSTER_ID'] = kmeans.labels_
    return geo1 

def cluster_density(df2_str):
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
        public = len(np.where(df3["PROP_USE_D"].str.contains("EDU"))[0]) + len(np.where(df3["PROP_USE_D"].str.contains("HOSPITAL"))[0])
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
    return gdf

def area_calc(geo_before,geo_after,structures, save_path):
    cluster = clustering(geo_before,geo_after,structures)
    df = cluster_density(cluster)
    df_area = pd.DataFrame(columns = df.columns)
    df_area["Area"] = ""
    df_area["growth"] = ""
    indus_mean = df['Industrial'].mean()
    comm_mean = df['Commercial'].mean()
    res_mean = df['Residentia'].mean()
    pub_mean= df['Public'].mean()
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
    geometry = [Point(xy) for xy in zip(df_area.Lon, df_area.Lat)]
    gdf = gpd.GeoDataFrame(df_area, crs="EPSG:4326", geometry=geometry)
    gdf.to_file(save_path)
    return
