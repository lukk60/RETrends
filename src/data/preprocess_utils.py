# -*- coding: utf-8 -*-
import pandas as pd
from bs4 import BeautifulSoup
from bs4.element import Comment
import unicodedata
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

def tag_visible(element):
    '''tags visible elements in a html document
    Parameters:
        element (bs4.element) html element

    Returns:
        Boolean (True if element is visible)
    '''
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    ''' extract visible text from a html document
    Parameters:
        body (bytes object e.g. from read("rb"))
    Returns:
        string with all visible text
    '''
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    
    return u" ".join(t.strip() for t in visible_texts)

def my_sent_tokenizer(document):
    ''' customizable sentence tokenizer
    '''
    return sent_tokenize(document)

def my_word_tokenizer(sentence):
    ''' customizable word tokenizer
    '''
    return word_tokenize(sentence)

def html_to_wordlist(document):
    ''' convert html document to conll format
    Parameters:
        document (bytes object e.g. from read("rb")
    Returns:
        list of sentences of list of words ([[s1w1, s1w2],[s2w1, s2w2]])
    '''
    out = []

    text = text_from_html(document)
    sents = my_sent_tokenizer(text)
    for s in sents:
        words = my_word_tokenizer(s)
        out.append(words)
    
    return out


def kaggle_to_conll(data, output_path):
    ''' casts the kaggle ner dataset in the correct format to be used by the modelling part
        
    Parameters:
        data (DataFrame): DataFrame with Columns "Sentence #", "Word" and "Tag"  
        output_path (str): Output Path

    Returns:
        None
    '''
    data = data[["Sentence #", "Word", "Tag"]].groupby("Sentence #")

    # create empty file
    pd.DataFrame().to_csv(output_path, header=False, index=False, sep=" ")
    
    # add sentences to file
    def agg_fun(df):
        df = df.append({"Word": "", "Tag": ""}, ignore_index=True)
        df[["Word","Tag"]].to_csv(output_path, mode="a", header=False, index=False, sep=" ")

    data.apply(agg_fun)
    
def split_train_dev_test(data, splits):
    ''' splits the dataframe into train dev and testset while avoiding to split up sentences

    Parameters:
        data (DataFrame): DataFrame with Columns "Sentence #", "Word" and "Tag"  
        splits (dict): dictionary with the names of the sets and the proportion of the data to include in each set

    Returns
        list of DataFrames
    ''' 
    
    def find_sentence_nr(s):
        return int(re.findall("\\d{1,6}", s)[0])
    
    data["SentNr"] = data["Sentence #"].apply(find_sentence_nr)

    nSentences = len(set(data["Sentence #"].values.tolist()))

    sets = {}
    firstSent = 0
    lastSent = 0
    for k,v in splits.items():
        lastSent = firstSent + int(nSentences*v)
        dk = data[(firstSent < data["SentNr"]) & (data["SentNr"] < lastSent)]
        sets[k] = dk
        firstSent = lastSent

    return sets

def strip_html(text):
    try:
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text()
    except TypeError:
        return None
    

def remove_accented_chars(text):
    try:
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        return text
    except TypeError:
        return None

def remove_special_characters(text, remove_digits=False):
    pattern = r'[^a-zA-Z0-9\s]' if not remove_digits else r'[^a-zA-Z\s]'
    try:
        text = re.sub(pattern, '', text)
        return text
    except TypeError:
        return None

def to_lowercase(text):
    try:
        return text.lower()
    except AttributeError:
        return None

def preprocess_document(doc):
    """ apply preprocessing steps
    
    Parameters
    ----------
    doc: string
        a raw text document

    Returns
    -------
    string
    """
    # check inputs
    if not doc:
        return None
    
    else:
        # strip html tags
        doc = strip_html(doc)

        # remove accented characters
        doc = remove_accented_chars(doc)

        # remove special characters
        doc = remove_special_characters(doc)
        
        # lowercasing
        doc = to_lowercase(doc)
        
        return(doc)