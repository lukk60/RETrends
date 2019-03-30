# -*- coding: utf-8 -*-
import pandas as pd
from bs4 import BeautifulSoup
import unicodedata
import re
import nltk

def dataframe_to_conll(data, output_path):
    ''' casts the kaggle ner dataset in the correct format to be used by the modelling part
        
    Parameters:
        data (DataFrame): DataFrame with Columns "Word" and "Tag"  

    Returns:
        None
    '''
    emptyLine = {"Sentence #": None, "Word": "", "POS": "", "Tag": ""}

    for i in range(len(data)):
        if i == 0:
            pass
        else:
            if data["Sentence #"][i] != data["Sentence #"][i-1]:
                newline = pd.DataFrame(emptyLine, index=[float(i)-0.5])
                data = pd.concat([data.iloc[:i-1], newline, data.iloc[i:]]).reset_index(drop=True)
            else:
                pass
    
    data[["Word","Tag"]].to_csv(output_path, sep=" ", header=False, index=False)


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