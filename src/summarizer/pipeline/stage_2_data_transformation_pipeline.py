from src.summarizer.config.configuration import ConfigurationManager
from src.summarizer.components.data_transformation import DataTransformation
from src.summarizer.logging import logger

class DataTransformationTrainingPipeline:
    def __init__(self):
        pass

    def initiate_data_transformation(self):
        config = ConfigurationManager()
        transformation_config = config.get_data_transformation_config()
        data_transformation = DataTransformation(config=transformation_config)
        data_transformation.split_data()
