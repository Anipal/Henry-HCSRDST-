library(shiny)
source('../utils.R')

#Get survey data
data <- main(geometry=FALSE)

#Load in geojsons for maps
region_geom <- st_read('../data/regions.geojson') %>% 
  mutate('Region Name' = paste0('Region ',`RegionID`))
city_geom <- st_read('../data/cities.geojson')
hc_border_geom <- st_read('../data/hc_border.geojson')
road_geom <- st_read('../data/roads.geojson')


#Variables from survey data, used in app
vars <- names(data)[-c(1:4)]

#Function for filtering the dataset
vfilter <- function(vars, data, input){
  
  data_ <- data
  
  #For each variable
  for(var in vars){
    
    #If the variable is not equal to 'All', perform the filter
    if(input[[var]] != 'All'){
      data_ <- data_[data_[var] == input[[var]],]
    }
  }
  
  return(data_)
}