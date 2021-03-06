# Import various modules for string cleaning
from bs4 import BeautifulSoup
import re
from nltk.corpus import stopwords
import json
import pandas as pd
from nltk import tokenize
import pandas as pd

# Download the punkt tokenizer for sentence splitting
import nltk.data
#nltk.download()


tweet_files = ['US_2018-03-22.json','US_2018-03-25.json','US_2018-03-23.json','US_2018-03-26.json','US_2018-03-27.json']      #'US_2018-03-22.json','US_2018-03-25.json','US_2018-03-23.json','US_2018-03-26.json','US_2018-03-27.json','US_2018-03-28.json'
tweets_data = []
for file in tweet_files:
    with open(file, 'r') as f:
        for line in f.readlines():
            tweets_data.append(json.loads(line))

#--------------------------------------------preprocessing methods-----------------------------------

def review_to_wordlist( review, remove_stopwords=True ):
    # Function to convert a document to a sequence of words,
    # optionally removing stop words.  Returns a list of words.
    #
    # 1. Remove HTML
    review_text = BeautifulSoup(review,"html.parser").get_text()
    #
    # 2. Remove non-letters
    review_text = re.sub("[^a-zA-Z]"," ", review_text)
    #
    # 3. Convert words to lower case and split them
    words = review_text.lower().split()
    #
    # 4. Optionally remove stop words (false by default)
    if remove_stopwords:
        stops = set(stopwords.words("english"))
        words = [w for w in words if not w in stops]
    #
    # 5. Return a list of words
    return(words)

#Json to dataframe
def populate_tweet_df(tweets):
    df = pd.DataFrame()
    df['text'] = list(map(lambda tweet: tweet['text'], tweets))
    return df

#---------------------------------------------------------------------------------------------

# Load the punkt tokenizer
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

# Define a function to split a review into parsed sentences
def review_to_sentences( review, tokenizer, remove_stopwords=True ):
    # Function to split a review into parsed sentences. Returns a
    # list of sentences, where each sentence is a list of words
    #
    # 1. Use the NLTK tokenizer to split the paragraph into sentences
    raw_sentences = tokenizer.tokenize(review.strip())
    #
    # 2. Loop over each sentence
    sentences = []
    for raw_sentence in raw_sentences:
        # If a sentence is empty, skip it
        if len(raw_sentence) > 0:
            # Otherwise, call review_to_wordlist to get a list of words
            sentences.append( review_to_wordlist( raw_sentence, \
              remove_stopwords ))
    #
    # Return the list of sentences (each sentence is a list of words,
    # so this returns a list of lists
    return sentences

#--------------------------------------------------------------------------------------------
data=populate_tweet_df(tweets_data)
sentences = []  # Initialize an empty list of sentences

print ("Parsing sentences from unlabeled set")
for review in data["text"]:
    sentences += review_to_sentences(review, tokenizer)

#-------------------------------------building model--------------------------------

# Import the built-in logging module and configure it so that Word2Vec
# creates nice output messages
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',\
    level=logging.INFO)

# Set values for various parameters
num_features =300 # Word vector dimensionality
min_word_count = 1   # Minimum word count
num_workers = 4       # Number of threads to run in parallel
context = 10        # Context window size
downsampling = 1e-3   # Downsample setting for frequent words

# Initialize and train the model (this will take some time)
from gensim.models import word2vec
print ("Training model...")
model = word2vec.Word2Vec(sentences, workers=num_workers, \
            size=num_features, min_count = min_word_count, \
            window = context, sample = downsampling,sg=1)

# If you don't plan to train the model any further, calling
# init_sims will make the model much more memory-efficient.
model.init_sims(replace=True)

# It can be helpful to create a meaningful model name and
# save the model for later use. You can load it later using Word2Vec.load()
model_name = "MyModel"
model.wv.save(model_name)



