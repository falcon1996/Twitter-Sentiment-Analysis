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

#for using limited tweet data set
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


import re
from nltk.tokenize import word_tokenize
from string import punctuation
from nltk.corpus import stopwords

class PreProcessTweets:
	def __init__(self):
		self._stopwords = set(stopwords.words('english')+list(punctuation)+['AT_USER', 'URL'])

	def processTweets(self, list_of_tweets):
		#list_of_tweets is a dictionary of text and label

		processTweets = []

		for tweet in list_of_tweets:
			processTweets.append(self._processTweet(tweet(["text"]),tweet["label"]))

		return processTweets

	def _processTweet(self,tweet):
		#conerting to lower case
		tweet = tweet.lower()

		#replacing links with word URL
		tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet)

		#replace @username with "AT_USER"
		tweet = re.sub('@[^\s]+', 'AT_USER', tweet)

		#replace #word with word
		tweet = re.sub(r'#([^\s]+)', r'\1', tweet)

		tweet = word_tokenize(tweet)

		return [word for word in tweet if word not in self._stopwords]


tweetProcessor = PreProcessTweets()
ppTrainingData = tweetProcessor.processTweets(trainingData)
ppTestData = tweetProcessor.processTweets(testData)

print ppTrainingData[:5]


import nltk
def buildVocabulary(ppTrainingData):
	all_words = []
	for(words, sentiment) in ppTrainingData:
		all_words.extend(words)
		wordlist = nltk.FreqDist(all_words)
		word_features = wordlist.keys()

		return word_features

def extract_features(tweet):
	tweet_words = set(tweet)
	features = {}
	for word in word_features:
		features['contains(%s)' % word] = (word in tweet_words)

	return features

word_features = buildVocabulary(ppTrainingData)
trainingFeatures = nltk.classify.apply_features(extract_features, ppTrainingData)

NBayesClassifier = nltk.NBayesClassifier.train(trainingFeatures)


#support vector machines

from nltk.corpus import sentiwordnet as swn
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer


svmTrainingData = [' '.join(tweet[0]) for tweet in ppTrainingData]

vectorizer = CountVectorizer(min_df=1)
X = vectorizer.fit_transform(svmTrainingData).toarray()

vocabulary = vectorizer.get_feature_names()

swn_weights = []

for word in vocabulary:
	try:
		synset = list(swn.senti_synsets(word))
		common_meaning = synset[0]

		if(common_meaning.pos_score() > common_meaning.neg_score()):
			weight = common_meaning.pos_score()

		elif (common_meaning.pos_score() < common_meaning.neg_score()):
			weight = common_meaning.neg_score()

		else:
			weight = 0

	except:
		weight = 0

	swn_weights.append(weight)


swn_X = []
for row in X:
	swn_X.append(np.multiply(row, np.array(swn_weights)))

swn_X = np.vstack(swn_X)


label_to_array = {"positive":1, "negative":2}
labels = [label_to_array[tweet[1]] for tweet in ppTrainingData]
y = np.array(labels)

from sklearn.svm import SVC 
SVCClassifier = SVC()
SVCClassifier.fit(swn_X, y)

#################Running Classifier##############

#Naive Bayes
NBResultLabels = [NBayesClassifier.classify(extract_features(tweet[0])) for tweet in ppTrainingData]

#SVM
SVResultLabels = []
for tweet in ppTestData:
	tweet_sentence = ' '.join(tweet[0])
	svmFeatures = np.multiply(vectorizer.transform([tweet_sentence]).toarray(), np.array(swn_weights))
	SVMResultLabels.append(SVMClassifier.predict(svmFeatures[0]))



############To get majority sentiment#########

if NBResultLabels.count('positive') > NBResultLabels.count('negative'):
	print "NB Result Positive Sentiment" + str(100 * NBResultLabels.count('positive')/len(NBResultLabels)+ "%")
else:
	print "NB Result Negative Sentiment" + str(100 * NBResultLabels.count('negative')/len(NBResultLabels)+ "%")



if SVMResultLabels.count(1) > SVMResultLabels.count(2):
	print "SVM Result Positive Sentiment" + str(100 * SVMResultLabels.count(1)/len(SVMResultLabels)+ "%")
else:
	print "SVM Result Negative Sentiment" + str(100 * SVMResultLabels.count(2)/len(SVMResultLabels)+ "%")