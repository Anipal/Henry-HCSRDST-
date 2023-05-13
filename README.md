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

# Important Information pertaining to attribute columns in the shapefiles
1. For zoning shapefile if any zoning apart from the following is added to the new database then the code will have to be modified to function:
    * RA, R1, R2, R3, R4, R5, RS, RD, RM, RMH
    * DTRC, DTMU
    * MR1, MR2
    * O1, OI, CITY
    * DTMU, MU
    * C1, C2, C3
    * IAC
    * M1, M2, PD
2. For landuse(flu) shapefile if any zoning apart from the following is added to the new database then the code will have to be modified to function:
    * RR, PRC
    * HD, LD, MD
    * OI, CITY
    * MX
    * COMM, COM
    * INDUS, PI, TCU

