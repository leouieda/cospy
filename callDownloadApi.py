import utils
from Preprint import Preprint
from api_token import osf_token

def callDownloadApi( provider='eartharxiv', filterDate='', verbose=True ):

   # Results
   allDois = []
   allDates = []
   allDownloads = []

   # URLs for OSF API

# new url as of June 2019
#  https://api.osf.io/v2/preprints/35juv/?metrics[downloads]=total
#  where 35juv is the preprint identifier

   # API URL to search/download preprints, NOTE: this is currently hard-coded to search EarthArXiv
   api_url_search = "https://api.osf.io/v2/preprints/?metrics[downloads]=total&page[size]=500&filter[provider]=" + provider

   # Are we filtering by date?
   if ( filterDate != '' ):
       api_url_search += '&filter[date_created][gte]=' + filterDate 

   # Set up the headers to be sent as part of every API request
   # osf_token is unique to each user and needs to be obtained from OSF site, it's imported from api_token.py
   headers = {'Content-Type': 'application/json',
             'Authorization': 'Bearer {0}'.format(osf_token)}

   # Send a request to the search API, this example just asks for all preprints at EarthArXiv
   response = utils.queryAPI(api_url_search, headers)

   # Check the response status code, 200 indicates everything worked as expected
   page = 1
   if response.status_code == 200:

       # Status update
       if ( verbose ):
          print("Working on page", page)

       # Extract the JSON data from the response
       json_object = utils.getJSON( response ) 

       # Parse all the preprints in the response (the current 'page' of results)
       dois, dates, downloads = utils.parseDownloadCounts( json_object )
       allDois.extend(dois)
       allDates.extend(dates)
       allDownloads.extend(downloads)

       # The API returns 500 preprints per "page". We need to look at the Links
       # data to see if there are additional pages. 
       next = json_object['links']['next']

       # Send a request to the search API, this time for the next page
       while( next != None ):
     
           page += 1
           if (verbose):
              print("Working on page", page)

           nextResponse = utils.queryAPI(next, headers)
           json_object = utils.getJSON( nextResponse ) 
           dois, dates, downloads = utils.parseDownloadCounts( json_object )
           allDois.extend(dois)
           allDates.extend(dates)
           allDownloads.extend(downloads)
           next = json_object['links']['next']

   else:

       # Something went wrong with the API call/response
       print( "Error connecting to API, HTTP status code is: ", response.status_code )

   return allDois, allDates, allDownloads 
