
from src.summarizer.logging import logger
from src.summarizer.pipeline.stage_1_data_ingestion_pipeline import DataIngestionTrainingPipeline
from src.summarizer.pipeline.stage_2_data_transformation_pipeline import DataTransformationTrainingPipeline
from src.summarizer.pipeline.stage_3_model_trainer_pipeline import ModelTrainerTrainingPipeline

if __name__ == "__main__":

    # -------------------- Stage 1: Data Ingestion --------------------
    STAGE_NAME = "Data Ingestion Stage"
    try:
        logger.info(f">>>>>> Stage: {STAGE_NAME} started <<<<<<")
        data_ingestion_pipeline = DataIngestionTrainingPipeline()
        data_ingestion_pipeline.initiate_data_ingestion()
        logger.info(f">>>>>> Stage: {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(f"Error in {STAGE_NAME}: {e}")
        raise e

    # -------------------- Stage 2: Data Transformation --------------------
    STAGE_NAME = "Data Transformation Stage"
    try:
        logger.info(f">>>>>> Stage: {STAGE_NAME} started <<<<<<")
        data_transformation_pipeline = DataTransformationTrainingPipeline()
        data_transformation_pipeline.initiate_data_transformation()
        logger.info(f">>>>>> Stage: {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(f"Error in {STAGE_NAME}: {e}")
        raise e

    # -------------------- Stage 3: Model Training --------------------
    STAGE_NAME = "Model Trainer Stage"
    try:
        logger.info(f">>>>>> Stage: {STAGE_NAME} started <<<<<<")
        model_trainer_pipeline = ModelTrainerTrainingPipeline()
        model_trainer_pipeline.initiate_model_trainer()
        logger.info(f">>>>>> Stage: {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(f"Error in {STAGE_NAME}: {e}")
        raise e
