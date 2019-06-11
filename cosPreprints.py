import os

# get the configuration parameters from environment variables
cosApiToken = os.environ['cosApiToken']   # for accessing COS API 
emailAddress = os.environ['emailAddress'] # for accessing Unpaywall API

print( cosApiToken )
print( emailAddress )
