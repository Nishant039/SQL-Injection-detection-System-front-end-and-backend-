import warnings
warnings.simplefilter("ignore")

import nltk
import pandas as pd
import numpy as np
import keras

text=pd.read_csv("plain.txt",sep='\n',skiprows=2,header=None)
text.head()
text.rename(columns={0:'txt'},inplace=True)

text2=pd.read_csv("sql_querys.txt",sep='\n',header=None)

s1=list(text['txt'])
s2=list(text2[0])
s1=[i.lower() for i in s1]
s2=[i.lower() for i in s2]

y1=[0 for i in range(len(s1))]
y2=[1 for i in range(len(s2))]
y=y1+y2
print("{} - plain text {} - sql injection querys".format(len(s1),len(s2)))

from nltk.stem import WordNetLemmatizer
word_lem=WordNetLemmatizer()


new_s1=[]
stopwords=nltk.corpus.stopwords.words("english")
for i in s1:
    temp=i.split(' ')
    temp1=[]
    for j in temp:

        j=j.strip(',').strip(r'["]').strip(';').strip('“').strip('”').strip(r'[.]+')
        j=j.replace("’",'')
        if j not in stopwords and j.isalpha():
            
            j=word_lem.lemmatize(j)
            temp1.append(j)

    new_s1.append(' '.join(temp1))


new_s2=[]
for i in s2:
    temp=i.split(' ')
    temp1=[]
    for j in temp:
        if j not in stopwords:
            
            j=word_lem.lemmatize(j)
            temp1.append(j)

    new_s2.append(' '.join(temp1))

new_s=new_s1+new_s2

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
tokenizer1 = Tokenizer(num_words = 100000, oov_token="<OOV>")
tokenizer1.fit_on_texts(new_s)
word_index1 = tokenizer1.word_index

sequences1 = tokenizer1.texts_to_sequences(new_s)

n=0
for i in sequences1:
    n=max(n,len(i))


padded1 = pad_sequences(sequences1, maxlen=150,padding="post")

df_new=pd.DataFrame(padded1)
df_new["target"]=y


from sklearn.model_selection import train_test_split
X_train,X_test,y_train,y_test=train_test_split(df_new.iloc[:,:150],pd.Series(y),random_state=42)


def get_model_tokenizer():
	return tokenizer1




