import os
import sys
import utils
import extras.downloadStats as stats
import extras.downloadManuscript as dm 

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
   
   df = utils.getProviders( cosApiToken )

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
   manuscripts = utils.getManuscripts(cosApiToken, provider, startDate, endDate, verbose)

   # example downloading PDF
   dm.download( manuscripts['downloadURL'][0], '/Users/narock/Desktop/test.pdf')

   # example getting download statistics
   downloads = stats.getDownloadStats( cosApiToken, manuscripts['cosID'][0] )
   print( manuscripts['cosID'][0], 'downloaded', downloads, 'times')

main()
