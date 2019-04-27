# -*- coding: utf-8 -*-
import sys, os, click, logging, datetime, json
from dotenv import find_dotenv, load_dotenv
from guillaumegenthial_LSTM_CRF.model.ner_model import NERModel
from guillaumegenthial_LSTM_CRF.model.config import Config
import ner_utils
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

    INPUT_DATA = "data/interim/scraped_data/scraped_data_wordlist.pkl"
    INPUT_METADATA = "data/interim/scraped_data/scraped_data_meta.pkl"
    OUTPUT_PATH = "data/processed/"

    # model config
    modelConfig = Config()
    
    ## start
    logger.info("************ Start ************")

    
    # load model and pretrained weights
    model = NERModel(modelConfig)
    model.build()
    model.restore_session(modelConfig.dir_model)

    # load datasets
    with open(INPUT_DATA, "rb") as f:
        data = pickle.load(f)

    with open(INPUT_METADATA, "rb") as f:
        metadata = pickle.load(f)

    # prediction
    
    for k,v in metadata.items():
        try:
            # keep only english documents
            if v["language"] == "english":
                for i,s in enumerate(data[v["processedFile"]]):
                    preds = zip(s, model.predict(s))
                    data[v["processedFile"]][i] = list(preds)
                logger.info("prediction completed for: %s" %k)
            else:
                data.pop(v["processedFile"])
                logger.info("non english language: %s" %k)
            
        except KeyError:
            logger.info("no data for: %s" %k)
            pass

    logger.info("Prediction complete")

    ## save predictions
    predictionFilePath = os.path.join(
        OUTPUT_PATH, "scraped_data_predictions.pkl"
        )
    with open(predictionFilePath, "wb") as f:
        pickle.dump(data, f)
    
    entityList = ner_utils.get_entity_list(data)

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
