import json
import requests
import pandas as pd

####################
## URLs for OSF API
####################

# API URL to list all preprint providers
api_url_providers = "https://api.osf.io/v2/preprint_providers"

# API URL for search
api_url_search = "https://api.osf.io/v2/preprints/?filter[provider]=" 

####################
####################

def getProviders( cosApiToken ):

	# Define a dictionary for the results
	ids = []
	descriptions = []
	d = { "providerID": [], 
	      "description": [] }

	# Set up the headers to be sent as part of every API request
	headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {0}'.format(cosApiToken)}

    # Send our request to the search API
	response = queryAPI(api_url_providers, headers)

    # Check the response status code, 200 indicates everything worked as expected
	if response.status_code == 200:

        # Extract the JSON data from the response
		json_object = getJSON( response ) 
		for i in range( len(json_object['data']) ):
			provider = json_object['data'][i]['attributes']
			descriptions.append( provider['description'] )
			ids.append( json_object['data'][i]['id'] )

		# We need to look at the Links data to see if there are additional pages. 
		next = json_object['links']['next']

    	# Send a request to the search API, this time for the next page
		while( next != None ):
			nextResponse = queryAPI(next, headers)
			json_object = getJSON( nextResponse ) 
			for i in range( len(json_object['data']) ):
				provider = json_object['data'][i]['attributes']
				descriptions.append( provider['description'] )
				ids.append( json_object['data'][i]['id'] )
				next = json_object['links']['next']

	else:

		# Something went wrong with the API call/response
		print( "Error connecting to API, HTTP status code is: ", response.status_code )

	d['providerID'] = ids
	d['description'] = descriptions

	return pd.DataFrame( d )

def getManuscripts( cosApiToken, provider='eartharxiv', startDate='', endDate='', verbose=True ):

   # List to hold all our manuscripts
   manuscripts = []

   # set up the search URL for this provider
   apiUrl = api_url_search + provider

   # Are we filtering by date?
   if ( startDate != '' ):
       apiUrl += '&filter[date_created][gte]=' + startDate 
   if ( endDate != '' ):
       apiUrl += '&filter[date_created][lte]=' + endDate 

   # Set up the headers to be sent as part of every API request
   headers = {'Content-Type': 'application/json',
             'Authorization': 'Bearer {0}'.format(cosApiToken)}

   # Send our request to the search API
   response = queryAPI(apiUrl, headers)

   # Check the response status code, 200 indicates everything worked as expected
   if response.status_code == 200:

       # Extract the JSON data from the response
	   json_object = getJSON( response ) 

       # Total number of manuscripts in the results
	   total_manuscripts = json_object['links']['meta']['total']
	   if (verbose): print("Total manuscripts returned:", total_manuscripts)

	   # Status update
	   page = 1
	   if (verbose): print("Working on results page", page)

       # Parse all the manuscripts in the response (the current 'page' of results)
	   ms = parseManuscripts( provider, json_object, headers, verbose )
	   manuscripts.extend( ms )

       # The API returns 10 preprints per "page". We need to look at the Links
       # data to see if there are additional pages. 
	   next = json_object['links']['next']

       # Send a request to the search API, this time for the next page
	   while( next != None ):
		   page +=1
		   if (verbose): print("Working on results page", page)
		   nextResponse = queryAPI(next, headers)
		   json_object = getJSON( nextResponse ) 
		   ms = parseManuscripts( provider, json_object, headers )
		   manuscripts.extend( ms )
		   next = json_object['links']['next']

   else:

       # Something went wrong with the API call/response
       print( "Error connecting to API, HTTP status code is: ", response.status_code )

   return pd.DataFrame( manuscripts )

 
def createManuscriptDict():

	d = { "cosID": '', 
	      "preprintDoi": '',
	      "peerReviewDoi": '',
          "preprintProvider": '',
          "title": '',
          "abstract": '', 
          "status": '',
          "webURL": '',
          "downloadURL": '', 
          "downloadCount": 0,
                
          "dateModified": '', 
          "datePublished": '', 
                
          "authors": [],
          "keywords": [] }

	return d

# Generic function to send a query to the API
def queryAPI( url, headers ):

	response = requests.get(url, headers=headers)
	return response

# Helper function to extract and decode JSON from API responses
def getJSON( response ):

	json_object = json.loads(response.content.decode('utf-8'))
	return json_object

# Helper function to parse JSON response and look for citation data
def parseCitation ( jsonData, manuscript ):
	
	authors = []
	data = jsonData['data']['attributes'] 
	manuscript['title'] = data['title'] 
	for a in range( len(data['author']) ):
		given = data['author'][a]['given']
		family = data['author'][a]['family']
		name = given.strip() + " " + family.strip()
		authors.append(name)
	manuscript['authors'] = authors
	return manuscript

# Helper function to parse JSON response and look for identifier data
#def parseIdentifier ( jsonData, manuscript ):

	# make sure we have valid data, sometimes the identifers are empty
#	test = len(jsonData['data'])
#	if ( test >= 1 ):
#		data = jsonData['data'][0]['attributes']
#		manuscript['identifier'] = data['value']
#		manuscript['identifierType'] = data['category']

#	return manuscript

# Function to loop over all preprints in the response and parse their data
def parseManuscripts( provider, json_object, headers, verbose=True ):

    # list to hold all the manuscripts
	manuscripts = []

	# Loop over all the response manuscripts
	for i in range( len(json_object['data']) ):
	
		# Response is comprised of Relationships, Links, and Attributes
		# Here we seperate them out of the response
		rel = json_object['data'][i]['relationships']
		attr = json_object['data'][i]['attributes']

		# Links also contains references to peer reviewed paper (if available) 
		links = json_object['data'][i]['links']
		if ( 'doi' in links ):
			peer_review_doi = links['doi']
		else:
			peer_review_doi = ''
		preprint_doi = links['preprint_doi']
		html_link = links['html']
		download_link = html_link + "/download"
		
		# Create a manuscript dictionary to store all the information 
		manuscript = createManuscriptDict()
		manuscript['cosID'] = json_object['data'][i]['id']
		manuscript['webURL'] = html_link
		manuscript['downloadURL'] = download_link
		manuscript['provider'] = provider
		manuscript['preprintDoi'] = preprint_doi
		manuscript['peerReviewDoi'] = peer_review_doi

		# Parse the Attributes data for this manuscript
		manuscript = parseAttrData( attr, manuscript )

		# The Relationships data has links to more information
		identifiersLink, citationLink = parseRelData( rel )

		# Now that we have the identifiers link (from the Relationships data), send it back to the API
		# to get the Identifier JSON and extract the actual DOI identifier
		if ( citationLink != '' ):
		#if ( identifiersLink != '' ):
		  
		    #############
		    ## this is redundant - we can get the same info from the initial response
		    #############

			#response2 = queryAPI( identifiersLink, headers )
			#if response2.status_code == 200:
			#	json_object2 = getJSON( response2 )
			#	manuscript = parseIdentifier( json_object2, manuscript )
			#else:
			#	print( "Error parsing Identifier Link, HTTP status code is: ", response2.status_code )

			# Do the same with the citation link to get all the authors
		
			response2 = queryAPI( citationLink, headers )
			if response2.status_code == 200:
				json_object2 = getJSON( response2 )
				manuscript = parseCitation( json_object2, manuscript )
			else:
				print( "Error parsing Citation Link, HTTP status code is: ", response2.status_code )	

		# Add the current manuscript to our list 
		manuscripts.append( manuscript )    

	return manuscripts

def parseAttrData( attr, manuscript ):

    keywords = []

    manuscript['dateModified'] = attr['date_modified']
    manuscript['abstract'] = attr['description']
    manuscript['status'] = attr['reviews_state']
    # there is also 'date_published' which is the date/time received by COS
    # but a doi may not be assigned right away
    # we use the date/time doi was assigned as the publication date
    manuscript['datePublished'] = attr['preprint_doi_created'] 
    n = len( attr['subjects'] )
    for i in range(n):
        keyword = attr['subjects'][i]
        n2 = len( keyword )
        for j in range(n2):
            # API returns the full keyword hierarchy, 
            # i.e Physical Sciences and Mathematics -> Earth Sciences -> Geology
            # We don't need to capture this each time
            # If we already have Physical Sciences and Mathematics -> Earth Sciences then just grab Geology
            if keyword[j]['text'] not in keywords:  
                keywords.append( keyword[j]['text'] )
    manuscript['keywords'] = keywords

    return manuscript

def parseRelData( rel ):
                        
    # make sure the links entry is available
    test = rel['identifiers']
    if ( 'links' in test ):
        identifiersLink = rel['identifiers']['links']['related']['href'] # DOI and other identifiers
        citationLink = rel['citation']['links']['related']['href'] # citation details
    else:
        identifiersLink = ''
        citationLink = ''
    return identifiersLink, citationLink
