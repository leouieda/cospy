import json
import requests

def getDownloadStats ( cosApiToken, id ):

	url = "https://api.osf.io/v2/preprints/" + id.strip() + "/?metrics[downloads]=total"

	# Set up the headers to be sent as part of every API request
	headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {0}'.format(cosApiToken)}

    # Send our request to the search API
	response = requests.get(url, headers=headers)

    # Check the response status code, 200 indicates everything worked as expected
	if response.status_code == 200:

        # Extract the JSON data from the response
		json_object = json.loads(response.content.decode('utf-8'))
		meta = json_object['meta']['metrics']
		downloads =  meta['downloads']

	else:

		# Something went wrong with the API call/response
		print( "Error connecting to API, HTTP status code is: ", response.status_code )

	return downloads