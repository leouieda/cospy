import sys
import utils
from Preprint import Preprint
from callDownloadApi import callDownloadApi

# command line inputs
# downloadDir - directory to download papers to, also where logs are stored
downloadDir = sys.argv[1]
# print out status messages as we go along (True or False)
verbose = sys.argv[2]
# start date - YYYY-MM-DD we should start the index from
startDate = sys.argv[3]
# preprint provider
provider = sys.argv[4]

# seperator for log file
s1 = ';'

# the API returns all preprints that were created
# some papers may not be available for download
# due to moderation problems or retraction
# keep track of how many preprints we actually get
numPreprints = 0

# check that the download directory includes 
# the trailing /
lc = downloadDir[-1]
if (lc != '/'):
   downloadDir += '/'

# set up log files based on provider
log = downloadDir + provider + '_download_counts.log'

# get the data 
dois, dates, downloads = callDownloadApi(provider, startDate, verbose)

# open log files for writing 
l = open(log, 'w')

# loop over all the papers we found
n = len(dois)
for i in range(n):
   line = dois[i] + "," + dates[i] + "," + str(downloads[i])
   print( line, file=l ) 


# close the log files   
l.close()

# print out the results
print("Total downloads for", provider, "=", sum(downloads))
#print("Number of preprints downloaded:", numPreprints)

