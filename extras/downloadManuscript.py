import urllib.request

# Helper function to download a file from a URL
def download( url, localFile ):
	
	error = False
	message = ""

	try:
		response = urllib.request.urlretrieve(url, localFile)
	except urllib.error.URLError:
		error = True
		message = "URL Error"	
	except urllib.error.HTTPError:
		error = True
		message = "HTTP Error"
	except urllib.error.ContentTooShortError:
		error = True
		message = "Content Too Short Error"

	return error, message