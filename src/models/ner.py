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
def main(config_filepath, query_filepath, update_linklist):
    """ Perform Named Entity Recognition on crawled data
    """    
    ## create logger
    logger = logging.getLogger(__name__)

    ## load config and query list
    with open(config_filepath, "r") as f:
        cfg = json.load(f)

    logger.info("************ Start ************")
    
    logger.info("************ End ************")

    
if __name__ == "__main__": 
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables    
    load_dotenv(find_dotenv())

    main()