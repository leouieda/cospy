import os
import sys
import utils

def main():

   # get the configuration parameters from environment variables
   cosApiToken = os.environ['cosApiToken']   # for accessing COS API 
   emailAddress = os.environ['emailAddress'] # for accessing Unpaywall API

   # command line inputs
   # downloadDir - directory to download papers to, also where logs are stored
   downloadDir = sys.argv[1]
   # print out status messages as we go along (True or False)
   verbose = sys.argv[2]
   # start date - YYYY-MM-DD we should start the index from
   startDate = sys.argv[3]
   endDate = sys.argv[4]
   # log file for the peer reviewed article data
   peerReviewLog = sys.argv[5]

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

   # preprint provider
   provider = 'eartharxiv'

   # set up log files based on provider
   log = downloadDir + provider + '.log'

   # get the papers
   preprints = utils.callOsfApi(cosApiToken, provider, startDate, endDate, verbose)
   print( len(preprints) )

main()
