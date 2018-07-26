# -*- coding: utf-8 -*-
"""
@author: Adam Dixon

This script will generate a csv file that contains each time in PDT of when a 
particular student has left the canvas quiz page. This script is made for 
quizzes with only one attempt allowed (online exams).
"""

#List of libraries needed, will automatically install if not present
try:
    import requests
except:
    import pip
    pip.main(['install', 'requests'])
    import requests

try:
    import pandas as pd
except:
    import pip
    pip.main(['install', 'pandas'])
    import pandas as pd

try:
    import json
except:
    import pip
    pip.main(['install', 'json'])
    import json
import dateutil.parser
import paginate

#========================================================================================================
# Given a course ID, return a list of user id's for all students in the course
#========================================================================================================
def get_students():
    r = requests.get(url + '/api/v1/courses/' + str(course_id) + "/students?per_page=1000",
                                headers =  {'Authorization': 'Bearer ' + token})
    students = []
    info = json.loads(r.text)
    
    for student in info:
        students.append(student['id'])
    return students
    
#========================================================================================================
# Given a list of json objects, return a dictionary... user_id : submission_id
#========================================================================================================
def get_dictionary(json_list):
    dictionary = {}
    for idx, val in enumerate(json_list):
        dictionary.setdefault(json_list[idx]['user_id'], json_list[idx]['id'])
    return dictionary
    
#========================================================================================================
# Given a user_id, access token and url link to a Canvas page, return a string (User name : user_id)
#========================================================================================================
def get_name(user_id):
    r = requests.get(url + '/api/v1/users/' + str(user_id) + "/profile?per_page=1000",
                                headers =  {'Authorization': 'Bearer ' + token})
    j = json.loads(r.text)
    return j['name'] + " : " + str(user_id)

#========================================================================================================
# Given a list of json objects and a dictionary (user_id : list of times), return a list of monitoring 
# log URLs for each user that has left the page at least 1 time
#========================================================================================================
def get_log_url_list(json_list, user_time_dictionary):
    l = []
    for user_id, time in user_time_dictionary.items():
        for idx, val in enumerate(json_list):
            if str(json_list[idx]['user_id']) == str(user_id):
                l.append(url + "courses/" + course_id + "/quizzes/" + quiz_id + "/submissions/" + str(json_list[idx]['user_id']) + "/log")
    return l

#========================================================================================================
# Generate a csv file with columns: user_id, name, time and url of log given all relevant information
#========================================================================================================
def generate_csv_file(json_list, user_time_dictionary):
    newd = {}  
    for user_id, time in user_time_dictionary.items():
        newd.setdefault(get_name(user_id, token, url), time)
    df = pd.DataFrame.from_dict(newd, orient='index')
    se = pd.Series(get_log_url_list(json_list, user_time_dictionary))
    df['url'] = se.values
    df.to_csv('event_log.csv')
    return None

#========================================================================================================
# Function to return a dictionary {user_id : time_stamps} where time_stamps
# is a list of times that the the student left the canvas quiz page
#========================================================================================================
def get_user_time_dictionary(json_list):
    d = {}        
    dictionary = get_dictionary(json_list)
    
    # for every submission
    for student_id, sub_id in dictionary.items(): 
        events_table = paginate.get_single_submission_paginated(url, course_id, quiz_id, token, str(sub_id))
        # search through log and associate a page left with a time
        time_stamps = []
        for index, row in events_table.iterrows():
            if str(row['quiz_submission_events']['event_type']) == "page_blurred":
                
                try:
                    # if there is a "page_focused" event directly after the "page_blurred", do not add it to the log
                    if (not events_table.iloc[index]['quiz_submission_events']['created_at'] == events_table.iloc[index + 1]['quiz_submission_events']['created_at']):
                        time_stamps.append(convert_time(parse(str(dateutil.parser.parse(str(row['quiz_submission_events']['created_at']))))))
                        d.setdefault(student_id, time_stamps)
                except:
                    time_stamps.append(convert_time(parse(str(dateutil.parser.parse(str(row['quiz_submission_events']['created_at']))))))
                    d.setdefault(student_id, time_stamps)
    return d
    


#========================================================================================================
# Helper function to parse time into a useful format
#========================================================================================================
def parse(s):
    start = s.index( ' ' ) + len( ' ' )
    end = s.index( '+', start )
    return s[start:end]

#========================================================================================================
# Function to convert the Canvas timezone into the UBC time zone
#========================================================================================================
def convert_time(s):
    s = " " + s
    start = s.index( ' ' ) + len( ' ' )
    end = s.index( ':', start )
    i = int(s[start:end])
    if (i <= 6 and i >= 0):
        switch = {
                0: "17",
                1: "18",
                2: "19",
                3: "20",
                4: "21",
                5: "22",
                6: "23"
                }
        i = switch[i]
    else:
        i = i - 7   
    return s.replace(" " + s[start:end], str(i))

#========================================================================================================
# Begin main script
#========================================================================================================

with open('Canvas API Token.txt','r') as f:
    for line in f:
        for word in line.split():
           token = word 

course_id = input("Type the course id and press ENTER\n")
quiz_id = input("Type the quiz id and press ENTER\n")

# ex: https://canvas.ubc.ca/
url = input("Copy and paste the url when you are on the canvas dashboard page and press ENTER\n")

# get a list of each students submission_id, user_id, etc.
student_info_list = paginate.get_submission_event_paginated_list(url, course_id, quiz_id, token)

generate_csv_file(student_info_list, get_user_time_dictionary(student_info_list))

print("Process successful. Check the file 'event_log.csv' for results.")