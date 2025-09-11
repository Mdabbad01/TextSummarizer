import os
import urllib.request as request
import zipfile
from src.summarizer.logging import logger
from src.summarizer.entity.dataingestionconfig import DataIngestionConfig

class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        self.config = config

    def download_file(self):
        if not os.path.exists(self.config.local_data_file):
            request.urlretrieve(
                url=self.config.source_URL,
                filename=self.config.local_data_file
            )
            logger.info(f"File downloaded at {self.config.local_data_file}")
        else:
            logger.info(f"File already exists at {self.config.local_data_file}")

    def extract_zip_file(self):
        os.makedirs(self.config.unzip_dir, exist_ok=True)
        with zipfile.ZipFile(self.config.local_data_file, 'r') as zip_ref:
            zip_ref.extractall(self.config.unzip_dir)
        logger.info(f"Extracted zip file to {self.config.unzip_dir}")
