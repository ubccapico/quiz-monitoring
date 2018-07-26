# -*- coding: utf-8 -*-
"""
@author: Adam Dixon

Helper python module used to paginate two quiz GET requests.
"""
import requests
import json
import pandas as pd

#==================================================================================================================
# Function to paginate the submission events of a quiz. 
# This function will return a list of json submission object, representing each student.
# This function will only work if there is only 1 quiz submission (multiple attempts not allowed)
#==================================================================================================================
def get_submission_event_paginated_list(url, c, q, token):
    
    r = requests.get(url + "api/v1/courses/" + str(c) + "/quizzes/" + str(q) + "/submissions?per_page=100", headers =  {'Authorization': 'Bearer ' + token})
    table = pd.read_json(r.text)
    df = pd.DataFrame(table)
    
    #grabs and concats pages    
    while r.links['current']['url'] != r.links['last']['url']:
        r = requests.get(r.links['next']['url'], 
                         headers =  {'Authorization': 'Bearer ' + token})
        sub_table = pd.read_json(r.text)
            
        df2 = pd.DataFrame(sub_table)
        df = df.append(df2)
        df.reset_index()
        
    df.reset_index()
        
    l = []
    for idx, row in df.iterrows():
        l.append(row['quiz_submissions'])
    return to_json(l)

#==================================================================================================================
# Given a list of raw data from an http request, turn it into a list of json data
#==================================================================================================================
def to_json(l):
    ret_list = []
    for idx, val in enumerate(l):
        ret_list.append(json.loads(json.dumps(l[idx])))
    return ret_list

#==================================================================================================================
# Return a paginated pandas dataframe representing a students submission events (page_viewed, page_blurred, etc.)
#==================================================================================================================
def get_single_submission_paginated(url, c, q, token, submission_id):
    
    r = requests.get(url + "api/v1/courses/" + str(c) + "/quizzes/" + str(q) + "/submissions/" + str(submission_id) + "/events?per_page=100", headers = {'Authorization': 'Bearer ' + token})
   
    table = pd.read_json(r.text)
    df = pd.DataFrame(table)

    while r.links['current']['url'] != r.links['last']['url']:
        r = requests.get(r.links['next']['url'], 
                         headers = {'Authorization': 'Bearer ' + token})
        sub_table = pd.read_json(r.text)
        df2 = pd.DataFrame(sub_table)
        df = df.append(df2)

        
    return df
    
