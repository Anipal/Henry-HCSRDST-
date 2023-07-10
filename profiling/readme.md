# Profiles of processes

- `p1_memory_profile.png` => the profile for process_1 i.e. generating the criteria.shp. It peaks at about `1.2 GB`
- `p2_memory_profile.png` => the profile for process_2 i.e. converting the .shp files to .geojson files. It peaks at about `0.8 GB`
- `web-app-trace.json` => trace file for the online web-app. You can view this by opening up the develop console (`Ctrl`+`Shift`+`I` on windows). navigating to the `Performance` tab and uploading this json file. It peaks at about `2 GB`

The repositories and the shapefiles combined take up `7 GB` memory.

With these profiles in mind, the minimal suggestion is a 8 GB RAM system with 16 GB memory.