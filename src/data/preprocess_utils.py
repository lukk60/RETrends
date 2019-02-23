# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import unicodedata
import re
import nltk

def strip_html(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()

def remove_accented_chars(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')
    return text

def remove_special_characters(text, remove_digits=False):
    pattern = r'[^a-zA-Z0-9\s]' if not remove_digits else r'[^a-zA-Z\s]'
    text = re.sub(pattern, '', text)
    return text

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
        doc = doc.lower()
        
        return(doc)