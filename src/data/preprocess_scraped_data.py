# -*- coding: utf-8 -*-
import sys, os, click, logging, datetime, json
from dotenv import find_dotenv, load_dotenv
import preprocess_utils
import pickle
import shutil

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

    RAW_PATH = "data/raw/scraped_data/"
    INTERIM_PATH = "data/interim/scraped_data/"

    ## start
    logger.info("************ Start ************")

    # load metadata
    with open(os.path.join(RAW_PATH, "scraped_data_meta.pkl"), "rb") as f:
        metadata = pickle.load(f)

    # delete old files
    for f in os.listdir(INTERIM_PATH):
        if os.path.isdir(os.path.join(INTERIM_PATH, f)):
            shutil.rmtree(os.path.join(INTERIM_PATH, f))

    data = {}

    # process all files listed in metadata
    for k,v in metadata.items():
        try:
            # apply preprocessing
            with open(v["rawFile"], "rb") as f:
                html = f.read()
            text = preprocess_utils.text_from_html(html)
            
            # save processed document
            outputPath = os.path.join(INTERIM_PATH, v["query"].replace(" ", "_"))
            if not os.path.exists(outputPath):
                os.mkdir(outputPath)
            outputFilePath = os.path.join(outputPath, str(v["rank"])+".txt")
            with open(outputFilePath, "wb") as f:
                f.write(text.encode("utf-8"))
            
            logger.info("file processed: %s" %v["rawFile"])

            # convert to wordlist
            wordList = preprocess_utils.text_to_wordlist(
                text, cfg["preprocessing"]["minimumSentenceLength"]
                ) 
            data[f.name] = wordList
            # add new metadata
            metadata[k]["processedFile"] = outputFilePath
            metadata[k]["language"] = preprocess_utils.detect_language(text)
            metadata[k]["nSentences"] = len(wordList)
            metadata[k]["nTokens"] = sum([len(l) for l in wordList])
        
        except TypeError:
            pass

    # save metadata
    with open(os.path.join(INTERIM_PATH, "scraped_data_meta.pkl"), "wb") as f:
        pickle.dump(metadata, file=f)
    
    # save wordlist
    with open(os.path.join(INTERIM_PATH, "scraped_data_wordlist.pkl"), "wb") as f:
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
