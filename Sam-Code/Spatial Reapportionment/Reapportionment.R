library(sf)
library(tidyverse)
library(tmap)
library(here)
#The aim of this script is to produce a function that
#when given one set of large of spatial data with attributes, will reapportion those attributes
#to a smaller set of geometry within the larger geometry.
reapportion_sf <- function(large, small, how = 'large_to_small', buffer_dist = units::set_units(5, 'meters')){
  
  if (how == 'large_to_small'){
    #Retain original geometries
    reference <- small %>%
      mutate(index = 1:nrow(.)) %>%
      select(c(index, geometry))
    
    #Get the intersection of every tract
    frame <- reference %>%
      
      st_intersection(large %>% st_buffer(dist = buffer_dist)) %>%
      
      #Calculate area of each intersection
      mutate(area = st_area(.)) %>%
      
      #Group by smaller unit
      group_by(index) %>%
      #Extract the row with the intersection largest area
      filter(area == max(area)) %>%
      ungroup() %>%
      
      #Drop geometry
      st_drop_geometry() %>%
      
      #Re-append original small unit geometries
      right_join(reference, by = 'index') %>%
      st_as_sf(crs = st_crs(reference)) %>%
      st_make_valid()
  }
  
  if(how == 'small_to_large'){
    #Retain original geometries
    reference <- large %>%
      mutate(index = 1:nrow(.)) %>%
      select(c(index, geometry)) %>% 
      st_buffer(dist = buffer_dist)
    
    #Get the intersection of every tract
    frame <- reference %>%
      
      st_intersection(small) %>%
      
      #Calculate area of each intersection
      mutate(area = st_area(.)) %>%
      
      #Group by smaller unit
      group_by(index) %>%
      #Extract the row with the intersection largest area
      filter(area == max(area)) %>%
      ungroup() %>%
      
      #Drop geometry
      st_drop_geometry() %>%
      
      #Re-append original small unit geometries
      right_join(reference, by = 'index') %>%
      st_as_sf(crs = st_crs(reference)) %>%
      st_make_valid()
  }

return(frame)
}
