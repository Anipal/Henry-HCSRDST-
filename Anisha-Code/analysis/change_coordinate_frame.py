import geopandas as gpd
from centroid_coords import *
import os
# def add_coords(df1):
#     df = gpd.DataFrame(columns = ['lat','lon','change'])
#     # df_1 = pd.DataFrame(columns = ['lat','lon','change'])
#     test_gj = test_gj.to_crs({'init': 'epsg:4326'}) 
#     df['Lon'] = test_gj['geometry'].x
#     df['Lat'] = test_gj['geometry'].y
#     return df
df2_str = gpd.read_file('/mnt/c/Users/apal72/Documents/Anisha/data/Henry_County_data/change_analysis/all_structures/centroids.shp')
df2_str.to_crs(epsg=4326, inplace=True)
df2_str.to_file((os.path.join('/mnt/c/Users/apal72/Documents/Anisha/data/Henry_County_data/change_analysis/','centroids_new_crs_str.shp')))