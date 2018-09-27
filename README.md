![Image of Sauder](http://www.hec.ca/en/executive-education/news/2018/logo-UBC-Sauder.jpg)

# Quiz Monitoring
Script to generate a csv file containing each time in PDT of when a student has left the Canvas quiz page (alt tabbed, changed browser tabs, etc.). It will also provide a link to the monitoring page of each student who has left the quiz page. This script is made specifically for quizzes that allow one attempt. It requires the course ID, quiz ID (IDs can be found in the quiz URL) and URL of the Canvas dashboard page.

## Instructions:
1. If you do not have Python, install it. If you have no experience with it, I recommend installing it through *https://www.anaconda.com/download/*.

2. Clone this GitHub repository.

3. Install all the dependencies using pip (first time use only). Use the command **pip install -r requirements.txt** through the command shell in the directory of your cloned GitHub repo.

4. Run the script. It will prompt you for your these things:
   1. Token (Canvas API token)
   2. Course ID
   3. Quiz ID

**Please note this script can be rather slow. Due to the risk of taking down the AWS server, all API calls are done on a single thread.**
