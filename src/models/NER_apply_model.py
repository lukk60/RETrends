# -*- coding: utf-8 -*-
import sys, os, click, logging, datetime, json
from dotenv import find_dotenv, load_dotenv
from guillaumegenthial_LSTM_CRF.model.ner_model import NERModel
from guillaumegenthial_LSTM_CRF.model.config import Config
import NER_utils
import pickle

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

    INPUT_FILE = "data/interim/scraped_data/scraped_data_wordlist.pkl"
    OUTPUT_PATH = "data/processed/"

    # model config
    modelConfig = Config()
    
    ## start
    logger.info("************ Start ************")

    
    # load model and pretrained weights
    model = NERModel(modelConfig)
    model.build()
    model.restore_session(modelConfig.dir_model)

    # load data
    with open(INPUT_FILE, "rb") as f:
        data = pickle.load(f)

    # prediction
    for k,v in data.items():
        for i,s in enumerate(v):
            preds = zip(s, model.predict(s))
            v[i] = list(preds)
        data[k] = v

    logger.info("Prediction complete")

    ## save predictions
    predictionFilePath = os.path.join(
        OUTPUT_PATH, "scraped_data_predictions.pkl"
        )
    with open(predictionFilePath, "wb") as f:
        pickle.dump(data, f)
    
    entityList = NER_utils.get_entity_list(data)

    entityFilePath = os.path.join(
        OUTPUT_PATH, "scraped_data_entitylist.pkl"
    )
    with open(entityFilePath, "wb") as f:
        pickle.dump(entityList, f)

    logger.info("************ End ************")



if __name__ == "__main__": 
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables    
    load_dotenv(find_dotenv())

    main()
