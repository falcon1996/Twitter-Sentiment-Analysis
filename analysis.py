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