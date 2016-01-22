from scraper import get_article_text_and_metadata
from sklearn.externals import joblib

from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer

wordnet = WordNetLemmatizer()

def my_tokenize(doc):
    tok = word_tokenize(doc)
    return[wordnet.lemmatize(x) for x in tok]

print "Input url: "
url = raw_input()

article = [get_article_text_and_metadata(url)[0]]

count_vect = joblib.load('data/count_vect.pkl')
tfidf_tranformer = joblib.load('data/tfidf_tranformer.pkl')
model = joblib.load('logistic_model.pkl')

counts = count_vect.transform(article)
article_tfidf = tfidf_tranformer.transform(counts)

print model.predict_proba(article_tfidf)
print model.predict(article_tfidf)