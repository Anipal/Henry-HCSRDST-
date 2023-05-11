#!/bin/bash
python3 main.py \
--save_dir ../../../../data/shapefiles/ \
--road ../../../../data/shapefiles/road/road.shp \
--parcel ../../../../data/shapefiles/Parcels/Parcels.shp \
--flu ../../../../data/shapefiles/flu/flu.shp \
--zoning ../../../../data/shapefiles/zoning/zoning.shp \
--buildings ../../../../data/shapefiles/structures/Structures.shp \
--res_centroids ../../../../data/shapefiles/areas/areas.shp \
--schools ../../../../data/shapefiles/Schools/Schools.shp \
--hospitals ../../../../data/shapefiles/Hospitals/Hospitals.shp \
--parks ../../../../data/shapefiles/Parks/Parks.shp \
--svi ../../../../data/shapefiles/SVI/SVI.shp \
--parcel_before ../../../../data/shapefiles/parcel_before/parcel_before.shp \
--parcel_after ../../../../data/shapefiles/parcel_after/parcel_after.shp