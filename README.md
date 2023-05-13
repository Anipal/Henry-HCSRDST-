# Henry-HCSRDST-
Official repo for HCSRDST

# Calculating the Objective_Criteria scores

1. Setup the environment by running  ```pip3 install -r Objective_Criteria/requirements.txt``` 
2. Create a shapefiles inside folder in the ```Objective_Criteria``` folder and add all the necessary shapefiles to it
3. If run.sh is to be run directly without modifying the name of the files passed in the arguments, then the following naming convention should be followed :
    | Shapefile content | Shapefile name |
    |  ----------- | ----------- |
    | buildings | Structures.shp |
    | zoning | zoning.shp |
    | landuse | flu.shp |
    | parcels | Parcels.shp |
    | road | road.shp |
    | zoning data for previous year | parcel_before.shp |
    | zoning data for current year | parcel_after.shp |
    | hospital locations | Hospitals.shp |
    | zoning data for previous year | parcel_before |
    | location of environmentally sensitive areas | Parks.shp|
    |location of  Schools| Schools |
3. Run the file using the following command : ```./run.sh```. It will take approximately 3 hours for the entire file to run.
4. The resulting scored file will be generated in the given path ```Objective_Criteria\shapefiles\criteria\criteria.shp```
5. To visualize in any GIS tool use CRS: ```EPSG 26967```

