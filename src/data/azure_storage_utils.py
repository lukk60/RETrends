# Utility functions to access azure data storage

import json, os
from azure.storage.blob import BlockBlobService, PublicAccess

def load_text_file(containerName, blobName, accountName, accountKey):
    '''
    load the file specified from azure block blob storage. if the file is not 
    found return an empty dictionary
        Parameters
        ----------
        containerName: str
            container in storage account to open

        blobName: str
            name of blob in container to open
        
        accountName: str
            name of storage account

        accountKey
            access key for storage account

        Returns
        -------
        dictionary
    '''
    # Create BlockBlockService
    block_blob_service = BlockBlobService(
        account_name=accountName, account_key=accountKey
        ) 

    # try loading data from blob store. if blob is not found return empty dict
    try:
        res = block_blob_service.get_blob_to_text(containerName, blobName)
        blobData = json.loads(res.content)
    except: 
        blobData = {}

    return blobData


def save_text_file(data, containerName, blobName, accountName, accountKey):
    '''
    save a textfile to azure block blob storage.
        Parameters
        ----------
        data: str
            (text)data to upload
        
        containerName: str
            container in storage account

        blobName: str
            name of blob in container

        accountName: str
            name of storage account

        accountKey
            access key for storage account
    
        Returns
        -------
    '''    
    # Create BlockBlockService
    block_blob_service = BlockBlobService(
        account_name=accountName, account_key=accountKey
        ) 

    block_blob_service.create_blob_from_text(containerName, blobName, data)    
