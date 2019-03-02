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
    logger.info("Raw documents retrieved: %d " % len(dRaw))

    # process structured data
    df = pd.DataFrame.from_dict(dRaw).transpose()
    df = df[["feedTitle", "author", "published", "engagement", "title"]]
    df["published"] = pd.to_datetime(df["published"], unit="ms")
    df["fileID"] = np.arange(len(df)) + 1

    # save structured data to pickle
    outputPath_structured = os.path.join(
        output_dir, "structured_data_"+ NOW.strftime("%Y%m%d") + ".pickle"
        )
    df.to_pickle(outputPath_structured)
    logger.info("Structured data saved: %d" % len(df))


    # extract text data and apply preprocessing pipeline
    outputPath_text = os.path.join(output_dir, "text_data")
    if not os.path.exists(outputPath_text):
        os.mkdir(outputPath_text)

    nFiles = 0

    for k,v in dRaw.items():
        try:
            title = v.get("title")
            summary = v.get("summary").get("content")
            text = title + "\n" + summary
            text_processed = preprocess_utils.preprocess_document(text)

            fileName = "feedly_"+str(df["fileID"][k])+".txt"
            fileName = os.path.join(outputPath_text, fileName)
            with open(os.path.normpath(fileName), "w") as f:
                f.write(text_processed)
            nFiles +=1

        except AttributeError:
            pass
        except TypeError:
            pass

    logger.info("Text documents written: %d" %nFiles)
    logger.info("************ End ************")

if __name__ == "__main__": 
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables    
    load_dotenv(find_dotenv())

    main()
