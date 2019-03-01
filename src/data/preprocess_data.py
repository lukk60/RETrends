# -*- coding: utf-8 -*-
import sys, os, click, logging, datetime, json
from dotenv import find_dotenv, load_dotenv
import preprocess_utils
import numpy as np
import pandas as pd
from azure_storage_utils import load_text_file

@click.command()
@click.argument("config_filepath", type=click.Path(exists=True))
@click.argument("output_dir", type=click.Path(writable=True))
def main(config_filepath, output_dir):
    """ load raw text data, apply preprocessing pipeline and save results 
    """
    ## create logger
    logger = logging.getLogger(__name__)

    ## load config
    with open(config_filepath, "r") as f:
        cfg = json.load(f)

    AZURE_STORAGE_NAME = os.environ.get("AZURE_STORAGE_NAME")
    AZURE_STORAGE_KEY = os.environ.get("AZURE_STORAGE_KEY")
    NOW = datetime.datetime.now()
    ## start
    logger.info("************ Start ************")
    
    # load raw data
    dRaw = load_text_file(
        containerName = cfg["azureStorage"]["containerName"], 
        blobName = cfg["azureStorage"]["blobName"],
        accountName = AZURE_STORAGE_NAME,
        accountKey = AZURE_STORAGE_KEY
        )
    logger.info("Raw Documents retrieved: %d " % len(dRaw))
    # convert to dataframe
    df = pd.DataFrame.from_dict(dRaw).transpose()
    df = df[[
        "feedTitle", "author", "published", "engagement", "title", "summary"
        ]]

    for i in df.index:
        try:
            df["summary"][i] = df["summary"][i]["content"]
        except TypeError:
            df["summary"][i] = None

    # convert timestamps
    df["published"] = pd.to_datetime(df["published"], unit="ms")

    # apply text preprocessing pipeline
    preprocessor = np.vectorize(preprocess_utils.preprocess_document)

    df["summary_processed"] = preprocessor(df["summary"])
    df["title_processed"]   = preprocessor(df["title"])

    # save preprocessed data
    output_filepath = os.path.join(
        output_dir, "preprocessed_"+ NOW.strftime("%Y%m%d")
        )
    df.to_pickle(output_filepath)

    logger.info("Processed Documents: %d" % len(df))
    logger.info("************ End ************")

if __name__ == "__main__": 
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables    
    load_dotenv(find_dotenv())

    main()
