import os
import numpy as np

try:
    import cPickle as pkl
except ImportError:
    import pickle as pkl

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib

def load_data():

    os.chdir('data/')
    data = []
    for filename in os.listdir(os.getcwd()):
        if filename[-4:] == '.pkl':
            print 'reading', filename
            with open(filename) as f:
                currentData = pkl.load(f)
            data += currentData
    os.chdir('../')

    article_text = []
    target = []

    for item in data:
        article_text.append(item[0])
        target.append(item[5])

    return article_text, target

def my_tokenize(doc):
    wordnet = WordNetLemmatizer()
    tok = word_tokenize(doc)
    return[wordnet.lemmatize(x) for x in tok]

if __name__ == "__main__":

    article_text, target = load_data()
    X_train, X_test, y_train, y_test = train_test_split(article_text, target)

    count_vect = CountVectorizer(stop_words = 'english', max_features = 700, tokenizer = my_tokenize)
    X_train_counts = count_vect.fit_transform(X_train)

    tfidf_transformer = TfidfTransformer()
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)

    if not os.path.isdir('pickledModel'):
        os.mkdir('pickledModel')

    joblib.dump(count_vect, 'pickledModel/count_vect.pkl')
    joblib.dump(tfidf_transformer, "pickledModel/tfidf_tranformer.pkl")

    model = LogisticRegression(C=1, class_weight="balanced")   
    model.fit(X_train_tfidf, y_train)

    joblib.dump(model, 'pickledModel/logistic_model.pkl')
