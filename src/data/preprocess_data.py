# -*- coding: utf-8 -*-
import sys, os, click, logging, datetime, json
from dotenv import find_dotenv, load_dotenv
import preprocess_utils
import numpy as np
import pandas as pd
from azure_storage_utils import load_text_file

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


    # prepare kaggle dataset

    trainTestSplit = cfg["ner_training"]["trainTestSplit"]

    output_path = os.path.join(cfg["paths"]["ner_trainingdata"], "train.txt")
    kaggle_data = pd.read_csv(
        cfg["paths"]["kaggle_ner_dataset"], encoding = "latin1"
        )
    kaggle_data = kaggle_data.fillna(method="ffill")
    kaggle_data_prep = preprocess_utils.dataframe_to_conll(
        data=kaggle_data,
        output_path=
        )
    with open("data/interim/kaggle_data.train.txt", "w") as f:
        f.write(kaggle_data_prep)

    logger.info("Tokens written: %d (output path: %s)", %len(kaggle_data) %output_path)
    logger.info("************ End ************")

if __name__ == "__main__": 
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables    
    load_dotenv(find_dotenv())

    main()
