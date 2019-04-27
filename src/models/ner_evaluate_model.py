# -*- coding: utf-8 -*-
import sys, os, click, logging, datetime, json
from dotenv import find_dotenv, load_dotenv
from guillaumegenthial_LSTM_CRF.model.ner_model import NERModel
from guillaumegenthial_LSTM_CRF.model.config import Config
import ner_utils
import pandas as pd
import numpy as np
from sklearn.metrics import f1_score, recall_score, precision_score, confusion_matrix
import datetime

@click.command()
@click.argument("config_filepath", type=click.Path(exists=True))
def main(config_filepath):
    """ load raw text data, apply preprocessing pipeline and save results 
    """
    ## create logger
    logger = logging.getLogger(__name__)

    ## load config
    # general
    with open(config_filepath, "r") as f:
        cfg = json.load(f)

    MODEL_NAME = "LSTM_CRF (copied from guillaume genthial)"
    INPUT_DATA = "data/interim/test_data/test_data_labelled.csv"
    OUTPUT_DATA = "data/processed/test_data_prediction.csv"

    # model config
    modelConfig = Config()
    
    ## start
    logger.info("************ Start ************")

    # load model and pretrained weights
    model = NERModel(modelConfig)
    model.build()
    model.restore_session(modelConfig.dir_model)

    # load test data 
    data = pd.DataFrame.from_csv(
        INPUT_DATA, sep=";", encoding="Windows-1252", index_col=None
        )
    data["prediction"] = np.nan
    data = data[["word","tag", "prediction"]]
    data["tag"] = data["tag"].str.strip()


    # loop through dataframe, concatenate words to sentences 
    # and add predictions

    sentence = []
    for i in data.index:
        if not pd.isnull(data["word"][i]):
            sentence.append(data["word"][i])
        else:
            preds = model.predict(sentence)
            data["prediction"][i-len(preds):i] = preds
            sentence = []

    # compute metrics
    data = data[np.logical_not( pd.isnull(data["word"]))]
    data["tag"] = data["tag"].astype(str).astype("category")
    data["prediction"] = data["prediction"].astype(str).astype("category")

    labels = list(data["tag"].cat.categories)

    metrics = dict({
        "date": datetime.datetime.now(),
        "modelname": MODEL_NAME,
        "metrics": {
            "f1": f1_score(
                data["tag"],
                data["prediction"],
                labels=labels, average="weighted"),
            "recall": recall_score(
                data["tag"], 
                data["prediction"], 
                labels=labels, average="weighted"),
            "precision": precision_score(
                data["tag"],
                data["prediction"],
                labels=labels, average="weighted"),
            "confusion_matrix": confusion_matrix(
                list(data["tag"]),
                list(data["prediction"]),
                labels=labels)
        }
    })

    logger.info("testset tokens: %s" %len(data))
    logger.info("f1 score: %s" %metrics["metrics"]["f1"])
    logger.info("precision: %s" %metrics["metrics"]["precision"])
    logger.info("recall: %s" %metrics["metrics"]["recall"])

    # save predictions
    data.to_csv(OUTPUT_DATA, sep=";")


if __name__ == "__main__": 
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables    
    load_dotenv(find_dotenv())

    main()