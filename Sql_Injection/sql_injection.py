import glob
import time
import pandas as pd
# from xml.dom import minidom
from nltk import ngrams
from nltk.tokenize import sent_tokenize
import nltk
#nltk.download('punkt')
#nltk.download('stopwords')
#nltk.download('wordnet')
from nltk.stem import PorterStemmer
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
import pickle

import pandas as pd
df = pd.read_csv("sqli.csv",encoding='utf-16')

from sklearn.feature_extraction.text import CountVectorizer
vectorizer = CountVectorizer( min_df=2, max_df=0.7, stop_words=stopwords.words('english'))
posts = vectorizer.fit_transform(df['Sentence'].values.astype('U')).toarray()

transformed_posts=pd.DataFrame(posts)
transformed_posts.to_csv('preprocessed.csv')

df=pd.concat([df,transformed_posts],axis=1)

X=df[df.columns[2:]]

y=df['Label']

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

from sklearn.linear_model import LogisticRegression
clf = LogisticRegression(random_state=0).fit(X_train, y_train)

# save the model to disk
filename = 'sql.sav'
pickle.dump(clf, open(filename, 'wb'))

from sklearn.metrics import accuracy_score
#X_test = [[1,2,3,4,5]]
y_pred=clf.predict(X_test)
acc = accuracy_score(y_test, y_pred)

print(y_pred)
print("Accuracy :",acc)
