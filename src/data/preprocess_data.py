# -*- coding: utf-8 -*-
import sys, os, click, logging
from dotenv import find_dotenv, load_dotenv
import preprocess_utils
import numpy as np




def main():
    """ load preprocess text 
    """
    ## create logger
    logger = logging.getLogger(__name__)

    ## load config
    with open(config_filepath, "r") as f:
        cfg = json.load(f)

    AZURE_STORAGE_NAME = os.environ.get("AZURE_STORAGE_NAME")
    AZURE_STORAGE_KEY = os.environ.get("AZURE_STORAGE_KEY")

    logger.info("************ Start ************")
    
    
    
    logger.info("************ End ************")

if __name__ == "__main__": 
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables    
    load_dotenv(find_dotenv())

    main()
