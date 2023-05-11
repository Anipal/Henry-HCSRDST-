import arcpy
import os
import glob
import re

def parseargs():
    #Get input feature
    input_feature = arcpy.GetParameterAsText(0)

    #Get weight and score parameters
    input_params_raw = arcpy.GetParameterAsText(1)

    #Get output field name
    output_field_name = arcpy.GetParameterAsText(2)

    #Parse input parameters
    input_params_list = input_params_raw.split(';')

    #Init score fields
    score_vars = []
    #Init weights
    weights = []

    #For each input parameter, extract the input features, score var, and weights
    pattern = r"(.+)\s(.+)"
    print(input_params_raw)
    print(input_params_list)
    for a in input_params_list:

        #Search input for groups
        groups = re.search(pattern,a).groups()

        score_vars.append(groups[0])

        weights.append(float(groups[1]))

    return input_feature, score_vars, weights, output_field_name

#Utility function to get weighted sum of input variables
#this needs to be stored as a string tragically because arcpy can't interpret functions from the namespace
cb = '''def weighted_sum(scores, weights):
    sum = 0
    for s, w in zip(scores, weights):
        sum += w*float(s)

    return round(sum,2)'''


def calculate_suitability(input_feature, score_vars, weights, field_name):

    #Format score var list for arcpy calculate_field input
    formatted_score_vars = ['!' + a + '!' for a in score_vars]

    #Perform the weighted sum calculation
    arcpy.management.CalculateField(input_feature, 
                                    field = field_name, 
                                    expression = "weighted_sum({}, {})".format(formatted_score_vars, weights),
                                    field_type = "FLOAT", 
                                    expression_type = 'PYTHON3',
                                    code_block = cb)
    

if __name__ == "__main__":
    calculate_suitability(*parseargs())

