# -*- coding: utf-8 -*-
import sys, os, click, logging, datetime, json
from dotenv import find_dotenv, load_dotenv
import preprocess_utils
import numpy as np
import pandas as pd


@click.command()
@click.argument("config_filepath", type=click.Path(exists=True))
def main(config_filepath):
    """ load training data, apply preprocessing pipeline and save results 
    """
    ## create logger
    logger = logging.getLogger(__name__)

    ## load config
    with open(config_filepath, "r") as f:
        cfg = json.load(f)

    
    ## start
    logger.info("************ Start ************")


    # load kaggle dataset
    kaggle_data = pd.read_csv(
        cfg["paths"]["kaggle_ner_dataset"], encoding = "latin1"
        )
    kaggle_data = kaggle_data.fillna(method="ffill")

    # split into train dev test
    trainTestSplit = cfg["ner_training"]["trainTestSplit"]
    kaggle_data = preprocess_utils.split_train_dev_test(kaggle_data, trainTestSplit)

    # convert to conll-format
    for k,v in kaggle_data.items():
        filename = k+".txt"
        output_path = os.path.join(cfg["paths"]["ner_trainingdata"], filename)
        preprocess_utils.kaggle_to_conll(
            data=v,
            output_path=output_path
            )
        logger.info("Tokens in %s: %d" % (k, len(v)))
    
    logger.info("************ End ************")
 
if __name__ == "__main__": 
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables    
    load_dotenv(find_dotenv())

    main()
