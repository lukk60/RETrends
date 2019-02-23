# -*- coding: utf-8 -*-
import sys, os, click, logging
from dotenv import find_dotenv, load_dotenv
import json, urllib
import feedly_api_utils as feedly
import datetime
import azure_storage_utils

@click.command()
@click.argument("config_filepath", type=click.Path(exists=True))
def main(config_filepath):
    """ download all articles from feedly, merge them with the already saved articles 
        and upload the new corpus to azure storage 
    """    
    ## create logger
    logger = logging.getLogger(__name__)

    ## load config
    with open(config_filepath, "r") as f:
        cfg = json.load(f)

    FEEDLY_USER_ID = os.environ.get("FEEDLY_USER_ID")
    FEEDLY_ACCESS_TOKEN = os.environ.get("FEEDLY_ACCESS_TOKEN")
    AZURE_STORAGE_NAME = os.environ.get("AZURE_STORAGE_NAME")
    AZURE_STORAGE_KEY = os.environ.get("AZURE_STORAGE_KEY")

    logger.info("************ Start ************")

    ## download articles
    headers = {'Authorization': 'OAuth ' + FEEDLY_ACCESS_TOKEN}
    feedlist = feedly.get_feedlist("Real Estate News", headers)
    feedData = feedly.download_feeds(
        feedlist, headers, count=int(cfg["feedly"]["maxDownloadsPerFeed"])
        )

    nDownloaded = [len(feedData[feed]["items"]) for feed in feedData]
    logger.info("%d Articles downloaded" % sum(nDownloaded))

    ## restructure data 
    feedDataSimple = feedly.restructure_data(feedData)

    ## save data
    # load stored data from blob store
    feedDataStored = azure_storage_utils.load_text_file(
        containerName = cfg["azureStorage"]["containerName"], 
        blobName = cfg["azureStorage"]["blobName"],
        accountName = AZURE_STORAGE_NAME,
        accountKey = AZURE_STORAGE_KEY
        )

    # merge downloaded data and data from blob store
    feedDataUpdated = {**feedDataStored, **feedDataSimple}

    # save back zu blob store
    azure_storage_utils.save_text_file(
        data = json.dumps(feedDataUpdated),
        containerName = cfg["azureStorage"]["containerName"], 
        blobName = cfg["azureStorage"]["blobName"],
        accountName = AZURE_STORAGE_NAME,
        accountKey = AZURE_STORAGE_KEY
        )

    
    logger.info("%d New articles added to datafile" % (len(feedDataUpdated)-len(feedDataStored)))

    logger.info("************ End ************")
    
if __name__ == "__main__": 
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables    
    load_dotenv(find_dotenv())

    main()
