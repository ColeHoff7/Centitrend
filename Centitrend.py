import re
import twitter
import pickle
from textblob import TextBlob
import sys
from datetime import datetime
import pytz
import time

class TwitterClient(object):
    def __init__(self):
        # keys and tokens from the Twitter Dev Console
        consumer_key = 'XXX'
        consumer_secret = 'XXX'
        access_token = 'XXX'
        access_token_secret = 'XXX'

        # twitter authentication
        try:
            self.api = twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret, access_token_key=access_token, access_token_secret=access_token_secret)
        except:
            print("Error: Twitter Authentication Failed")

    def clean_tweet(self, tweet):
        '''
        Cleans tweets of links and special chars
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        '''
        Gets tweet sentiment using textblob
        '''
        analysis = TextBlob(self.clean_tweet(tweet))
        # We can also get the analysis.sentiment.subjectivity. May come in handy later
        return analysis.sentiment.polarity

    def get_tweets(self, query, m_id, r_type, count = 5):
        '''
        Fetches tweets and parses them
        '''
        # empty list to store parsed tweets
        tweets = []

        #try:
            # call twitter api to fetch tweets
        fetched_tweets = self.api.GetSearch(term = query, max_id = m_id, result_type = r_type, count = count, lang='en')
        for tweet in fetched_tweets:
            parsed_tweet = {}
            parsed_tweet['created_at'] = tweet.created_at
            parsed_tweet['text'] = tweet.text
            parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)
            parsed_tweet['id'] = tweet.id;

            # if tweet.retweet_count > 0:
            #     # no retweets
            if parsed_tweet not in tweets:
                tweets.append(parsed_tweet)
            # else:
            #     tweets.append(parsed_tweet)
        return tweets

        #except tweepy.TweepError as e:
        #    print("Error with Tweepy: " + str(e))

def main():
    api = TwitterClient()
    max_id = None
    tweets = []
    dateStuff = {}
    print("Searching for tweets")
    max_id = sys.maxsize

    for j in range(25):
        print('Iteration {}'.format(j))
        for i in range(180):
            print('\tBatch {}'.format(i))
            tweets.extend(api.get_tweets(query = '$GOOG', m_id = max_id, r_type = 'recent', count = 100))
            for tweet in tweets:
                stupidDate = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y').replace(tzinfo=pytz.UTC)
                radDate = datetime.strftime(stupidDate, "%Y-%m-%d")
                if not radDate in dateStuff:
                    dateStuff[radDate] = {'size':0, 'mean':0}
                dateStuff[radDate]['size']+=1
                dateStuff[radDate]['mean']+=tweet['sentiment']
                if tweet['id'] < max_id:
                    max_id = tweet['id']-1
        for date in dateStuff:
            dateStuff[date]['mean']/=dateStuff[date]['size']
        with open("dump.file", "wb") as f:
            pickle.dump(dateStuff, f, pickle.HIGHEST_PROTOCOL)
        time.sleep((15*60)+15)


    ptweets = [tweet for tweet in tweets if tweet['sentiment'] > 0]
    print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets)))
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] < 0]
    print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets)))
    print("Neutral tweets percentage: {} %".format(100*(len(tweets) - len(ntweets) - len(ptweets))/len(tweets)))

    print("\n\nPositive tweets:")
    for tweet in ptweets[:3]:
        print(tweet['text'])

    print("\n\nNegative tweets:")
    for tweet in ntweets[:3]:
        print(tweet['text'])

    #with open("dump.file", "rb") as f:
    #    tweets2 = pickle.load(f)
    #print(tweets2)


if __name__ == "__main__":
    # calling main function
    main()
