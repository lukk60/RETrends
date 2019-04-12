# -*- coding: utf-8 -*-
import pandas as pd

def extract_entities(s):
    """ create entity- and taglist from a sentence
    Parameters:
        s: list of entity-tag tuples
    Returns:
        (entitiylist, taglist)
    """
    entities = []
    tags = []
    for w,t in s:
        t = t.split("-")
        if [0] == 'O':
            pass
        if t[0] == "B":
            entities.append(w)
            tags.append(t[1])
        if t[0] == "I":
            try:
                entities[-1] += " " + w
            except IndexError:
                entities.append(w)
                tags.append(t[1])
    sentence = " ".join(w for w,_ in s)
    return (sentence, entities, tags)            

def get_entity_list(data):
    """ convert prediction result to DataFrame containing a list of entities per sentence
    Parameters:
        data (dict): keys documentname, values list of sentences and word/tag tuples
    Returns:
        DataFrame
    """
    entityList = {}
    for k, doc in data.items():
        entityList[k] = {}
        for i,s in enumerate(doc):
            sentence, entities, tags = extract_entities(s)
            entityList[k][i] = {
                "sentence": sentence, "entities": entities, "tags": tags
                }
        
    return(entityList)

