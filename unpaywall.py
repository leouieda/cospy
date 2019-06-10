import sys
import json
import requests
from datetime import date
sys.path.insert(0, './API')

import datetime

headers = {'Content-Type': 'application/json'}

# command line inputs
# logFile - full path to log file 
logFile = sys.argv[1]
email = sys.argv[2]
delayFile = sys.argv[3]

# seperator for log file
sep = ';'

# counters
total = 0
responseErrors = 0
noDateErrors = 0
preprints = 0
postprints = 0

preprintIsOA = 0
preprintIsNotOA = 0
preprintJournals = []

postprintIsOA = 0
postprintIsNotOA = 0
postprintJournals = []

# open the log file
dFile = open(delayFile, "w")
lFile = open(logFile, "r")
for line in lFile:

   parts = line.split(sep)
   preprint_date = parts[4]
   peer_review_doi = parts[3]

   if (peer_review_doi != "" ):
     total += 1
     p = peer_review_doi.split("/")
     l = len(p)
     if (l == 5):
       url = "https://api.unpaywall.org/v2/" + p[-2].strip() + "/" + p[-1].strip() + "?email=" + email.strip()
     if (l == 6):
       url = "https://api.unpaywall.org/v2/" + p[-3].strip() + "/" + p[-2].strip() + "/" + p[-1].strip() + "?email=" + email.strip()
     response = requests.get(url, headers=headers)
     if ( response.status_code == 200 ):

        # extract data from the returned JSON object
        json_object = json.loads(response.content.decode('utf-8'))
        r = json_object['journal_is_in_doaj'] # True if gold OA, false otherwise
        journal = json_object['journal_name']
        published_date = json_object['published_date']

        # publication delay
        preprint = preprint_date.split("T")
        preprint = preprint[0].split("-")
        if ( published_date is None ):
           noDateErrors += 1
        else:
           j = published_date.split("-")
           d0 = date(int(preprint[0]), int(preprint[1]), int(preprint[2]))
           d1 = date(int(j[0]), int(j[1]), int(j[2]))        
           delta = d1 - d0
           if (delta.days <= 0):
              postprints += 1
              if ( r == True ):
                 postprintIsOA += 1
              else: 
                 postprintIsNotOA += 1
              if (journal not in postprintJournals):
                 postprintJournals.append(journal)
           else:
              preprints += 1
              if ( r == True ):
                preprintIsOA += 1
              else:
                preprintIsNotOA += 1
              if (journal not in preprintJournals):
                 preprintJournals.append(journal)
           print(delta.days, file=dFile)
     else:
        responseErrors += 1
        
# close the log files  
lFile.close()
dFile.close()

print("Total number of papers", total)
print()
print("Preprints", preprints)
print("Preprints OA", preprintIsOA)
print("Preprints Not OA", preprintIsNotOA)
print("Preprint Percentage OA", (preprintIsOA/preprints)*100)
print("Preprint Unique journals", len(preprintJournals))
print()
print("Postprints", postprints)
print("Postprints OA", postprintIsOA)
print("Postprints Not OA", postprintIsNotOA)
print("Postprint Percentage OA", (postprintIsOA/postprints)*100)
print("Postprint Unique journals", len(postprintJournals))
print()
print("Response Errors", responseErrors)
print("No date errors", noDateErrors)
print()
print()
