library(shiny)
library(dplyr)
library(tmap)
source('../utils.r')

#Create layout
pageWithSidebar(
  
  headerPanel('Survey Data Visualizer', windowTitle = 'Survey Data Visualizer'),
  
  #Create sidebar variable options
  sidebarPanel(
    selectInput(vars[1],vars[1],(data %>% select(vars[1]) %>% unique() %>% as.vector())),
    selectInput(vars[2],vars[2],append("All",(data %>% select(vars[2]) %>% unique() %>% as.vector() %>% unname())[[1]])),
    selectInput(vars[3],vars[3],append("All",(data %>% select(vars[3]) %>% unique() %>% as.vector() %>% unname())[[1]])),
    selectInput(vars[4],vars[4],append("All",(data %>% select(vars[4]) %>% unique() %>% as.vector() %>% unname())[[1]])),
    selectInput(vars[5],vars[5],append("All",(data %>% select(vars[5]) %>% unique() %>% as.vector() %>% unname())[[1]])),
    selectInput(vars[6],vars[6],append("All",(data %>% select(vars[6]) %>% unique() %>% as.vector() %>% unname())[[1]])),
    selectInput(vars[7],vars[7],append("All",(data %>% select(vars[7]) %>% unique() %>% as.vector() %>% unname())[[1]])),
    selectInput(vars[8],vars[8],append("All",(data %>% select(vars[8]) %>% unique() %>% as.vector() %>% unname())[[1]])),
    selectInput(vars[9],vars[9],append("All",(data %>% select(vars[9]) %>% unique() %>% as.vector() %>% unname())[[1]])),
    selectInput(vars[10],vars[10],append("All",(data %>% select(vars[10]) %>% unique() %>% as.vector() %>% unname())[[1]])),
    selectInput(vars[11],vars[11],append("All",(data %>% select(vars[11]) %>% unique() %>% as.vector() %>% unname())[[1]])),
    selectInput(vars[12],vars[12],append("All",(data %>% select(vars[12]) %>% unique() %>% as.vector() %>% unname())[[1]])),
    selectInput(vars[13],vars[13],append("All",(data %>% select(vars[13]) %>% unique() %>% as.vector() %>% unname())[[1]])),
    selectInput(vars[14],vars[14],append("All",(data %>% select(vars[14]) %>% unique() %>% as.vector() %>% unname())[[1]])),
    selectInput(vars[15],vars[15],append("All",(data %>% select(vars[15]) %>% unique() %>% as.vector() %>% unname())[[1]])),
    selectInput(vars[16],vars[16],append("All",(data %>% select(vars[16]) %>% unique() %>% as.vector() %>% unname())[[1]])),
    selectInput(vars[17],vars[17],append("All",(data %>% select(vars[17]) %>% unique() %>% as.vector() %>% unname())[[1]])),
    selectInput(vars[18],vars[18],append("All",(data %>% select(vars[18]) %>% unique() %>% as.vector() %>% unname())[[1]])),
    selectInput(vars[19],vars[19],append("All",(data %>% select(vars[19]) %>% unique() %>% as.vector() %>% unname())[[1]])),
    selectInput(vars[20],vars[20],append("All",(data %>% select(vars[20]) %>% unique() %>% as.vector() %>% unname())[[1]])),
    actionButton('update', 'Render Map')
  ),
  mainPanel(
    tmapOutput("map"),
    tableOutput("table")
  )
)