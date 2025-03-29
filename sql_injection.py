import glob
import time
# from xml.dom import minidom
from nltk import ngrams
from nltk.tokenize import sent_tokenize
import nltk
#nltk.download('punkt')
#nltk.download('stopwords')
#nltk.download('wordnet')
from nltk.stem import PorterStemmer
from nltk.stem import PorterStemmer
from datetime import datetime
dt = datetime.now().timestamp()
#run = 1 if dt-1692057600<0 else 0
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
import pickle
import numpy as np
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import keras
import cv2
import tensorflow.keras

model = tensorflow.keras.models.load_model('XSS_model.h5')

df = pd.read_csv("sqli.csv",encoding='utf-16')

from sklearn.feature_extraction.text import CountVectorizer
vectorizer = CountVectorizer( min_df=2, max_df=0.7, stop_words=stopwords.words('english'))
posts = vectorizer.fit_transform(df['Sentence'].values.astype('U')).toarray()

transformed_posts=pd.DataFrame(posts)
#transformed_posts.to_csv('preprocessed.csv')

df=pd.concat([df,transformed_posts],axis=1)

X=df[df.columns[2:]]

y=df['Label']
df.to_csv('cleanedDataset.csv')

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

def sqlFeatures(query):
    df = [[query]]
    feat = vectorizer.transform([query]).toarray()
    return feat


def convert_to_ascii(sentence):
    sentence_ascii=[]

    for i in sentence:
        
        
        """Some characters have values very big e.g. 8221 and some are chinese letters
        we are removing letters having values greater than 8222 and for rest greater 
        than 128 and smaller than 8222 assigning them values so they can easily be normalized"""
       
        if(ord(i)<8222):      # ” has ASCII of 8221
            
            if(ord(i)==8217): # ’  :  8217
                sentence_ascii.append(134)
            
            
            if(ord(i)==8221): # ”  :  8221
                sentence_ascii.append(129)
                
            if(ord(i)==8220): # “  :  8220
                sentence_ascii.append(130)
                
                
            if(ord(i)==8216): # ‘  :  8216
                sentence_ascii.append(131)
                
            if(ord(i)==8217): # ’  :  8217
                sentence_ascii.append(132)
            
            if(ord(i)==8211): # –  :  8211
                sentence_ascii.append(133)
                
                
            """
            If values less than 128 store them else discard them
            """
            if (ord(i)<=128):
                    sentence_ascii.append(ord(i))
    
            else:
                    pass
            

    zer=np.zeros((10000))

    for i in range(len(sentence_ascii)):
        zer[i]=sentence_ascii[i]

    zer.shape=(100, 100)


#     plt.plot(image)
#     plt.show()
    return zer

def detect_xss(sentences):
    arr=np.zeros((len(sentences),100,100))
    image=convert_to_ascii(sentences)

    x=np.asarray(image,dtype='float')
    image =  cv2.resize(x, dsize=(100,100), interpolation=cv2.INTER_CUBIC)
    image/=128

    
#     if i==1:
#         plt.plot(image)
#         plt.show()    
    arr=image
    # Reshape data for input to CNN
    data = arr.reshape(1, 100, 100, 1)
    pred=model.predict(data)
    pred = "Normal" if pred[0][0] < 0.5 else 'XSS Scripting Attack'
    return pred
