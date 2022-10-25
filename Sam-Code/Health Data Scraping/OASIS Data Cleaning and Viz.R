library(tidyverse)
library(tmap)
library(tidycensus)
library(sf)
library(readxl)

year <- 2020
epsg_id <- 26967

#Read in health data
health_scrape_raw <- read_csv('./Data/health_data_raw.csv') %>%
  mutate(tract = as.character(tract))

respiratory_deaths <- read_xlsx('./Data/respiratory_deaths.xlsx', skip = 1) %>%
  filter(!is.na(Geography) & !is.na(`\nNumber of Deaths`)) %>%
  mutate('Respiratory Deaths' = as.numeric(`\nNumber of Deaths`), .keep = 'unused')

total_deaths <- read_xlsx('./Data/total_deaths.xlsx', skip = 1) %>%
  filter(!is.na(Geography) & !is.na(`\nNumber of Deaths`)) %>%
  mutate('Total Deaths' = as.numeric(`\nNumber of Deaths`), .keep = 'unused')

#Concatenate all data into one frame
health_data_joined <- full_join(health_scrape_raw, respiratory_deaths, by = c('tract' = 'Geography')) %>%
  full_join(total_deaths, by = c('tract' = 'Geography'))

#Get census tract population for 2021 using ACS 5-year estimates
census_api_key('cf3c51073f5e6be8f75b96e5c12662a25525326b')

acs_codebook <- load_variables(year = year, dataset = 'acs5')

#Get population data from acs5
henry_acs <- get_acs(geography = 'tract',
                     state = 'GA', 
                     county = 'Henry County', 
                     variables = c('Population' = 'B01003_001'), 
                     year = year, 
                     survey = 'acs5', 
                     output = 'wide',
                     geometry = TRUE) %>%
  
  #Drop unneeded fields
  select(-c(NAME, 'PopulationM')) %>%
  
  #Project
  st_transform(crs = epsg_id)

#Get 2010 census tracts
henry_2010_tracts <- tigris::tracts(state = 'GA', county = 'Henry', year = 2010) %>%
  
  #Drop unneeded fields
  select(NAMELSAD10, GEOID10, geometry) %>%
  
  #Project
  st_transform(crs = epsg_id)

#Plot where 2020 tracts overlap 2010 tracts
tmap_mode('view')
tm_shape(henry_2010_tracts) + 
  tm_polygons(border.col = 'red', border.alpha = 0.3) + 
  tm_shape(henry_acs) + 
  tm_polygons(lty = 'dashed', alpha = 0.3, border_col = 'black')

#Union by feature
henry_acs_union <- henry_acs %>%
  st_join(st_buffer(henry_2010_tracts, 200), join = st_within) %>%
  group_by(`GEOID10`, `NAMELSAD10`) %>%
  summarize(geometry = st_union(geometry), population = sum(PopulationE)) %>%
  st_as_sf() %>%
  st_transform(crs = epsg_id)

#Ensure the borders of merged polygons match borders of original 2010 polygons
st_within(henry_acs_union, henry_2010_tracts %>% st_buffer(200))
#If any of these values are empty, that means the join did not work for that tract

#Plot the coerced 2020 tracts on top of the 2010 tracts
tmap_mode('view')
tm_shape(henry_2010_tracts) + tm_borders(col = 'blue', lwd = 4, alpha = 0.3) +
  tm_shape(henry_acs_union) + tm_borders(col = 'red', lwd = 4, alpha = 0.3)

#Add health data to population data
henry_health_final <- henry_acs_union %>%
  left_join(health_data_joined, by = c('GEOID10' = 'tract')) %>%
  
  #Normalize variables by population
  mutate(across(-any_of(c('GEOID10', 'NAMELSAD10', 'geometry', 'population')), 
                .fns = ~ (.x/population) %>% signif(2))) %>%
  
  #Rename variables
  rename('GEOID' = 'GEOID10',
         'Tract Name' = 'NAMELSAD10',
         'Tract Population' = 'population',
         'ACSC Hospital Discharge Rate' = 'acsc_discharges',
         'ACSC ER Visit Rate' = 'acsc_er_visits',
         'ER Visit Rate (Respiratory Conditions)' = 'respiratory_er_visits',
         'Hospital Discharge Rate (Respiratory Conditions)' = 'respiratory_hosp_discharges',
         'Death Rate (Respiratory Conditions)' = 'Respiratory Deaths',
         'Death Rate' = 'Total Deaths'
         )

#Generate shapefile
st_write(henry_health_final, './Exports/henry_health.shp', append = FALSE)

#Generate plot of variables
tmap_mode('plot')

resp_er_map <- tm_shape(henry_health_final) +
  tm_polygons(col = 'ER Visit Rate (Respiratory Conditions)')

resp_hosp_map <- tm_shape(henry_health_final) +
  tm_polygons(col = 'Hospital Discharge Rate (Respiratory Conditions)')

acsc_hosp_map <- tm_shape(henry_health_final) +
  tm_polygons(col = 'ACSC Hospital Discharge Rate')

acsc_er_map <- tm_shape(henry_health_final) +
  tm_polygons(col = 'ACSC ER Visit Rate')

tmap_arrange(resp_er_map, acsc_er_map, ncol = 2, nrow = 1) %>% print(knit = TRUE)
