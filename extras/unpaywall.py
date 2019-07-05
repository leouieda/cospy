import sys
import json
import requests
from datetime import date
import pandas as pd
import datetime

def callUnpaywall( dataFrame, email ):

  journalInDoaj = []
  journalName = []
  journalPublicationDate = []

  d = { "totalManuscripts": 0, 
        "preprints": 0,
        "preprintsDOAJ": 0,
        "preprintsNotDOAJ": 0,
        "preprintPercentageDOAJ": 0,
        "preprintUniqueJournals": 0,
        "postprints": 0,
        "postprintsDOAJ": 0,
        "postprintsNotDOAJ": 0,
        "postprintPercentageDOAJ": 0,
        "postprintUniqueJournals": 0,
        "responseErrors": 0,
        "noDateErrors": 0
      }

  url = "https://api.unpaywall.org/v2/"
  headers = {'Content-Type': 'application/json'}

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

  for index, row in dataFrame.iterrows():
    
    if ( row['peerReviewDoi'] != '' ): 

      total += 1
      p = row['peerReviewDoi'].split("/")
      l = len(p)
      if (l == 5):
        u = url + p[-2].strip() + "/" + p[-1].strip() + "?email=" + email.strip()
      if (l == 6):
        u = url + p[-3].strip() + "/" + p[-2].strip() + "/" + p[-1].strip() + "?email=" + email.strip()
      response = requests.get(u, headers=headers)
      if ( response.status_code == 200 ):

        # extract data from the returned JSON object
        json_object = json.loads(response.content.decode('utf-8'))
        journalInDoaj.append( json_object['journal_is_in_doaj'] ) # True if gold OA, false otherwise
        journalName.append( json_object['journal_name'] )
        journalPublicationDate.append( json_object['published_date'] )

        # publication delay
        preprint = row['datePublished'].split("T")
        preprint = preprint[0].split("-")
        if ( journalPublicationDate is None ):
           noDateErrors += 1
        else:
           j = json_object['published_date'].split("-")
           d0 = date(int(preprint[0]), int(preprint[1]), int(preprint[2]))
           d1 = date(int(j[0]), int(j[1]), int(j[2]))        
           delta = d1 - d0
           if (delta.days <= 0):
              postprints += 1
              if ( json_object['journal_is_in_doaj'] == True ):
                 postprintIsOA += 1
              else: 
                 postprintIsNotOA += 1
              if (json_object['journal_name'] not in postprintJournals):
                 postprintJournals.append(json_object['journal_name'])
           else:
              preprints += 1
              if ( json_object['journal_is_in_doaj'] == True ):
                preprintIsOA += 1
              else:
                preprintIsNotOA += 1
              if (json_object['journal_name'] not in preprintJournals):
                 preprintJournals.append(json_object['journal_name'])
      else:
        journalInDoaj.append( 'Response Error' ) 
        journalName.append( 'Response Error' )
        journalPublicationDate.append( 'Response Error' )
        
    else:

        journalInDoaj.append( None ) 
        journalName.append( None )
        journalPublicationDate.append( None )

  # append to the dataframe
  dataFrame['journalInDoaj'] = journalInDoaj 
  dataFrame['journalName'] = journalName
  dataFrame['journalPublicationDate'] = journalPublicationDate

  # fill in the data
  d['totalManuscripts'] = total
  d['preprints'] = preprints
  d['preprintsDOAJ'] = preprintIsOA 
  d['preprintsNotDOAJ'] = preprintIsNotOA
  d['preprintPercentageDOAJ'] =  (preprintIsOA/preprints)*100
  d['preprintUniqueJournals'] = len(preprintJournals)
  d['postprints'] = postprints
  d['postprintsDOAJ'] = postprintIsOA
  d['postprintsNotDOAJ'] = postprintIsNotOA
  d['postprintPercentageDOAJ'] = (postprintIsOA/postprints)*100
  d['postprintUniqueJournals'] = len(postprintJournals)
  d['responseErrors'] = responseErrors
  d['noDateErrors'] = noDateErrors

  # convert to dataframe
  df = pd.DataFrame( d, index=[0] )

  return dataFrame, d

