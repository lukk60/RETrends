''' Setup Azure Storage Environment '''
# -*- coding: utf-8 -*-
import os, sys, getopt
import json
import logging
from azure.storage.blob import BlockBlobService, PublicAccess
from dotenv import find_dotenv, load_dotenv


def main():
    """ Creates necessary containers to on azure storage 
        to store the feedly data 
    """
    logger = logging.getLogger(__name__)
    logger.info("start setup azure blob storage")

    # load env variables
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path)

    AZURE_STORAGE_NAME = os.environ.get("AZURE_STORAGE_NAME")
    AZURE_STORAGE_KEY = os.environ.get("AZURE_STORAGE_KEY")

    # Start Block Blob Service
    block_blob_service = BlockBlobService(
        account_name=AZURE_STORAGE_NAME, 
        account_key=AZURE_STORAGE_KEY
        ) 

    # Create Container
    container_name = "feedlydata"
    if block_blob_service.create_container(container_name):
        logger.info("new container created: %s" % container_name)

    # Set the permission so the blobs are public.
    block_blob_service.set_container_acl(
        container_name, public_access=PublicAccess.Container
        )


if __name__ == "__main__":    
    
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    
    main()