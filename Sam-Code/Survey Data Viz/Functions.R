library(tidyverse)
library(httr)
library(sf)
library(tmap)
library(tigris)

#Pull response function
get_survey_responses <- function(surveyid, api_key){
  
  #Craft URL
  url <- paste0("https://iad1.qualtrics.com/API/v3/surveys/", surveyid, "/export-responses")
  
  payload <- "{\n  \"format\": \"csv\",\n  \"useLabels\": true,\n  \"breakoutSets\": false\n}"
  
  encode <- 'json'
  
  req <- POST(url,
              body = payload,
              add_headers(`X-API-TOKEN` = api_key),
              content_type("application/json"), 
              encode = encode
  )
  
  #Get progress ID
  progress_id <- content(req)$result$progressId
  
  Sys.sleep(5)
  
  url <- paste0("https://iad1.qualtrics.com/API/v3/surveys/", surveyid, "/export-responses/", progress_id)
  
  req <- GET(url,
             body = payload,
             add_headers(`X-API-TOKEN` = api_key),
             content_type("application/json"), 
             encode = encode
  )
  
  #Retrieve survey file
  file_id <- content(req)$result$fileId
  
  url <- paste0("https://iad1.qualtrics.com/API/v3/surveys/", surveyid, "/export-responses/", file_id, "/file")
  
  req <- GET(url,
             body = payload,
             add_headers(`X-API-TOKEN` = api_key),
             content_type("application/octet_stream")
  )
  
  #Parse content from bin
  content <- content(req)
  tf <- tempfile()
  writeBin(content, tf)
  a <- unzip(tf)
  ex <- read_csv(a)
  return(ex)
}

#Create function to clean survey
clean_survey <- function(survey_raw){
  
  #Create crosswalk between question names and IDs
  question_raw <- as.vector(survey_raw[2,]) %>% 
    unlist(use.names = FALSE)
  question_names <- as.vector(survey_raw[1,]) %>% 
    unlist(use.names = FALSE)
  question_numbers <- names(survey_raw)
  
  question_key <- data.frame('Question.ID' = question_numbers, 'Question.Name' = question_names) %>%
    as.data.frame() %>%
    drop_na()
  
  survey_longer <- survey_raw %>%
    
    .[3:nrow(.),] %>%
    
    #Pivot by question ID
    pivot_longer(cols = starts_with('Q'), names_to = 'Question.ID') %>%
    
    #Parse question and choice IDs
    
    left_join(question_key, by = 'Question.ID') %>%
    
    #Get question number
    
    select(c('ResponseId', 'Question.ID', 'Question.Name', 'value')) %>%
    rename('Respondent.ID' = 'ResponseId', 'Question.Response' = 'value')
}

#Create function to convert the survey into geospatial information
regionalize_survey <- function(survey_longer, type_of_development = 'all'){
  
  respondent_info <- survey_longer %>%
    filter(Question.ID %in% c('Q3', 'Q4', 'Q5', 'Q7', 'Q7.1', 'Q14', 'Q15', 'Q16', 'Q17', 'Q18', 'Q19', 'Q20')) %>%
    mutate('Question.Name' = str_remove(`Question.Name`, '^Q\\d+(\\.\\d+)?\\s\\|\\s')) %>%
    pivot_wider(id_cols = 'Respondent.ID', names_from = 'Question.Name', values_from = 'Question.Response') %>%
    
    #Mutate groups represented into boolean
    mutate(`HC Resident` = if_else(str_detect(`Which group do you represent? (Select all that apply)`, 'Henry County resident'), TRUE, FALSE)) %>%
    mutate(`HC Municipal Employee` = if_else(str_detect(`Which group do you represent? (Select all that apply)`, 'Henry County municipal government'), TRUE, FALSE)) %>%
    mutate(`Public Sector Employee` = if_else(str_detect(`Which group do you represent? (Select all that apply)`, 'Public sector'), TRUE, FALSE)) %>%
    mutate(`HC Private Sector Employee` = if_else(str_detect(`Which group do you represent? (Select all that apply)`, 'employer located'), TRUE, FALSE)) %>%
    mutate(`Non-HC Private Sector Employee` = if_else(str_detect(`Which group do you represent? (Select all that apply)`, 'employer NOT located'), TRUE, FALSE)) %>%
    mutate(`HC Business Owner` = if_else(str_detect(`Which group do you represent? (Select all that apply)`, 'business owner'), TRUE, FALSE)) %>%
    mutate(`HC Unemployed` = if_else(str_detect(`Which group do you represent? (Select all that apply)`, 'not currently employed'), TRUE, FALSE)) %>%
    
    #Breakout race/ethnicity lists
    mutate(`Race / Ethnicity` = case_when(
      str_detect(`Which best describes the race or ethnicity of your household? (Select all that apply) - Selected Choice`, '(?<!\\s),(?!\\s)') ~ '2+ Races/Ethnicities',
      TRUE ~ `Which best describes the race or ethnicity of your household? (Select all that apply) - Selected Choice`
    )) %>%
    mutate(`Hispanic / Latino` = str_detect(`Which best describes the race or ethnicity of your household? (Select all that apply) - Selected Choice`, 'Hispanic')) %>%
    
    rename('Community of Residence' = `Please indicate where you live in Henry County:`,
           'Community of Employment' = `Please indicate where you work in Henry County`,
           'HC Residential Tenure' = `How long have you been living or working in Henry County?`,
           'Gender' = `What gender do you identify with?`,
           'Age' = `What is your age group?`,
           'Disability Status' = `Do you have any vision, hearing, or mobility related disability?`,
           'Education' = `With respect to your education, please select the highest education level that applies:`,
           'Income' = `To ensure our study is representative of all income groups in the area, please indicate your household's annual gross income range (before taxes are taken out).`,
           'Household Strucutre' = `What best describes your household structure? - Selected Choice`
           ) %>%
    
    select(-c(`Which group do you represent? (Select all that apply)`, `Which best describes the race or ethnicity of your household? (Select all that apply) - Selected Choice`))
  
  region_q <- survey_longer %>%
    
    filter((str_detect(`Question.ID`, '^Q9') | str_detect(`Question.ID`, '^Q13')) == TRUE) %>%
    filter(!is.na(Question.Response)) %>%
    
    #Where multiple regions are selected, create a unique row for each region
    mutate('Area Selection' = str_split(Question.Response,',')) %>%
    unnest('Area Selection') %>%
    
    #Parse the type of development from each question
    mutate('Type of Development' = str_match(Question.Name, '- (.+)$')[,2]) %>%
    
    select(-Question.Response) %>%
    
    #Add respondent information
    left_join(respondent_info, by = 'Respondent.ID')
  
  if(type_of_development != 'all'){
    region_q <- region_q %>%
      filter(`Type of Development` == type_of_development)
  }
  
  return(region_q)
}


survey_to_sf <- function(region_q, region_geom = regions){
  
  survey_region_support <- region_q %>%
    #Add geometry
    left_join(regions %>% select(c(geometry, `Region Name`)), by = c('Area Selection' = 'Region Name')) %>%
    
    st_drop_geometry() %>%
    
    #Remove non map-based questions
    filter(!str_detect(`Question.ID`, '^Q\\d+\\.')) %>%
    count(`Question.ID`, `Type of Development`, `Area Selection`, name = 'Num Responses') %>%
    
    #Add total number of responses
    left_join(region_q %>% count(Question.ID, name = 'Total Responses'), by = 'Question.ID') %>%
    
    mutate('Proportion in Favor' = `Num Responses` / `Total Responses`) %>%
    mutate('Region Number' = str_extract(`Area Selection`, '\\d+')) %>%
    
    #Add geometry
    left_join(regions %>% select(c(geometry, `Region Name`)), by = c('Area Selection' = 'Region Name')) %>%
    
    st_as_sf()
    
    return(survey_region_support)
}

build_map <- function(survey_region_support, map_title = 'Development Support by Region', region_geom = regions, city_geom = cities, hc_border_geom = hc_border, road_geom = roads){
  
  map <- tm_shape(
    survey_region_support %>%
      filter(`Area Selection` %in% c('Another Region outside Henry County', 'I do not support this type of development anywhere', 'Prefer not to answer / don\'t know') == FALSE),
    bbox = st_bbox(hc_border)
  ) +
    
    tm_polygons(col = 'Proportion in Favor') +
    
    tm_shape(regions) +
    tm_text(text = 'RegionID') +
    
    tm_shape(roads %>% filter(Layer %in% c('Interstates', 'State Highways'))) +
    tm_lines(col = '#33362c', lwd = 2) +
    
    tm_shape(cities) +
    tm_dots(size = 0.3, col = '#4b50eb') +
    
    tm_shape(hc_border) +
    tm_borders(lwd = 2) +
    
    tm_layout(main.title = map_title, main.title.size = .75, main.title.fontface = 'bold')
  
  return(map)
}




