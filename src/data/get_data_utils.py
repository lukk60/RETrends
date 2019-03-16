# -*- coding: utf-8 -*-
# Utility functions for data collection
from googlesearch import search
import time
import requests


def get_links(searchStrings, topN):
    ''' send queries to google websearch and return first N results as links
    Parameters:
        searchStrings: list
            list of strings to send as query to google search
        topN: int
            number of results to return
    Returns:
        dict with list of links of length topN for each search query
    '''
    res = dict()

    for l in searchStrings:
        llist = []
        searchGenerator = search(l, stop=topN)
        for i in range(topN):
            llist.append(searchGenerator.send(None))
    
        res[l] = llist
    
    return res

def merge_linklists(new, old):
    ''' union new and old linklists
    Parameters:
        new: dict
            new links
        old: dict
            old links
    Returns:
        dict with old and new links
    '''
    for k,v in new.items():
        try: 
            old[k] = list(set(old[k]+v))
        except KeyError:
            old[k] = v

    return(old)



def crawl_links(links):
    # https://www.dataquest.io/blog/web-scraping-tutorial-python/
    pass
    


