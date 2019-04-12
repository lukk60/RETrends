# -*- coding: utf-8 -*-
import sys, os, click, logging
from dotenv import find_dotenv, load_dotenv
import json
import datetime
import azure_storage_utils
import get_data_utils
import numpy as np
import re
import shutil

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
        queryList = f.read().splitlines()

    STORAGE_PATH = "data/raw/scraped_data/"
    # if no linklist exists create empty file
    LINKLIST_PATH = "data/raw/linklist.json"
    if not os.path.exists(LINKLIST_PATH):
        open(LINKLIST_PATH, "w").close()

    logger.info("************ Start ************")

    ## update Linklist   
    if update_linklist:
        # get links
        newLinks = get_data_utils.get_links(
            queryList, topN=cfg["googleSearch"]["SearchTopN"]
            )
        nLinksNew = np.sum([len(v) for v in newLinks.values()])        

        # merge new and existing links
        try:
            with open(LINKLIST_PATH, "r") as f:
                oldLinks = json.load(f)
        except:
            oldLinks = dict()
        allLinks = get_data_utils.merge_linklists(newLinks, oldLinks)

        nLinksTot = np.sum([len(v) for v in allLinks.values()])
        logger.info("Returned links: %d" % nLinksNew)
    
        # save updated linklist
        with open(LINKLIST_PATH, "w") as f:
            json.dump(allLinks, f, sort_keys=True, indent=4)
        
        logger.info("New total of links saved: %d" % nLinksTot)
    
    
    ## Crawl webpages in linklist
    with open(LINKLIST_PATH, "r") as f:
        linklist = json.load(f)
    
    # delete old files
    for f in os.listdir(STORAGE_PATH):
        shutil.rmtree(os.path.join(STORAGE_PATH, f))

    for k,v in linklist.items():
        
        # setup directories
        dirName = k.replace(" ", "_")
        storagePath =  STORAGE_PATH + dirName  
        if not os.path.exists(storagePath):
            os.mkdir(storagePath)

        # scrape pages in linklist
        for i,l in enumerate(v):

            # skip pdfs
            if len(re.findall(".pdf", l))==0:
                res = get_data_utils.get_webpage(l)
                get_data_utils.save_html(res, storagePath, str(i)+".html")
                logger.info("download complete: %s" %l)
            else: 
                logger.info("PDF File skipped: %s" %l)

    logger.info("HTML Files written to disk: %d" % i )
    
    logger.info("************ End ************")
    
if __name__ == "__main__": 
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables    
    load_dotenv(find_dotenv())

    main()
