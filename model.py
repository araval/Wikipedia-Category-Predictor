import os
try:
    import cPickle as pkl
except ImportError:
    import pickle as pkl

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

from sklearn.cross_validation import train_test_split
from sklearn.cross_validation import cross_val_score

from sklearn.linear_model import LogisticRegression

from sklearn.pipeline import Pipeline
from sklearn.externals import joblib


def load_data():

    os.chdir('data/')

    data = []
    for filename in os.listdir(os.getcwd()):
        if filename[-4:] == '.pkl':
            print 'reading', filename
            with open(filename) as f:
                currentData = pkl.load(f)
            if len(currentData) < 2000:
                data += currentData
            else:
                data += currentData[:2000]

    article_text = []
    other_numbers = []
    target = []

    for item in data:
        article_text.append(item[0])
        other_numbers.append([item[1], item[2], item[3], item[4]])
        target.append(item[5])

    other_numbers = np.array(other_numbers)

    return article_text, other_numbers, target

def make_tfidf(X, num_features = 7000):

    from nltk.stem.wordnet import WordNetLemmatizer
    from nltk.tokenize import word_tokenize

    wordnet = WordNetLemmatizer()

    def my_tokenize(doc):
        tok = word_tokenize(doc)
        return[wordnet.lemmatize(x) for x in tok]

    count_vect = CountVectorizer(stop_words = 'english', max_features = num_features, tokenizer = my_tokenize)
    X_counts = count_vect.fit_transform(X)

    tfidf_transformer = TfidfTransformer()
    X_tfidf = tfidf_transformer.fit_transform(X_counts)

    joblib.dump(count_vect, 'count_vect.pkl')
    joblib.dump(tfidf_transformer, "tfidf_tranformer.pkl")

    return X_tfidf

if __name__ == "__main__":

    article_text, other_numbers, target = load_data()
    X_train, X_test, y_train, y_test = train_test_split(article_text, target)
    X_train_tfidf = make_tfidf(X_train)

    model = LogisticRegression(C=c, class_weight="auto")   
    model.fit(X_train_tfidf, y_train)
    joblib.dump(model, 'logistic_model.pkl')
