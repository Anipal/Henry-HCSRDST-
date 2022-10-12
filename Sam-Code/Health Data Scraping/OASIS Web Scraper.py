# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 08:49:30 2022

@author: smartinez63
"""

import re
import os
import pandas as pd
import csv
import glob

#Establish path to data folder
path = os.getcwd() + '\Data'

#Get list of HTMLs
htmls = glob.glob(path + '\*.html')

#Read in htmls
raw_text = {re.search(r'([^\\]+)\.html$',a).groups()[0]: open(a, 'r').read() for a in htmls}

#Scrape each element of raw text to get the geography, map level
#Establish pattern
level_p = re.compile(r"""
                     \"Geography\"\s:\s\"
                     (?P<geoid>\d+)
                     \",\"DataClass\"\s:\s\"
                     (?P<map_level>\d+)
                     """, re.X)

#Match pattern to text
levels = {b[0]: {a.groups()[0]: int(a.groups()[1]) for a in level_p.finditer(b[1])} for b in raw_text.items()}

#Establish pattern for map level keys
key_list_p = re.compile(r'\[([\d\.,]+)\]')

#Get key values for each map
#Create an empty dictionary
keys = {}

#For every html
for (k,v) in raw_text.items():
    
    #Scrape the key list
    key_list = key_list_p.search(v).group(1).split(',')
    
    #Zip lists to get the value
    #This value is calculated by adding up the lower bound of the key range and the upper bound of the key range
    #then dividing by 2. This will allow us to assign a single value to each tract
    values = [(float(a) + float(b))/2 for (a,b) in zip(key_list[::2], key_list[1::2])]
    
    #Create a dict to assign each value to a map level
    #This will allow us to join the output dictionary with the original levels dictionary
    values_dict = {a:b for a,b in zip(range(1,len(values) + 1), values)}
    
    #Append the above dictionary to the final dictionary
    keys[k] = values_dict


#Join all html data together into one dictionary
final_dict = {'tract':list(), 'value':list(), 'type':list()}

#For every type, dict pair in levels 
for (k,v) in levels.items():
    
    final_dict['tract'] += [t for t in v.keys()]
    
    #Iterate through every tract
    for (t,l) in v.items():
        
        #Get the real value of the type
        final_dict['value'] += [keys[k][l]]
        
        #Record the type
        final_dict['type'] += [k]
        
#Build a dataframe of the scraped html data
health_incidence_raw = pd.DataFrame(final_dict)

#Export the dataframe
health_incidence_raw.to_csv(os.getcwd() + '\Scraper Exports\health_data_raw.csv')


