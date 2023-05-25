library(shiny)
library(tmap)
library(dplyr)
source('../utils.r')

function(input,output,session){
  
  #Filter data as outputs are changed
  geometry <- reactive({
    vfilter(vars, data, input) %>% survey_to_sf(region_geom)
  }) %>%
    bindEvent(input$update)
  
  map <- reactive({
    build_map(geometry(), map_title = input[[vars[1]]], region_geom, city_geom, hc_border_geom, road_geom)
  })
  
  data_ <- reactive({
    vfilter(vars, data, input)
  }) %>%
    bindEvent(input$update)
  
  output$map <- renderTmap(map())
  output$table <- renderTable(data_() %>% select(-c('Respondent.ID', 'Question.ID', 'Question.Name')) %>% head())
}