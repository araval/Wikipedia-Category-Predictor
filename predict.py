from scraper import get_article_text_and_metadata
from sklearn.externals import joblib
import numpy as np
import requests
from model import my_tokenize
import sys

print "Input url: ", 
url = raw_input().strip()

try:
    r = requests.get(url)
except requests.exceptions.RequestException as e: 
    print e
    sys.exit(1)

article = [get_article_text_and_metadata(url)[0]]

#Load vectorizer and model:
count_vect = joblib.load('pickledModel/count_vect.pkl')
tfidf_tranformer = joblib.load('pickledModel/tfidf_tranformer.pkl')
model = joblib.load('pickledModel/logistic_model.pkl')

#prepare data for prediction
counts = count_vect.transform(article)
article_tfidf = tfidf_tranformer.transform(counts)

#predict and print
classes =  model.classes_
probas = model.predict_proba(article_tfidf)

indices = np.argsort(probas[0])

print "\nProbabilities:\n\n"
for i in reversed(indices):
    print "%30s %05.2f%%" % (classes[i], probas[0][i]*100)

print "\n\n"
print 'Predicted Category:', model.predict(article_tfidf)[0]
print "\n"

