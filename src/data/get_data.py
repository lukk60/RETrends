# -*- coding: utf-8 -*-
import sys, os, click, logging
from dotenv import find_dotenv, load_dotenv
import json
import datetime
import azure_storage_utils
import get_data_utils
import numpy as np

@click.command()
@click.argument("config_filepath", type=click.Path(exists=True))
@click.argument("query_filepath", type=click.Path(exists=True))
@click.option("--update_linklist", default=True, help="Should the linklist be updated or not")
def main(config_filepath, query_filepath, update_linklist):
    """ send pilot query to google search, 
        collect links in linklist,
        crawl webpages in linklist
        save crawled documents to azure blob storage
    """    
    ## create logger
    logger = logging.getLogger(__name__)

    ## load config and query list
    with open(config_filepath, "r") as f:
        cfg = json.load(f)

    with open(query_filepath, "r") as f:
        queryList = f.readlines()

    AZURE_STORAGE_NAME = os.environ.get("AZURE_STORAGE_NAME")
    AZURE_STORAGE_KEY = os.environ.get("AZURE_STORAGE_KEY")

    logger.info("************ Start ************")

    
    if update_linklist:
        # get links
        newLinks = get_data_utils.get_links(
            queryList, topN=cfg["googleSearch"]["topN"]
            )
        nLinksNew = np.sum([len(v) for v in newLinks.values()])        

        # merge new and existing links
        linklist_filepath = cfg["general"]["linklist_filepath"]
        if not os.path.exists(linklist_filepath):
            open(linklist_filepath, "w").close()

        try:
            with open(linklist_filepath, "r") as f:
                oldLinks = json.load(f)
        except:
            oldLinks = dict()
        allLinks = get_data_utils.merge_linklists(newLinks, oldLinks)

        nLinksTot = np.sum([len(v) for v in allLinks.values()])
        logger.info("Returned links: %d" % nLinksNew)
    
        # save updated linklist
        with open(linklist_filepath, "w") as f:
            json.dump(allLinks, f, sort_keys=True, indent=4)
        
        logger.info("New total of links saved: %d" % nLinksTot)
    
    '''
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
'''
    logger.info("************ End ************")
    
if __name__ == "__main__": 
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables    
    load_dotenv(find_dotenv())

    main()
