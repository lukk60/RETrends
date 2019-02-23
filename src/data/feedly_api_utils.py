# Utility functions to query the feedly API

import requests
import json
import urllib


def get_subscriptions(headers):    
    '''Get all subscriptions for current user.

    Parameters
    ----------
    headers: dict
        Authenication information for feedly API

    Returns
    -------
    list of dictionaries
        list of all subscriptions with metadata 
    '''
    service = "http://cloud.feedly.com/v3/subscriptions/"
    res = requests.get(url=service, headers=headers)
    
    assert res.status_code == 200, "API Call returned bad result (Code %s)" %res.status_code
    return res.json() 

def get_categories(headers):   
    '''Get all categories for current user

    Parameters
    ----------
    headers: dict
        Authenication information for feedly API

    Returns
    -------
    list of dictionaries
        list of categories with metadata 
    '''
    service = "http://cloud.feedly.com/v3/categories/"
    res = requests.get(url=service, headers=headers)
    
    assert res.status_code == 200, "API Call returned bad result (Code %s)" %res.status_code
    return res.json() 


def get_feed_metadata(feedURI, headers):
    '''Get metadata such as Topic, language, number of subscribers etc. on a given feed

    Parameters
    ----------
    feedURI: str
        Feed Identifier (e.g. 'feed/http://abc.ch/xy')
    headers: dict
        Authenication information for feedly API
    Returns
    -------
    dict
        dictionary containing metadata on given feed
    '''
    feedURI = urllib.parse.quote(feedURI, safe="")
    service = "http://cloud.feedly.com/v3/feeds/"
    res = requests.get(url=service+feedURI, 
                       headers=headers)

    assert res.status_code == 200, "API Call returned bad result (Code %s)" %res.status_code
    return res.json() 


def get_stream_ids(streamID, headers, count=100, continuation=None):
    '''Get stream ids for a given feedID

    Parameters
    ----------
    streamID: str
        stream identifier (e.g. 'feed/http://abc.ch/xy')
    headers: dict
        Authenication information for feedly API
        
    Returns
    -------
    list
        list of dictionarys 
    '''
    query = {"streamId": streamID,
            "count": count}
    service = "http://cloud.feedly.com/v3/streams/ids?"
    
    res = requests.get(url=service, params=query, headers=headers)
    
    assert res.status_code == 200, "API Call returned bad result (Code %s)" %res.status_code
    return res.json() 


def get_feed_content(streamID, headers, count=100, continuation=None):
    '''Get contents of a given feed

    Parameters
    ----------
    streamID: str
        stream identifier (e.g. 'feed/http://abc.ch/xy')
    headers: dict
        Authenication information for feedly API
    count: int
        number of results to return
    continuation:
        continuation-string from previous call
        
    Returns
    -------
    list
        dictionary
    '''
    
    query = {"streamId": streamID,
            "count": count,
            "continuation": continuation}
    service = "https://cloud.feedly.com/v3/streams/contents?" + urllib.parse.urlencode(query)

    res = requests.get(url=service, headers=headers)
    
    assert res.status_code == 200, "API Call returned bad result (Code %s)" %res.status_code
    return res.json() 

def get_feedlist(category, headers):
    '''get all feeds for a given category

    Parameters
    ----------
    category: str
        name of the category to retrieve 
    headers: dict
        Authenication information for feedly API
        
    Returns
    -------
    list
        list of feed IDs 
    '''
    subs = get_subscriptions(headers)
    
    feeds = []
    
    for s in subs:
        if s["categories"][0]["label"] == category:
            feeds.append(s["id"])
    
    return feeds

def download_feeds(feedIDs, headers, count=10):
    '''download the contents for a list of feeds 

    Parameters
    ----------
    feedIDs: list
        list of feedIDs to retrieve
    headers: dict
        Authenication information for feedly API
    count: int
        number of items to retrieve per feed
        
    Returns
    -------
    list
        list of feed IDs 
    '''
    feedContents = {}
    
    for f in feedIDs:
        feedContents[f] = get_feed_content(f, headers, count)
        
    return feedContents        

def restructure_data(feedData):
    '''restructure the feedly data structure so each item in the dictionary is an 
    article identified by its id. information stored on feed-level is added to each article object.

        Parameters
        ----------
        feedData: dictionary
            dictionary returned by download_feeds
    
        Returns
        -------
        dictionary
            dictionary where each item is an article 
    '''

    articles = {}

    for f in feedData.keys():
        for i in feedData[f]["items"]:
            i["feedId"]    = feedData[f]["id"]
            i["feedTitle"] = feedData[f]["title"]

            articles[i["id"]] = i
    
    return articles


