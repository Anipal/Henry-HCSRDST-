import requests
import time
import json
import io
import zipfile
import os
import shutil
import pandas as pd

def get_survey_responses(surveyid, api_key):

    #Request survey export from qualtrics API
    url = "https://iad1.qualtrics.com/API/v3/surveys/{}/export-responses".format(surveyid)
    payload = "{\n  \"format\": \"csv\",\n  \"useLabels\": true,\n  \"breakoutSets\": false\n}"
    headers = {
        "content-type": "application/json",
        "x-api-token": api_key,
    }
    #Post survey results request
    req = requests.post(url,
                        data = payload,
                        headers = headers)

    #Get prgress ID to pull responses
    progressid = req.json()['result']['progressId']
    progressStatus = 'inProgress'

    #Download results from export request
    while progressStatus != "complete" and progressStatus != "failed":
        url = "https://iad1.qualtrics.com/API/v3/surveys/{}/export-responses/{}".format(surveyid, progressid)
        req = requests.get(url,
                            headers = headers)
        print("Download is {}% complete".format(req.json()['result']['percentComplete']))
        progressStatus = req.json()['result']['status']
    
    #Get fileId
    fileid = req.json()['result']['fileId']

    #Download file
    url = "https://iad1.qualtrics.com/API/v3/surveys/{}/export-responses/{}/file".format(surveyid, fileid)
    req = requests.get(url,
                       headers=headers,
                       stream=True)
    
    #Generate zip file
    zipfile.ZipFile(io.BytesIO(req.content)).extractall("tf")
    #Read zip file contents
    contents = pd.read_csv('\\'.join(['tf', os.listdir('tf')[0]]))
    #Delete tempfile
    shutil.rmtree('tf')

    return contents

survey_raw = get_survey_responses('SV_4UULU29RAidh96m', 'hRLGDdJ4Ko0UqruJbW5xhsQYWBamJtpc0h4Vlj8E')


