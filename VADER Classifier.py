import json
import pandas as pd
from nltk import tokenize
import pandas as pd
import matplotlib.pyplot as plt

tweet_files = ['US_2018-03-22.json','US_2018-03-25.json','US_2018-03-23.json','US_2018-03-26.json','US_2018-03-27.json']
#'US_2018-03-22.json','US_2018-03-25.json','US_2018-03-23.json','US_2018-03-26.json','US_2018-03-27.json' 'negative_tweets.json','positive_tweets.json'
tweets_data = []
for file in tweet_files:
    with open(file, 'r') as f:
        for line in f.readlines():
            tweets_data.append(json.loads(line))

#Json to dataframe
def populate_tweet_df(tweets):


    df = pd.DataFrame()
    df['created_at']= list(map(lambda tweet: tweet['created_at'], tweets))
    df['text'] = list(map(lambda tweet: tweet['text'], tweets))
    df['favorite_count'] = list(map(lambda tweet: tweet['favorite_count'], tweets))
    df['favorited'] = list(map(lambda tweet: tweet['favorited'], tweets))
    df['retweeted'] = list(map(lambda tweet: tweet['retweeted'], tweets))
    df['id'] = list(map(lambda tweet: tweet['id'], tweets))
    df['entities'] = list(map(lambda tweet: tweet['entities'], tweets))
    df['user'] = list(map(lambda tweet: tweet['user'], tweets))
    df['location'] = list(map(lambda tweet: tweet['user']['location'], tweets))
    df['lang'] = list(map(lambda tweet: tweet['lang'], tweets))
    df['country'] = list(map(lambda tweet: tweet['place']['country'] if tweet['place'] != None else None, tweets))
    return df

#------------------------------------------preprocessing-------------------------#

from nltk.tokenize import TweetTokenizer # a tweet tokenizer from nltk.
tokenizer = TweetTokenizer()
from nltk.corpus import stopwords
from nltk.stem.porter import *
import re


networds =[]#['internet','netnuetrality']
def stem_tokens(tokens, stemmer):
   stemmed = []
   for item in tokens:
       stemmed.append(stemmer.stem(item))
   return stemmed

def preprocessor(text):
    words = text.split()
    stops = set(stopwords.words("english"))
    del words[0]
    words = [re.sub('[^0-9a-zA-Z]+', '', w.replace('#','').lower()) for w in words if not w.startswith('http') and not w.startswith('@')]
    finalwords = [w for w in words if (not w.isdigit() and w not in networds and w not in stops)]
    stemmer = PorterStemmer()
    stemmed = stem_tokens(finalwords, stemmer)

    return ' '.join(stemmed)


data=populate_tweet_df(tweets_data)
print("Total Tweets $:",len(tweets_data))
data['text'] = data['text'].apply(preprocessor)

#-------------------------------------wordcloud-------------------------------
'''
from wordcloud import WordCloud, STOPWORDS
def wordcloud_by_province(tweets):
    a = pd.DataFrame(tweets['text'].str.contains("ajit").astype(int))
    b = list(a[a['text']==1].index.values)
    stopwords = set(STOPWORDS)
    stopwords.add("kill")
    stopwords.add("save")

    wordcloud = WordCloud(background_color="white",stopwords=stopwords,
                          random_state = 50).generate(" ".join([i for i in tweets.ix[b,:]['text'].str.upper()]))
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.show()

wordcloud_by_province(data)

'''
#--------------------------categorizing tweets---------------------------------------------
#Sentment Analysing by using existing library
from nltk.sentiment.vader import SentimentIntensityAnalyzer
sid = SentimentIntensityAnalyzer()

data['sentiment_compound_polarity']=data.text.apply(lambda x:sid.polarity_scores(x)['compound'])
data['sentiment_neutral']=data.text.apply(lambda x:sid.polarity_scores(x)['neu'])
data['sentiment_negative']=data.text.apply(lambda x:sid.polarity_scores(x)['neg'])
data['sentiment_pos']=data.text.apply(lambda x:sid.polarity_scores(x)['pos'])
data['sentiment_type']=''
data.loc[data.sentiment_compound_polarity>0,'sentiment_type']='POSITIVE'
data.loc[data.sentiment_compound_polarity==0,'sentiment_type']='NEUTRAL'
data.loc[data.sentiment_compound_polarity<0,'sentiment_type']='NEGATIVE'
print(data.head(2))


#--------------------- Distribution Graphs-------------------------------------------------------------------
import matplotlib
matplotlib.style.use('ggplot')

tweets_sentiment = data.groupby(['sentiment_type'])['sentiment_neutral'].count()
tweets_sentiment.rename("",inplace=True)
explode = (0, 0,1.0)
plt.subplot(221)
tweets_sentiment.transpose().plot(kind='barh',figsize=(10, 6))
plt.title('Sentiment Analysis ', bbox={'facecolor':'0.8', 'pad':0})
plt.subplot(222)
tweets_sentiment.plot(kind='pie',figsize=(10, 6),autopct='%1.1f%%',shadow=True,explode=explode)
plt.legend(bbox_to_anchor=(1, 1), loc=3, borderaxespad=0.)
plt.title('Sentiment Analysis ', bbox={'facecolor':'0.8', 'pad':0})
plt.show()


#evaluation of sentiments by hours
import numpy as np
#import matplotlib.pyplot as plt
data['hour'] = pd.DatetimeIndex(data['created_at']).hour
data['count'] = 1
tweets_filtered = data[['hour', 'sentiment_type', 'count']]
pivot_tweets = tweets_filtered.pivot_table(tweets_filtered, index=["sentiment_type", "hour"], aggfunc=np.sum)
print(pivot_tweets.head())

sentiment_type = pivot_tweets.index.get_level_values(0).unique()
f, ax = plt.subplots(1, 1, figsize=(7, 10))
plt.setp(ax, xticks=list(range(0,24)))

for sentiment_type in sentiment_type:
    split = pivot_tweets.xs(sentiment_type)
    split["count"].plot( legend=True, label='' + str(sentiment_type))
plt.title('Hourly sentiment reviews', bbox={'facecolor':'0.8', 'pad':0})
plt.show()
