# -*- coding: utf-8 -*-
import sys, os, click, logging, datetime, json
from dotenv import find_dotenv, load_dotenv
import pickle
import os
import preprocess_utils

@click.command()
@click.argument("text_path", type=click.Path(exists=True))
def main(text_path):
    """ prepare a testset to be manually labelled from a given collection of 
    text files 
    """
    ## create logger
    logger = logging.getLogger(__name__)

    OUTPUT_PATH = "data/interim/test_data_preparation/"
    # if output path does not exist, create it
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    logger.info("************ Start ************")

    # preprocessing
    wordList = list()
    for doc in os.listdir(text_path):
        with open(os.path.join(text_path, doc), "rb") as f:
            text = f.read().decode("utf-8")
        
        wordList.append(
            preprocess_utils.text_to_wordlist(text, 5) 
        )

    # convert to output-format:
    # s1w1 tag
    # s1w2 tag
    # 
    # s2w1 tag
    # s2w2 tag
    flatList = list()
    for i,doc in enumerate(wordList):
        flatList.append(("--------- %s ---------\n" %i).encode("utf-8"))
        for s in doc:
            for w in s:
                flatList.append((w+";O\n").encode("utf-8"))
            flatList.append("\n".encode("utf-8"))
        
    
    outputFile = os.path.join(OUTPUT_PATH, "test_data_unlabelled.csv")
    with open(outputFile, "wb") as f:
        f.writelines(flatList)
    logger.info("output written to: %s" %outputFile)        
    logger.info("************ End ************")
if __name__ == "__main__": 
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables    
    load_dotenv(find_dotenv())

    main()