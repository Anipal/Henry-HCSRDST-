#!/bin/bash
python3 main.py \
--save_dir ../shapefiles/ \
--road ../shapefiles/road/road.shp \
--parcel ../shapefiles/Parcels/Parcels.shp \
--flu ../shapefiles/flu/flu.shp \
--zoning ../shapefiles/zoning/zoning.shp \
--buildings ../shapefiles/structures/Structures.shp \
--res_centroids ../shapefiles/areas/areas.shp \
--schools ../shapefiles/Schools/Schools.shp \
--hospitals ../shapefiles/Hospitals/Hospitals.shp \
--parks ../shapefiles/Parks/Parks.shp \
--svi ../shapefiles/SVI/SVI.shp \
--parcel_before ../shapefiles/parcel_before/parcel_before.shp \
--parcel_after ../shapefiles/parcel_after/parcel_after.shp