import twitter 


api = twitter.Api(consumer_key='4Mpcp4aZdh0F2VS7nPHE6dgBC',
	consumer_secret='eMkStwK4C4LCdCspt92Rg5MS2OedEJKjJzVtnhgKatHhEAq34e',
	access_token_key='4358774233-p8P1IVzt7lJGvROi5aWUjlO3hPbKvC05UIdixH3',
	access_token_secret='IS6b8Dv19s6Hh6EBc3BZoahQ3uNqZXmn9rjlzxgtC2Fcf')



#print api.VerifyCredentials()

def createTestData(search_string):
	try:
		tweets_fetched = api.GetSearch(search_string, count = 100)
		print "Fetched!" + search_string
		return [{"text":status.text, "label":None} for status in tweets_fetched]

	except:
		print "Fuck!"
		return None


search_string = raw_input("enter input!")
testData = createTestData(search_string)
print testData[0:9]


##############################classifying tweets###########################################

"""
def createTrainingCorpus(corpusFile, tweetDataFile):
	import csv
	corpus = []
	with open(corpusFile, 'rb') as csvfile:
		lineReader = csv.reader(csvfile, delimiter=',', quotechar='\"')
		for row in lineReader:
			corpus.append({"tweet_id":row[2], label:row[1], "topic":row[0]})



	#to download full corpus
	import time
	rate_limit = 180
	sleep_time = 900/180
	trainingData = []
	for tweet in corpus:
		try:
			status = api.GetStatus(tweet["tweet_id"])
			print "Tweet fetched" + status.text
			tweet["text"] = status.text
			trainingData.append(tweet)
			time.sleep(sleep_time)
		except:
			continue

	#writing to csv file
	with open(tweetDataFile, 'wb') as csvfile:
	linewriter = csv.writer(csvfile, delimiter=',', quotechar='\"')
		for tweet in trainingData:
			linewriter.writerow([tweet["tweet_id"], tweet["text"], tweet["label"], tweet["topic"]])

	return trainingData
"""

def createLimitedTrainingCorpus(corpusFile, tweetDataFile):

	import csv
	corpus = []
	with open(corpusFile, 'rb') as csvfile:
		lineReader = csv.reader(csvfile, delimiter=',', quotechar='\"')
		for row in lineReader:
			corpus.append({"tweet_id":row[2], "label":row[1], "topic":row[0]})



	#to download full corpus
	trainingData = []

	for label in ['positive','negative']:
		i=1

		for tweet in corpus:
			if tweet["label"] == label and i<=50:
				try:
					status = api.GetStatus(tweet["tweet_id"])
					print "Tweet fetched" + status.text
					tweet["text"] = status.text
					trainingData.append(tweet)
					i = i+1
				except Exception, e:
					print e

	#writing to csv file
	with open(tweetDataFile, 'wb') as csvfile:
		linewriter = csv.writer(csvfile, delimiter=',', quotechar='\"')
		for tweet in trainingData:
			try:
				linewriter.writerow([tweet["tweet_id"], tweet["text"], tweet["label"], tweet["topic"]])
			except Exception, e:
				print e
	return trainingData


corpusFile = "/mnt/d/dhruv/twitter/sanders-twitter-0.2/corpus.csv"
tweetDataFile = "/mnt/d/dhruv/twitter/sanders-twitter-0.2/tweetDataFile.csv"

trainingData = createLimitedTrainingCorpus(corpusFile, tweetDataFile)