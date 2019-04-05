# -*- coding: utf-8 -*-
import sys, os, click, logging, datetime, json
from dotenv import find_dotenv, load_dotenv
import preprocess_utils
import pickle

@click.command()
@click.argument("config_filepath", type=click.Path(exists=True))
def main(config_filepath):
    """ load raw text data, apply preprocessing pipeline and save results 
    """
    ## create logger
    logger = logging.getLogger(__name__)

    ## load config
    with open(config_filepath, "r") as f:
        cfg = json.load(f)

    ## start
    logger.info("************ Start ************")

    rawPath = cfg["paths"]["crawled_data_raw"]
    data = {}

    # process all files in rawPath
    for folder in os.listdir(rawPath): 
        for file in os.listdir(os.path.join(rawPath, folder)):
            with open(os.path.join(rawPath, folder, file), "rb") as f:
                html = f.read()
            data[f.name] = preprocess_utils.html_to_wordlist(html)
    
    # save processed data
    with open(cfg["paths"]["crawled_data_processed"], "wb") as f:
        pickle.dump(data, file=f)

    logger.info("Number of documents tokenized: %d" %len(data.keys()))
    logger.info("************ End ************")



if __name__ == "__main__": 
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables    
    load_dotenv(find_dotenv())

    main()
