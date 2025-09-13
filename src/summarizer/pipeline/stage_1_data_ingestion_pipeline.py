from src.summarizer.config.configuration import ConfigurationManager
from src.summarizer.components.data_ingestion import DataIngestion
from src.summarizer.logging import logger 


class DataIngestionTrainingPipeline:
    def __init__(self):
        pass  # Optionally, you could initialize config here

    def initiate_data_ingestion(self):
        logger.info("Starting Data Ingestion...")

        # Instantiate config manager
        config = ConfigurationManager()

        # Get data ingestion configuration
        data_ingestion_config = config.get_data_ingestion_config()

        # Initialize data ingestion component
        data_ingestion = DataIngestion(config=data_ingestion_config)

        # Download and extract data
        data_ingestion.download_file()
        data_ingestion.extract_zip_file()

        logger.info("Data Ingestion completed successfully.")
